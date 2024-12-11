from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QListWidget, QPushButton, QLabel, QGroupBox
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QImageReader, QImage, QFont, QPainter, QPen, QCursor
import numpy as np
from typing import Tuple
import math
from skimage.draw import polygon  # 添加到文件开头的导入语句中


class ClickableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.parent_view = None

    def mousePressEvent(self, event):
        if self.parent_view:
            # 转换鼠标坐标到图片坐标系
            mapped_pos = self.parent_view.map_to_image_coordinates(event.pos())
            if mapped_pos:
                event.mapped_pos = mapped_pos
                self.parent_view.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.parent_view:
            # 转换鼠标坐标到图片坐标系
            mapped_pos = self.parent_view.map_to_image_coordinates(event.pos())
            if mapped_pos:
                event.mapped_pos = mapped_pos
                self.parent_view.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.parent_view:
            # 转换鼠标坐标到图片坐标系
            mapped_pos = self.parent_view.map_to_image_coordinates(event.pos())
            if mapped_pos:
                event.mapped_pos = mapped_pos
                self.parent_view.mouseReleaseEvent(event)


class ShowView():
    def __init__(self) -> None:
        # Component
        self.is_drawing = False
        self.start_point = None
        self.end_point = None
        self.current_pixmap = None
        self.temp_pixmap = None
        self.image_rect = None  # 存储实际显示的图片区域

        self.origin_image = ClickableLabel(
            "Please add images and select an image :)")
        self.origin_image.parent_view = self

        font = QFont()
        font.setPointSize(20)
        self.origin_image.setFont(font)
        self.origin_image.setAlignment(Qt.AlignCenter)
        self.origin_image.setGeometry(100, 100, 640, 480)
        self.origin_image.setFixedSize(640, 480)

        self.quality_image = QLabel()
        self.quality_image.setAlignment(Qt.AlignCenter)

        self.angle_image = QLabel()
        self.angle_image.setAlignment(Qt.AlignCenter)

        self.width_image = QLabel()
        self.width_image.setAlignment(Qt.AlignCenter)

        # 添加标签
        self.quality_label = QLabel("Quality")
        self.quality_label.setAlignment(Qt.AlignCenter)
        self.angle_label = QLabel("Angle")
        self.angle_label.setAlignment(Qt.AlignCenter)
        self.width_label = QLabel("Width")
        self.width_label.setAlignment(Qt.AlignCenter)

        # 创建颜色比例尺标签
        self.colorbar_label = QLabel()
        self.width_colorbar_label = QLabel()  # 添加width的比例尺
        self.colorbar_label.setFixedWidth(20)
        self.width_colorbar_label.setFixedWidth(20)
        self.colorbar_label.setAlignment(Qt.AlignCenter)
        self.width_colorbar_label.setAlignment(Qt.AlignCenter)

        # Layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Origin Image
        self.origin_groupbox = QGroupBox("Origin Image")
        self.origin_groupbox.setAlignment(Qt.AlignCenter)
        self.origin_layout = QHBoxLayout()
        self.origin_layout.addWidget(self.origin_image)
        self.origin_groupbox.setLayout(self.origin_layout)

        # Preview
        self.preview_groupbox = QGroupBox("Preview Image")
        self.preview_groupbox.setAlignment(Qt.AlignCenter)
        self.preview_layout = QVBoxLayout()  # 垂直布局

        # 创建水平布局来放预览图
        self.preview_images_layout = QHBoxLayout()
        self.preview_images_layout.setAlignment(Qt.AlignCenter)

        # 为每个预览图建垂直布局
        quality_container = QVBoxLayout()    # 垂直布局放图片和标签
        quality_preview = QHBoxLayout()      # 水平布局放比例尺和图片
        quality_preview.addWidget(self.colorbar_label)  # 先添加比例尺
        quality_preview.addWidget(self.quality_image)   # 再添加图片
        quality_preview.setAlignment(
            self.colorbar_label, Qt.AlignVCenter)  # 垂直居中对齐
        quality_container.addLayout(quality_preview)    # 添加水平布局
        quality_container.addWidget(self.quality_label)  # 添加标签

        angle_container = QVBoxLayout()
        angle_container.addWidget(self.angle_image)
        angle_container.addWidget(self.angle_label)

        width_container = QVBoxLayout()
        width_preview = QHBoxLayout()
        width_preview.addWidget(self.width_colorbar_label)
        width_preview.addWidget(self.width_image)
        width_preview.setAlignment(self.width_colorbar_label, Qt.AlignVCenter)
        width_container.addLayout(width_preview)
        width_container.addWidget(self.width_label)

        # 各个容器添加到预览图布局中
        preview_widget1 = QWidget()
        preview_widget1.setLayout(quality_container)
        preview_widget2 = QWidget()
        preview_widget2.setLayout(angle_container)
        preview_widget3 = QWidget()
        preview_widget3.setLayout(width_container)

        self.preview_images_layout.addWidget(preview_widget1)
        self.preview_images_layout.addWidget(preview_widget2)
        self.preview_images_layout.addWidget(preview_widget3)

        # 将预览图布局添加到预览组布局中
        self.preview_layout.addLayout(self.preview_images_layout)
        self.preview_groupbox.setLayout(self.preview_layout)

        self.layout.addWidget(self.origin_groupbox, 3)
        self.layout.addWidget(self.preview_groupbox, 2)

        # 添加一个回调函数属性
        self.on_drawing_finished = None

        # 添加新的属性来存储抓取线的信息
        self.grasp_lines = []  # 存储所有的抓取线信息
        self.current_grasp_line = None  # 当前选中的抓取线

        # 添加相关的属性
        self.quality_map = None
        self.angle_map = None
        self.width_map = None

        self.click_tolerance = 5  # 中心轴可点击范围的半宽度（总宽度为10px）

        # 添加微调相关的属性
        self.fine_tune_mode = None  # 'up', 'down', 或 'select'
        self.fine_tune_radius = 10  # 修改为10（原来是20）
        self.fine_tune_strength = 0.1  # 每次微调的强度

        # 修改鼠标跟踪
        self.origin_image.setMouseTracking(True)
        self.origin_image.setCursor(Qt.ArrowCursor)

    def map_to_image_coordinates(self, pos):
        """将窗口坐标映射到图片坐标"""
        if not self.image_rect or not self.current_pixmap:
            return None

        # 计算相对于图片显示区域的坐标
        x = pos.x() - self.image_rect.x()
        y = pos.y() - self.image_rect.y()

        # 检查是否在图片区域内
        if x < 0 or y < 0 or x > self.image_rect.width() or y > self.image_rect.height():
            return None

        return QPoint(x, y)

    def update_image_rect(self):
        """更新图片显示区域的信息"""
        if not self.current_pixmap:
            return

        # 计算保持纵横比的缩放后图片大小
        label_size = self.origin_image.size()
        scaled_size = self.current_pixmap.size().scaled(
            label_size, Qt.KeepAspectRatio)

        # 计算图片在Label中的实际显示区域
        x = (label_size.width() - scaled_size.width()) // 2
        y = (label_size.height() - scaled_size.height()) // 2

        self.image_rect = QRect(
            x, y, scaled_size.width(), scaled_size.height())

    def distance_to_line(self, point, line_start, line_end):
        """计算点到线段的距离"""
        px = point[0]
        py = point[1]
        x1 = line_start[0]
        y1 = line_start[1]
        x2 = line_end[0]
        y2 = line_end[1]

        # 计算线段长度的平方
        l2 = (x2 - x1) ** 2 + (y2 - y1) ** 2

        if l2 == 0:
            # 如果线段长度为0，直接返回到端点的距离
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # 计算点到线段的投影位置参数 t
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))

        # 计算投影点坐标
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        # 返回点到投影点的距离
        return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

    def find_nearest_line(self, point):
        """找到离点击位置最近的抓取线"""
        if not self.grasp_lines:
            return None

        min_distance = float('inf')
        nearest_line = None

        for line in self.grasp_lines:
            distance = self.distance_to_line(
                point,
                line['start'],
                line['end']
            )
            if distance < min_distance and distance <= self.click_tolerance:
                min_distance = distance
                nearest_line = line

        return nearest_line

    def mousePressEvent(self, event):
        if self.fine_tune_mode in ['up', 'down'] and event.button() == Qt.LeftButton:
            # 获取点击位置
            pos = event.mapped_pos
            # 转换为预览图坐标
            preview_x = int(pos.x() / 2)
            preview_y = int(pos.y() / 2)

            # 更新quality map
            if self.quality_map is not None:
                height, width = self.quality_map.shape
                radius = self.fine_tune_radius // 2  # 预览图上的半径（现在是5像素）

                # 在圆形区域内更新值
                for y in range(max(0, preview_y - radius), min(height, preview_y + radius)):
                    for x in range(max(0, preview_x - radius), min(width, preview_x + radius)):
                        # 计算到中心的距离
                        dist = math.sqrt((x - preview_x) **
                                         2 + (y - preview_y)**2)
                        if dist <= radius:
                            # 使用高斯衰减
                            factor = math.exp(-(dist**2)/(2*(radius/2)**2))
                            if self.fine_tune_mode == 'up':
                                self.quality_map[y, x] = min(
                                    1.0, self.quality_map[y, x] + self.fine_tune_strength * factor)
                            else:  # down
                                self.quality_map[y, x] = max(
                                    0.0, self.quality_map[y, x] - self.fine_tune_strength * factor)

                # 更新预览图显示
                self.update_preview_images()
        elif self.is_drawing and event.button() == Qt.LeftButton:
            # 处理绘制模式下的点击
            self.start_point = event.mapped_pos
            if self.current_pixmap:
                self.temp_pixmap = self.current_pixmap.copy()
        elif not self.is_drawing and event.button() == Qt.LeftButton:
            # 非绘制模式下，检查是否点击了某条中心轴
            clicked_point = (event.mapped_pos.x(), event.mapped_pos.y())
            nearest_line = self.find_nearest_line(clicked_point)

            if nearest_line:
                # 更新当前选中的抓取线
                self.current_grasp_line = nearest_line

                # 重绘所有线段，突出显示选中的线
                if self.current_pixmap:
                    self.current_pixmap = self.temp_pixmap.copy()
                    painter = QPainter(self.current_pixmap)

                    # 先绘制所有未选中的线
                    for line in self.grasp_lines:
                        if line != self.current_grasp_line:
                            # 绘制红色的中心轴
                            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                            painter.drawLine(
                                int(line['start'][0]), int(line['start'][1]),
                                int(line['end'][0]), int(line['end'][1])
                            )

                            # 如果有垂直线，绘制蓝色的垂直线
                            if line['perp_line']:
                                painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                                painter.drawLine(
                                    int(line['perp_line']['start'][0]),
                                    int(line['perp_line']['start'][1]),
                                    int(line['perp_line']['end'][0]),
                                    int(line['perp_line']['end'][1])
                                )

                    # 最后绘选中的线（使用更粗的线条）
                    painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                    painter.drawLine(
                        int(self.current_grasp_line['start'][0]),
                        int(self.current_grasp_line['start'][1]),
                        int(self.current_grasp_line['end'][0]),
                        int(self.current_grasp_line['end'][1])
                    )

                    # 如果选中的线有垂直线，也用更粗的线条绘制
                    if self.current_grasp_line['perp_line']:
                        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
                        painter.drawLine(
                            int(self.current_grasp_line['perp_line']
                                ['start'][0]),
                            int(self.current_grasp_line['perp_line']
                                ['start'][1]),
                            int(self.current_grasp_line['perp_line']
                                ['end'][0]),
                            int(self.current_grasp_line['perp_line']['end'][1])
                        )

                    painter.end()
                    self.origin_image.setPixmap(
                        self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

    def mouseMoveEvent(self, event):
        if self.is_drawing and self.start_point:
            if self.temp_pixmap:
                drawing_pixmap = self.temp_pixmap.copy()
                painter = QPainter(drawing_pixmap)
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawLine(self.start_point, event.mapped_pos)
                painter.end()
                self.origin_image.setPixmap(
                    drawing_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

    def mouseReleaseEvent(self, event):
        if self.is_drawing and event.button() == Qt.LeftButton and self.start_point:
            self.end_point = event.mapped_pos
            if self.current_pixmap:
                # 创建新的抓取线信息
                grasp_line = {
                    'start': (self.start_point.x(), self.start_point.y()),
                    'end': (self.end_point.x(), self.end_point.y()),
                    'perp_line': None,  # 存储垂直线信息
                    'length': None,     # 存储线段长度
                    'center': None,     # 存储中心点
                    'angle': None       # 存储角度
                }

                # 计算并存储抓取线的信息
                dx = self.end_point.x() - self.start_point.x()
                dy = self.end_point.y() - self.start_point.y()
                grasp_line['length'] = math.sqrt(dx*dx + dy*dy)
                grasp_line['center'] = (
                    (self.start_point.x() + self.end_point.x()) / 2,
                    (self.start_point.y() + self.end_point.y()) / 2
                )
                grasp_line['angle'] = math.atan2(dy, dx)

                # 添加到列表中
                self.grasp_lines.append(grasp_line)

                # 设置为当前选中的线
                self.current_grasp_line = grasp_line

                # 新绘制所有线段
                self.current_pixmap = self.temp_pixmap.copy()
                painter = QPainter(self.current_pixmap)

                # 先绘制所有未选中的线
                for line in self.grasp_lines:
                    if line != self.current_grasp_line:
                        # 绘制红色的中心轴
                        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                        painter.drawLine(
                            int(line['start'][0]), int(line['start'][1]),
                            int(line['end'][0]), int(line['end'][1])
                        )

                        # 如果有垂直线，绘制蓝色的垂直线
                        if line['perp_line']:
                            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                            painter.drawLine(
                                int(line['perp_line']['start'][0]),
                                int(line['perp_line']['start'][1]),
                                int(line['perp_line']['end'][0]),
                                int(line['perp_line']['end'][1])
                            )

                # 绘制选中的线（使用更粗的线条）
                painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                painter.drawLine(
                    int(self.current_grasp_line['start'][0]),
                    int(self.current_grasp_line['start'][1]),
                    int(self.current_grasp_line['end'][0]),
                    int(self.current_grasp_line['end'][1])
                )

                painter.end()
                self.origin_image.setPixmap(
                    self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

                # 保存当前图片状态
                self.temp_pixmap = self.current_pixmap.copy()

                print(f"Added new grasp line from {
                      grasp_line['start']} to {grasp_line['end']}")

            self.start_point = None
            self.end_point = None
            self.is_drawing = False

            if self.on_drawing_finished:
                self.on_drawing_finished()

    def draw_perpendicular_line(self, length_ratio=0.25):
        """在当前选中的抓取线中心绘制垂直线"""
        if not self.current_grasp_line:
            return False

        # 计算垂直线的长度
        perp_length = self.current_grasp_line['length'] * length_ratio

        # 计算垂直线的角度
        perp_angle = self.current_grasp_line['angle'] + math.pi/2

        # 计算垂直线的端点
        center = self.current_grasp_line['center']
        half_length = perp_length / 2
        start_x = center[0] - half_length * math.cos(perp_angle)
        start_y = center[1] - half_length * math.sin(perp_angle)
        end_x = center[0] + half_length * math.cos(perp_angle)
        end_y = center[1] + half_length * math.sin(perp_angle)

        # 存储垂直线信息
        self.current_grasp_line['perp_line'] = {
            'start': (start_x, start_y),
            'end': (end_x, end_y),
            'length_ratio': length_ratio
        }

        # 重绘所有线段
        if self.current_pixmap:
            self.current_pixmap = self.temp_pixmap.copy()
            painter = QPainter(self.current_pixmap)

            # 绘制所有抓取线
            for line in self.grasp_lines:
                # 先画红色的中心轴
                if line == self.current_grasp_line:
                    # 当前选中的线画粗一点
                    painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                else:
                    painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

                painter.drawLine(
                    int(line['start'][0]), int(line['start'][1]),
                    int(line['end'][0]), int(line['end'][1])
                )

                # 如果有垂直线，绘制蓝色的垂直线
                if line['perp_line']:
                    # 计算垂直线的端点
                    center = line['center']
                    perp_length = line['length'] * \
                        line['perp_line']['length_ratio']
                    half_length = perp_length / 2
                    perp_angle = line['angle'] + math.pi/2

                    start_x = center[0] - half_length * math.cos(perp_angle)
                    start_y = center[1] - half_length * math.sin(perp_angle)
                    end_x = center[0] + half_length * math.cos(perp_angle)
                    end_y = center[1] + half_length * math.sin(perp_angle)

                    if line == self.current_grasp_line:
                        # 当前选中的线的垂直线画粗一点
                        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
                    else:
                        painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))

                    painter.drawLine(
                        int(start_x), int(start_y),
                        int(end_x), int(end_y)
                    )

            painter.end()
            self.origin_image.setPixmap(
                self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))
            return True
        return False

    def update_perpendicular_line(self, length_ratio):
        """更新当前选中抓取线的垂直线长度"""
        if not self.current_grasp_line:
            return False

        # 更新当前选中线的垂直线长度比例
        if self.current_grasp_line['perp_line']:
            self.current_grasp_line['perp_line']['length_ratio'] = length_ratio

        # 重新绘制所有线段
        if self.current_pixmap:
            self.current_pixmap = self.temp_pixmap.copy()
            painter = QPainter(self.current_pixmap)

            # 绘制所有抓取线
            for line in self.grasp_lines:
                # 先画红色的中心轴
                if line == self.current_grasp_line:
                    # 当前选中的线画粗一点
                    painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                else:
                    painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

                painter.drawLine(
                    int(line['start'][0]), int(line['start'][1]),
                    int(line['end'][0]), int(line['end'][1])
                )

                # 如果有垂直线，绘制蓝色的垂直线
                if line['perp_line']:
                    # 计算垂直线的端点
                    center = line['center']
                    perp_length = line['length'] * \
                        line['perp_line']['length_ratio']
                    half_length = perp_length / 2
                    perp_angle = line['angle'] + math.pi/2

                    start_x = center[0] - half_length * math.cos(perp_angle)
                    start_y = center[1] - half_length * math.sin(perp_angle)
                    end_x = center[0] + half_length * math.cos(perp_angle)
                    end_y = center[1] + half_length * math.sin(perp_angle)

                    if line == self.current_grasp_line:
                        # 当前选中的线的垂直线画粗一点
                        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
                    else:
                        painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))

                    painter.drawLine(
                        int(start_x), int(start_y),
                        int(end_x), int(end_y)
                    )

            painter.end()
            self.origin_image.setPixmap(
                self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))
            return True
        return False

    @staticmethod
    def init_label_image(width, height) -> Tuple[np.ndarray, QImage]:
        # 确保宽度和高度是整数
        width = int(width)
        height = int(height)
        # 使用灰色（128）而不是黑色（0）
        image = np.full((height, width), 200, dtype=np.uint8)  # 使用浅灰色
        qimage = QImage(image.data,
                        width, height,
                        width,  # 添加步长参数
                        QImage.Format_Grayscale8)
        return image, qimage

    def generate_heatmaps(self):
        """生成热力图，考虑所有已标注的抓取线"""
        if not self.image_rect or not self.grasp_lines:
            return False

        # 获取图像尺寸
        height = self.image_rect.height() // 2
        width = self.image_rect.width() // 2

        # 创建热力图
        self.quality_map = np.zeros((height, width), dtype=np.float32)
        self.angle_map = np.zeros((height, width), dtype=np.float32)  # 全部置0
        self.width_map = np.zeros((height, width), dtype=np.float32)  # 全部置0

        # 在原图上绘制中心轴上的蓝线
        if self.current_pixmap:
            painter = QPainter(self.current_pixmap)
            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))

            # 遍历所有抓取线
            for grasp_line in self.grasp_lines:
                if not grasp_line['perp_line']:  # 跳过没有标注宽度的线
                    continue

                # 计算在中心轴上均匀分布的点
                num_points = int(grasp_line['length'])  # 每个像素一个点

                dx = (grasp_line['end'][0] -
                      grasp_line['start'][0]) / (num_points - 1)
                dy = (grasp_line['end'][1] -
                      grasp_line['start'][1]) / (num_points - 1)

                prev_start_x_scaled, prev_start_y_scaled = None, None
                prev_end_x_scaled, prev_end_y_scaled = None, None

                # 在每个点上绘制垂直的蓝线并更新热力图
                for i in range(num_points):
                    # 原坐标
                    center_x = grasp_line['start'][0] + dx * i
                    center_y = grasp_line['start'][1] + dy * i

                    # 计算垂直线的端点（原图坐标）
                    perp_length = grasp_line['length'] * \
                        grasp_line['perp_line']['length_ratio']
                    half_length = perp_length / 2
                    perp_angle = grasp_line['angle'] + math.pi/2

                    start_x = center_x - half_length * math.cos(perp_angle)
                    start_y = center_y - half_length * math.sin(perp_angle)
                    end_x = center_x + half_length * math.cos(perp_angle)
                    end_y = center_y + half_length * math.sin(perp_angle)

                    # 绘制垂直线（原图）
                    painter.drawLine(
                        int(start_x), int(start_y),
                        int(end_x), int(end_y)
                    )

                    # 计算预览图坐标
                    start_x_scaled = int(start_x / 2)
                    start_y_scaled = int(start_y / 2)
                    end_x_scaled = int(end_x / 2)
                    end_y_scaled = int(end_y / 2)

                    # 在两个垂直线之间填充区域
                    if i > 0:  # 从第二个点开始，连接前后两个垂直线
                        # 创建多边形的顶点数组
                        poly_y = np.array([
                            prev_start_y_scaled,
                            prev_end_y_scaled,
                            end_y_scaled,
                            start_y_scaled
                        ])
                        poly_x = np.array([
                            prev_start_x_scaled,
                            prev_end_x_scaled,
                            end_x_scaled,
                            start_x_scaled
                        ])

                        # 使用polygon函数获取多边形内的所有点
                        rr, cc = polygon(
                            poly_y, poly_x, shape=self.quality_map.shape)

                        # 一次性更新所有点的值
                        self.quality_map[rr, cc] = 1.0
                        self.width_map[rr,
                                       cc] = grasp_line['perp_line']['length_ratio']

                    # 更新前一个点的坐标
                    prev_start_x_scaled, prev_start_y_scaled = start_x_scaled, start_y_scaled
                    prev_end_x_scaled, prev_end_y_scaled = end_x_scaled, end_y_scaled

            painter.end()
            self.origin_image.setPixmap(
                self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

            # 更新预览图显示
            self.update_preview_images()
            return True

    def update_preview_images(self):
        """更新预览图的显示"""
        if all([self.quality_map is not None,
                self.angle_map is not None,
               self.width_map is not None]):

            # 转换为uint8类型并应用颜色映射
            quality_colored = self.apply_colormap(self.quality_map)
            angle_colored = self.apply_colormap(self.angle_map)
            width_colored = self.apply_colormap(self.width_map)

            # 创建QImage并显示
            h, w = self.quality_map.shape

            quality_qimage = QImage(
                quality_colored.data, w, h, w * 3, QImage.Format_RGB888)
            self.quality_image.setPixmap(QPixmap.fromImage(quality_qimage))

            angle_qimage = QImage(angle_colored.data, w,
                                  h, w * 3, QImage.Format_RGB888)
            self.angle_image.setPixmap(QPixmap.fromImage(angle_qimage))

            width_qimage = QImage(width_colored.data, w,
                                  h, w * 3, QImage.Format_RGB888)
            self.width_image.setPixmap(QPixmap.fromImage(width_qimage))

            # 创建并更新颜色比例尺
            self.update_colorbar(h)
            self.update_width_colorbar(h)

    def apply_colormap(self, data):
        """应用热力图颜色映射"""
        # 确保数据在0-1范围内
        data = np.clip(data, 0, 1)

        # 转换为uint8类型
        data_uint8 = (data * 255).astype(np.uint8)

        # 创建彩色图像
        colored = np.zeros((data.shape[0], data.shape[1], 3), dtype=np.uint8)

        # 应用颜色映射（这里使用简单的红色到蓝色渐变）
        colored[..., 0] = data_uint8  # 红色通道
        colored[..., 2] = 255 - data_uint8  # 蓝色通道

        return colored

    def set_fine_tune_mode(self, mode):
        """设置微调模式"""
        self.fine_tune_mode = mode
        if mode in ['up', 'down']:
            # 创建圆形光标
            cursor = self.create_circle_cursor()
            self.origin_image.setCursor(cursor)
        else:
            self.origin_image.setCursor(Qt.ArrowCursor)

    def create_circle_cursor(self):
        """创建圆形光标"""
        cursor_size = self.fine_tune_radius * 2
        pixmap = QPixmap(cursor_size, cursor_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.drawEllipse(0, 0, cursor_size-1, cursor_size-1)
        painter.end()

        return QCursor(pixmap)

    def update_colorbar(self, height):
        """更新颜色比例尺"""
        # 创建一个垂直的颜色渐变条
        colorbar = np.zeros((height, 20, 3), dtype=np.uint8)
        for i in range(height):
            value = 1.0 - (i / height)  # 从上到下，值从1降到0
            colorbar[i, :, 0] = int(value * 255)  # 红色通道
            colorbar[i, :, 2] = int((1 - value) * 255)  # 蓝色通道

        # 添加最大值和最小值标签
        font = QPainter()
        colorbar_pixmap = QPixmap(20, height)
        colorbar_qimage = QImage(
            colorbar.data, 20, height, 60, QImage.Format_RGB888)
        colorbar_pixmap.convertFromImage(colorbar_qimage)

        painter = QPainter(colorbar_pixmap)
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 8))

        # 在顶部绘制"1.0"
        painter.drawText(0, 10, "1.0")
        # 在底部绘制"0.0"
        painter.drawText(0, height-2, "0.0")

        painter.end()

        self.colorbar_label.setPixmap(colorbar_pixmap)

    def update_width_colorbar(self, height):
        """更新width热力图的颜色比例尺"""
        # 创建一个垂直的颜色渐变条
        colorbar = np.zeros((height, 20, 3), dtype=np.uint8)
        for i in range(height):
            value = 1.0 - (i / height)  # 从上到下，值从1降到0
            colorbar[i, :, 0] = int(value * 255)  # 红色通道
            colorbar[i, :, 2] = int((1 - value) * 255)  # 蓝色通道

        # 添加最大值和最小值标签
        font = QPainter()
        colorbar_pixmap = QPixmap(20, height)
        colorbar_qimage = QImage(
            colorbar.data, 20, height, 60, QImage.Format_RGB888)
        colorbar_pixmap.convertFromImage(colorbar_qimage)

        painter = QPainter(colorbar_pixmap)
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 8))

        # 在顶部绘制"2.0"
        painter.drawText(0, 10, "2.0")
        # 在底部绘制"0.0"
        painter.drawText(0, height-2, "0.0")

        painter.end()

        self.width_colorbar_label.setPixmap(colorbar_pixmap)

    def point_in_quadrilateral(self, point, quad_points):
        """
        判断点是否在四边形内部
        point: 要检查的点 [x, y]
        quad_points: 四边形的四个顶点 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        """
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        d1 = sign(point, quad_points[0], quad_points[1])
        d2 = sign(point, quad_points[1], quad_points[2])
        d3 = sign(point, quad_points[2], quad_points[3])
        d4 = sign(point, quad_points[3], quad_points[0])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0) or (d4 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0) or (d4 > 0)

        return not (has_neg and has_pos)
