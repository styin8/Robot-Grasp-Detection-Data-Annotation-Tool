from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QWidget,
                             QFileDialog, QListWidget, QPushButton, QLabel,
                             QGroupBox, QSlider, QMessageBox)
from PyQt5.QtCore import Qt
import os
import cv2
import numpy as np


class ActionView():
    def __init__(self, show_view_instance) -> None:
        # 保存ShowView实例的引用
        self.show_view = show_view_instance
        # 设置回调函数
        self.show_view.on_drawing_finished = self.on_drawing_finished

        # Layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Action
        self.action_groupbox = QGroupBox("操作面板")
        self.action_groupbox.setAlignment(Qt.AlignCenter)
        self.action_layout = QVBoxLayout()

        # Action/Component
        select_text = QLabel("选择抓取中心轴线")
        select_text.setAlignment(Qt.AlignCenter)
        self.select_button = QPushButton("选择")
        self.select_button.setFixedWidth(200)
        self.select_button.clicked.connect(
            lambda: self.check_image_loaded(self.toggle_drawing_mode))
        self.action_layout.addWidget(select_text)
        self.action_layout.addWidget(self.select_button)
        self.action_layout.setAlignment(self.select_button, Qt.AlignCenter)

        mark_text = QLabel("标记抓取宽度")
        mark_text.setAlignment(Qt.AlignCenter)
        self.mark_button = QPushButton("标记")
        self.mark_button.setFixedWidth(200)
        self.mark_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_mark))

        self.mark_slider = QSlider(Qt.Horizontal)
        self.mark_slider.setFixedWidth(200)
        self.mark_slider.setTickPosition(QSlider.TicksBelow)
        self.mark_slider.setMinimum(0)
        self.mark_slider.setMaximum(200)
        self.mark_slider.setValue(25)
        self.mark_slider.setTickInterval(10)
        self.mark_slider.valueChanged.connect(
            lambda: self.check_image_loaded(self.handle_slider_change))

        self.generate_button = QPushButton("生成热力图")
        self.generate_button.setFixedWidth(200)
        self.generate_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_generate))

        self.action_layout.addWidget(mark_text)
        self.action_layout.addWidget(self.mark_button)
        self.action_layout.addWidget(self.mark_slider)
        self.action_layout.addWidget(self.generate_button)
        self.action_layout.setAlignment(self.mark_button, Qt.AlignCenter)
        self.action_layout.setAlignment(self.mark_slider, Qt.AlignCenter)
        self.action_layout.setAlignment(self.generate_button, Qt.AlignCenter)

        fine_text = QLabel("选择区域进行微调")
        fine_text.setAlignment(Qt.AlignCenter)

        # 加Up和Down按钮
        self.fine_up_button = QPushButton("增加质量值")
        self.fine_up_button.setFixedWidth(95)
        self.fine_up_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_fine_up))

        self.fine_down_button = QPushButton("减少质量值")
        self.fine_down_button.setFixedWidth(95)
        self.fine_down_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_fine_down))

        # 创建水平布局来放置Up和Down按钮
        fine_tune_buttons = QHBoxLayout()
        fine_tune_buttons.addWidget(self.fine_up_button)
        fine_tune_buttons.addWidget(self.fine_down_button)

        self.action_layout.addWidget(fine_text)
        self.action_layout.addLayout(fine_tune_buttons)
        self.action_layout.setAlignment(fine_tune_buttons, Qt.AlignCenter)

        self.action_layout.addSpacing(20)

        self.save_button = QPushButton("保存")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_save))
        self.action_layout.addWidget(self.save_button)
        self.action_layout.setAlignment(self.save_button, Qt.AlignCenter)

        self.action_groupbox.setLayout(self.action_layout)

        # Output
        self.output_groupbox = QGroupBox("输出信息")
        self.output_groupbox.setAlignment(Qt.AlignCenter)
        self.output_layout = QVBoxLayout()
        self.output_layout.setAlignment(Qt.AlignCenter)

        # Output/Component
        self.output_list = QListWidget()
        self.output_list.setFixedWidth(200)
        self.output_list.setFixedHeight(480)
        # 使用样式表设置文本居中
        self.output_list.setStyleSheet("""
            QListWidget {
                text-align: center;
            }
            QListWidget::item {
                text-align: center;
                alignment: center;
            }
        """)

        self.output_layout.addWidget(self.output_list)
        self.output_groupbox.setLayout(self.output_layout)

        # Add to Layout
        self.layout.addWidget(self.action_groupbox)
        self.layout.addWidget(self.output_groupbox)

        # 定义按钮样式
        self.normal_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """

        self.selected_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #3399ff;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """

        # 应用默认样式到所有按钮（移除fine_button）
        self.select_button.setStyleSheet(self.normal_style)
        self.mark_button.setStyleSheet(self.normal_style)
        self.generate_button.setStyleSheet(self.normal_style)
        self.fine_up_button.setStyleSheet(self.normal_style)
        self.fine_down_button.setStyleSheet(self.normal_style)
        self.save_button.setStyleSheet(self.normal_style)

    def check_image_loaded(self, callback_function):
        """检查是否已加载图片的通用方法"""
        if not self.show_view.current_pixmap:
            QMessageBox.warning(self.widget,
                                "警告",
                                "请先上传并选择一张图片！",
                                QMessageBox.Ok)
            return
        callback_function()

    def on_drawing_finished(self):
        """当绘制完成时更新按钮状态"""
        self.select_button.setText("选择")

    def toggle_drawing_mode(self):
        self.show_view.is_drawing = not self.show_view.is_drawing
        if self.show_view.is_drawing:
            self.select_button.setText("绘制中...")
        else:
            self.select_button.setText("选择")

    def handle_slider_change(self):
        """处理滑块值变化的逻辑"""
        if not self.show_view.current_grasp_line:
            return

        value = self.mark_slider.value()
        # 将滑块值转换为比例（0-200 转换为 0-2.0）
        ratio = value / 100.0
        # 调用ShowView的方法重绘垂直线
        self.show_view.update_perpendicular_line(ratio)

    def handle_mark(self):
        """处理Mark按钮点击的逻辑"""
        # 检查是否已经画了select线
        if not self.show_view.current_grasp_line:
            QMessageBox.warning(self.widget,
                                "警告",
                                "请先使用选择按钮画一条线！",
                                QMessageBox.Ok)
            return

        # 设置滑动条的值为垂直线的默认长度
        self.mark_slider.setValue(25)

        # 使用当前滑块值绘制垂直线
        ratio = self.mark_slider.value() / 100.0
        if not self.show_view.draw_perpendicular_line(ratio):
            QMessageBox.warning(self.widget,
                                "警告",
                                "无法绘制垂直线，请重试！",
                                QMessageBox.Ok)

    def handle_generate(self):
        """处理Generate按钮点击的逻辑"""
        # 检查是否有已标注抓取线
        if not self.show_view.grasp_lines:
            QMessageBox.warning(self.widget,
                                "警告",
                                "请先完成抓取轴的选择和宽度标注！",
                                QMessageBox.Ok)
            return

        # 生成热力图
        if not self.show_view.generate_heatmaps():
            QMessageBox.warning(self.widget,
                                "警告",
                                "生成热力图失败，请重试！",
                                QMessageBox.Ok)

    def handle_fine_up(self):
        """理Up按钮点击的逻辑"""
        if self.fine_up_button.styleSheet() == self.selected_style:
            # 如果已经选中，则取消选中
            self.show_view.set_fine_tune_mode(None)
            self.fine_up_button.setStyleSheet(self.normal_style)
        else:
            # 如果未选中，则选中
            self.show_view.set_fine_tune_mode('up')
            self.fine_up_button.setStyleSheet(self.selected_style)
            self.fine_down_button.setStyleSheet(self.normal_style)

    def handle_fine_down(self):
        """处理Down按钮点击的逻辑"""
        if self.fine_down_button.styleSheet() == self.selected_style:
            # 如果已经选中，则取消选中
            self.show_view.set_fine_tune_mode(None)
            self.fine_down_button.setStyleSheet(self.normal_style)
        else:
            # 如果未选中，则选中
            self.show_view.set_fine_tune_mode('down')
            self.fine_down_button.setStyleSheet(self.selected_style)
            self.fine_up_button.setStyleSheet(self.normal_style)

    def handle_save(self):
        """处理保存按钮点击的逻辑"""
        if not self.show_view.quality_map is not None or \
           not self.show_view.angle_map is not None or \
           not self.show_view.width_map is not None:
            QMessageBox.warning(self.widget,
                                "警告",
                                "请先生成热力图！",
                                QMessageBox.Ok)
            return

        # 获取当前图片的文件名（不包含扩展名）
        current_item = self.show_view.current_pixmap
        if not current_item:
            QMessageBox.warning(self.widget,
                                "警告",
                                "请先选择一张图片！",
                                QMessageBox.Ok)
            return

        # 获取原始图片的尺寸
        original_height = self.show_view.current_pixmap.height()
        original_width = self.show_view.current_pixmap.width()

        # 创建label文件夹
        folder_path = os.path.dirname(
            os.path.dirname(self.show_view.current_file_path))
        label_folder = os.path.join(folder_path, 'labels')
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)

        # 获取原始文件名（不包含扩展名）
        base_name = os.path.splitext(os.path.basename(
            self.show_view.current_file_path))[0]
        save_path = os.path.join(label_folder, f"{base_name}.mat")

        try:
            # 将预览图尺寸的热力图放大到原图尺寸
            quality_resized = cv2.resize(self.show_view.quality_map,
                                         (original_width, original_height),
                                         interpolation=cv2.INTER_LINEAR)
            width_resized = cv2.resize(self.show_view.width_map,
                                       (original_width, original_height),
                                       interpolation=cv2.INTER_LINEAR)
            angle_resized = cv2.resize(self.show_view.angle_map,
                                       (original_width, original_height),
                                       interpolation=cv2.INTER_LINEAR)

            combined_data = cv2.merge(
                [quality_resized, width_resized, angle_resized])

            # 保存为.dat文件
            combined_data.tofile(save_path)

            # 在output框中显示保存路径
            self.output_list.addItem(f"已保存到: {save_path}")
            # 滚动到最新的项
            self.output_list.scrollToBottom()

        except Exception as e:
            # 弹出错误提示框
            QMessageBox.critical(self.widget,
                                 "错误",
                                 f"保存失败: {str(e)}",
                                 QMessageBox.Ok)

            # 清理当前图片的所有标注信息
            self.show_view.grasp_lines = []  # 清空抓取线信息
            self.show_view.current_grasp_line = None  # 清空当前选中的抓取线
            self.show_view.quality_map = None  # 清空质量图
            self.show_view.angle_map = None  # 清空角度图
            self.show_view.width_map = None  # 清空宽度图
            self.show_view.temp_pixmap = None  # 清空临时图像
            self.show_view.is_drawing = False  # 重置绘制状态
            self.show_view.start_point = None  # 清空起点
            self.show_view.end_point = None  # 清空终点
            self.show_view.fine_tune_mode = None  # 重置微调模式

            # 清空比例尺
            self.show_view.colorbar_label.clear()
            self.show_view.width_colorbar_label.clear()
            self.show_view.angle_colorbar_label.clear()

            # 清空标签文字
            self.show_view.quality_label.setText("")
            self.show_view.angle_label.setText("")
            self.show_view.width_label.setText("")

            # 重新加载原图
            if self.show_view.current_pixmap:
                self.show_view.origin_image.setPixmap(
                    self.show_view.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

            # 在output框中显示错误信息
            self.output_list.addItem(f"保存失败: {str(e)}")
            self.output_list.scrollToBottom()
