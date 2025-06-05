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
            "Please add and select an image :)")
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
        self.quality_label = QLabel("")  # 初始化时不显示文字
        self.quality_label.setAlignment(Qt.AlignCenter)
        self.angle_label = QLabel("")    # 初始化时不显示文字
        self.angle_label.setAlignment(Qt.AlignCenter)
        self.width_label = QLabel("")    # 初始化时不显示文字
        self.width_label.setAlignment(Qt.AlignCenter)

        # 创建颜色比例尺标签
        self.colorbar_label = QLabel()
        self.width_colorbar_label = QLabel()
        self.angle_colorbar_label = QLabel()  # 新增angle比例尺标签

        self.colorbar_label.setFixedWidth(20)
        self.width_colorbar_label.setFixedWidth(20)
        self.angle_colorbar_label.setFixedWidth(20)  # 设置宽度

        self.colorbar_label.setAlignment(Qt.AlignCenter)
        self.width_colorbar_label.setAlignment(Qt.AlignCenter)
        self.angle_colorbar_label.setAlignment(Qt.AlignCenter)

        # Layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Origin Image
        self.origin_groupbox = QGroupBox("Original Image")
        self.origin_groupbox.setAlignment(Qt.AlignCenter)
        self.origin_layout = QHBoxLayout()
        self.origin_layout.addWidget(self.origin_image)
        self.origin_groupbox.setLayout(self.origin_layout)

        # Preview
        self.preview_groupbox = QGroupBox("Preview Images")
        self.preview_groupbox.setAlignment(Qt.AlignCenter)
        self.preview_layout = QVBoxLayout()  # Vertical layout

        # Create horizontal layout for preview images
        self.preview_images_layout = QHBoxLayout()
        self.preview_images_layout.setAlignment(Qt.AlignCenter)

        # Create vertical layout for each preview image
        quality_container = QVBoxLayout()    # Vertical layout for image and label
        quality_preview = QHBoxLayout()      # Horizontal layout for scale and image
        quality_preview.addWidget(self.colorbar_label)  # Add scale first
        quality_preview.addWidget(self.quality_image)   # Then add image
        quality_preview.setAlignment(
            self.colorbar_label, Qt.AlignVCenter)  # Vertical center alignment
        quality_container.addLayout(quality_preview)    # Add horizontal layout
        quality_container.addWidget(self.quality_label)  # Add label

        angle_container = QVBoxLayout()
        angle_preview = QHBoxLayout()
        angle_preview.addWidget(self.angle_colorbar_label)
        angle_preview.addWidget(self.angle_image)
        angle_preview.setAlignment(
            self.angle_colorbar_label, Qt.AlignVCenter)
        angle_container.addLayout(angle_preview)
        angle_container.addWidget(self.angle_label)

        width_container = QVBoxLayout()
        width_preview = QHBoxLayout()
        width_preview.addWidget(self.width_colorbar_label)
        width_preview.addWidget(self.width_image)
        width_preview.setAlignment(self.width_colorbar_label, Qt.AlignVCenter)
        width_container.addLayout(width_preview)
        width_container.addWidget(self.width_label)

        # Add each container to preview images layout
        preview_widget1 = QWidget()
        preview_widget1.setLayout(quality_container)
        preview_widget2 = QWidget()
        preview_widget2.setLayout(angle_container)
        preview_widget3 = QWidget()
        preview_widget3.setLayout(width_container)

        self.preview_images_layout.addWidget(preview_widget1)
        self.preview_images_layout.addWidget(preview_widget2)
        self.preview_images_layout.addWidget(preview_widget3)

        # Add preview images layout to preview group layout
        self.preview_layout.addLayout(self.preview_images_layout)
        self.preview_groupbox.setLayout(self.preview_layout)

        self.layout.addWidget(self.origin_groupbox, 3)
        self.layout.addWidget(self.preview_groupbox, 2)

        # 添加一个回调函数属性
        self.on_drawing_finished = None

        # 添加新的存储抓取线的信息
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

        self.current_file_path = None  # 添加这一行

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
            # 调用 update_quality_value 方法来更新值
            self.update_quality_value(event.mapped_pos)
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

                # 重绘所有线，突出显示选中的线
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

                    # 绘选中的线（使用更粗的线条）
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
        if self.fine_tune_mode in ['up', 'down'] and event.buttons() & Qt.LeftButton:
            # 当鼠标按下并移动时，也更新值
            self.update_quality_value(event.mapped_pos)
        elif self.is_drawing and self.start_point:
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

                # 添加到表中
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

                # 保存当前图状
                self.temp_pixmap = self.current_pixmap.copy()

                print(
                    f"Added new grasp line from {grasp_line['start']} to {grasp_line['end']}")

            self.start_point = None
            self.end_point = None
            self.is_drawing = False

            if self.on_drawing_finished:
                self.on_drawing_finished()

    def draw_perpendicular_line(self, length_ratio=0.25):
        """在当前选中取线中心绘制垂直线"""
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
                        width,  # 加步长参数
                        QImage.Format_Grayscale8)
        return image, qimage

    def generate_heatmaps(self):
        """生成热力图，考虑所有已标注的抓取线"""
        if not self.image_rect or not self.grasp_lines:
            return False

        # 获取原图尺寸
        original_height = self.current_pixmap.height()
        original_width = self.current_pixmap.width()

        # 获取预览图尺寸
        preview_height = original_height // 2
        preview_width = original_width // 2

        # 创建热力图（使用预览图尺寸）
        self.quality_map = np.zeros(
            (preview_height, preview_width), dtype=np.float32)
        self.angle_map = np.zeros(
            (preview_height, preview_width), dtype=np.float32)
        self.width_map = np.zeros(
            (preview_height, preview_width), dtype=np.float32)

        # 用于跟踪最大值
        max_angle = float('-inf')
        max_width = float('-inf')

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

                # 计算中心轴与x轴正方向的夹角
                dx_axis = grasp_line['end'][0] - grasp_line['start'][0]
                dy_axis = -(grasp_line['end'][1] - grasp_line['start'][1])
                angle_rad = math.atan2(dy_axis, dx_axis)
                angle_deg = math.degrees(angle_rad)

                # 确保角度在-90到90度之间
                if angle_deg > 90:
                    angle_deg = angle_deg - 180
                elif angle_deg < -90:
                    angle_deg = angle_deg + 180

                # 更新最大角度值
                max_angle = max(max_angle, abs(angle_deg))

                prev_start_x, prev_start_y = None, None
                prev_end_x, prev_end_y = None, None

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

                    # 更新最大宽度值
                    max_width = max(max_width, perp_length)

                    # 绘制垂直线（原图）
                    painter.drawLine(
                        int(start_x), int(start_y),
                        int(end_x), int(end_y)
                    )

                    # 在两个垂直线之间填充区域
                    if i > 0:  # 从第二个点开始，连接前后两个垂直线
                        # 创建多边形的顶点数组（缩放到预览图尺寸）
                        poly_y = np.array([
                            int(prev_start_y * preview_height / original_height),
                            int(prev_end_y * preview_height / original_height),
                            int(end_y * preview_height / original_height),
                            int(start_y * preview_height / original_height)
                        ])
                        poly_x = np.array([
                            int(prev_start_x * preview_width / original_width),
                            int(prev_end_x * preview_width / original_width),
                            int(end_x * preview_width / original_width),
                            int(start_x * preview_width / original_width)
                        ])

                        # 使用polygon函数获取多边形内的所有点
                        rr, cc = polygon(
                            poly_y, poly_x, shape=(preview_height, preview_width))

                        # 计算中心线的点（缩放到预览图尺寸）
                        center_line_start = np.array([
                            int((prev_start_x + prev_end_x) / 2 *
                                preview_width / original_width),
                            int((prev_start_y + prev_end_y) / 2 *
                                preview_height / original_height)
                        ])
                        center_line_end = np.array([
                            int((start_x + end_x) / 2 *
                                preview_width / original_width),
                            int((start_y + end_y) / 2 *
                                preview_height / original_height)
                        ])

                        # 为多边形区域内的每个点计算高斯值
                        for y, x in zip(rr, cc):
                            point = np.array([x, y])
                            # 计算点到中心线的距离
                            dist = self.point_to_line_distance(
                                point, center_line_start, center_line_end)
                            # 计算高斯值（sigma可以调整来改变分布的宽度）
                            sigma = perp_length / \
                                (4 * original_height /
                                 preview_height)  # 调整sigma以适应预览图尺寸
                            gaussian_value = np.exp(-0.5 *
                                                    (dist ** 2) / (sigma ** 2))

                            # 更新quality map（使用高斯值）
                            self.quality_map[y, x] = max(
                                self.quality_map[y, x], gaussian_value)
                            # 更新其他map（保持不变）
                            self.width_map[y, x] = perp_length
                            self.angle_map[y, x] = angle_deg

                    # 更新前一个点的坐标
                    prev_start_x, prev_start_y = start_x, start_y
                    prev_end_x, prev_end_y = end_x, end_y

            print(f"最大角度值: {angle_deg:.2f}°")
            print(f"最大宽度值: {perp_length:.2f}")

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
            self.update_angle_colorbar(h)  # 新增

    def apply_colormap(self, data):
        """应用热力图颜色映射"""
        # 创建彩色图像
        colored = np.zeros((data.shape[0], data.shape[1], 3), dtype=np.uint8)

        # 根据不同类型的数据使用不同的归一化方法
        if data is self.quality_map:
            # quality_map 已经是 0-1 范围，直接使用
            normalized_data = np.clip(data, 0, 1)
        elif data is self.angle_map:
            # angle_map 范围是 -90 到 90，归一化到 0-1
            normalized_data = (data + 90) / 180
        elif data is self.width_map:
            # width_map 范围是 0 到 150，归一化到 0-1
            normalized_data = data / 150
        else:
            # 默认情况，假设数据已经归一化
            normalized_data = np.clip(data, 0, 1)

        # 转换为uint8类型
        data_uint8 = (normalized_data * 255).astype(np.uint8)

        # 应用颜色映射（红色到蓝色渐变）
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
        """更新quality热力图的颜色比例"""
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

        # 在顶部绘制最大值
        painter.drawText(0, 10, "1.0")
        # 在中间绘制中间值
        painter.drawText(0, height//2, "0.5")
        # 在底部绘制最小值
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

        # 在顶部绘制最大值
        painter.drawText(0, 10, "150")
        # 在中间绘制中间值
        painter.drawText(0, height//2, "75")
        # 在底部绘制最小值
        painter.drawText(0, height-2, "0")

        painter.end()
        self.width_colorbar_label.setPixmap(colorbar_pixmap)

    def update_angle_colorbar(self, height):
        """更新angle热力图的颜色比例尺"""
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

        # 在顶部绘制最大值
        painter.drawText(0, 10, "90°")
        # 在中间绘制中间值
        painter.drawText(0, height//2, "0°")
        # 在底部绘制最小值
        painter.drawText(0, height-2, "-90°")

        painter.end()
        self.angle_colorbar_label.setPixmap(colorbar_pixmap)

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

    def point_to_line_distance(self, point, line_start, line_end):
        """计算点到线段的距离"""
        if np.array_equal(line_start, line_end):
            return np.linalg.norm(point - line_start)

        line_vec = line_end - line_start
        point_vec = point - line_start
        line_length = np.linalg.norm(line_vec)
        line_unit_vec = line_vec / line_length
        projection_length = np.dot(point_vec, line_unit_vec)

        if projection_length < 0:
            return np.linalg.norm(point - line_start)
        elif projection_length > line_length:
            return np.linalg.norm(point - line_end)
        else:
            projection = line_start + line_unit_vec * projection_length
            return np.linalg.norm(point - projection)

    def update_quality_value(self, pos):
        """更新quality map的值"""
        # 转换为预览图坐标
        preview_x = int(pos.x() / 2)
        preview_y = int(pos.y() / 2)

        # 更新quality map
        if self.quality_map is not None:
            height, width = self.quality_map.shape
            radius = self.fine_tune_radius // 2  # 预览图上的半径

            # 在圆形区域内更新值
            for y in range(max(0, preview_y - radius), min(height, preview_y + radius)):
                for x in range(max(0, preview_x - radius), min(width, preview_x + radius)):
                    # 计算到中心的距离
                    dist = math.sqrt((x - preview_x) ** 2 + (y - preview_y)**2)
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
