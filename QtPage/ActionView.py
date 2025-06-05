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
        self.action_groupbox = QGroupBox("Operation Panel")
        self.action_groupbox.setAlignment(Qt.AlignCenter)
        self.action_layout = QVBoxLayout()

        # Action/Component
        select_text = QLabel("Select Grasp Center Axis")
        select_text.setAlignment(Qt.AlignCenter)
        self.select_button = QPushButton("Select")
        self.select_button.setFixedWidth(200)
        self.select_button.clicked.connect(
            lambda: self.check_image_loaded(self.toggle_drawing_mode))
        self.action_layout.addWidget(select_text)
        self.action_layout.addWidget(self.select_button)
        self.action_layout.setAlignment(self.select_button, Qt.AlignCenter)

        mark_text = QLabel("Mark Grasp Width")
        mark_text.setAlignment(Qt.AlignCenter)
        self.mark_button = QPushButton("Mark")
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

        self.generate_button = QPushButton("Generate Preview")
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

        fine_text = QLabel("Select Area for Fine-tuning")
        fine_text.setAlignment(Qt.AlignCenter)

        # Add Up and Down buttons
        self.fine_up_button = QPushButton("Increase")
        self.fine_up_button.setFixedWidth(95)
        self.fine_up_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_fine_up))

        self.fine_down_button = QPushButton("Decrease")
        self.fine_down_button.setFixedWidth(95)
        self.fine_down_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_fine_down))

        # Create horizontal layout to place Up and Down buttons
        fine_tune_buttons = QHBoxLayout()
        fine_tune_buttons.addWidget(self.fine_up_button)
        fine_tune_buttons.addWidget(self.fine_down_button)

        self.action_layout.addWidget(fine_text)
        self.action_layout.addLayout(fine_tune_buttons)
        self.action_layout.setAlignment(fine_tune_buttons, Qt.AlignCenter)

        self.action_layout.addSpacing(20)

        self.save_button = QPushButton("Save")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(
            lambda: self.check_image_loaded(self.handle_save))
        self.action_layout.addWidget(self.save_button)
        self.action_layout.setAlignment(self.save_button, Qt.AlignCenter)

        self.action_groupbox.setLayout(self.action_layout)

        # Output
        self.output_groupbox = QGroupBox("Output Information")
        self.output_groupbox.setAlignment(Qt.AlignCenter)
        self.output_layout = QVBoxLayout()
        self.output_layout.setAlignment(Qt.AlignCenter)

        # Output/Component
        self.output_list = QListWidget()
        self.output_list.setFixedWidth(200)
        self.output_list.setFixedHeight(480)
        # Use stylesheet to set text center
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

        # Define button styles
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

        # Apply default styles to all buttons (remove fine_button)
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
                                "Warning",
                                "Please upload and select an image first!",
                                QMessageBox.Ok)
            return
        callback_function()

    def on_drawing_finished(self):
        """当绘制完成时更新按钮状态"""
        self.select_button.setText("Select")

    def toggle_drawing_mode(self):
        self.show_view.is_drawing = not self.show_view.is_drawing
        if self.show_view.is_drawing:
            self.select_button.setText("Drawing...")
        else:
            self.select_button.setText("Select")

    def handle_slider_change(self):
        """处理滑块值变化的逻辑"""
        if not self.show_view.current_grasp_line:
            return

        value = self.mark_slider.value()
        # Convert slider value to ratio (0-200 to 0-2.0)
        ratio = value / 100.0
        # Call ShowView method to redraw vertical line
        self.show_view.update_perpendicular_line(ratio)

    def handle_mark(self):
        """处理Mark按钮点击的逻辑"""
        # Check if a select line has already been drawn
        if not self.show_view.current_grasp_line:
            QMessageBox.warning(self.widget,
                                "Warning",
                                "Please draw a line using the select button first!",
                                QMessageBox.Ok)
            return

        # Set slider value to default length of vertical line
        self.mark_slider.setValue(25)

        # Use current slider value to draw vertical line
        ratio = self.mark_slider.value() / 100.0
        if not self.show_view.draw_perpendicular_line(ratio):
            QMessageBox.warning(self.widget,
                                "Warning",
                                "Cannot draw vertical line, please try again!",
                                QMessageBox.Ok)

    def handle_generate(self):
        """处理Generate按钮点击的逻辑"""
        # Check if there are labeled grasp lines
        if not self.show_view.grasp_lines:
            QMessageBox.warning(self.widget,
                                "Warning",
                                "Please complete the grasp axis selection and width marking first!",
                                QMessageBox.Ok)
            return

        # Generate heatmap
        if not self.show_view.generate_heatmaps():
            QMessageBox.warning(self.widget,
                                "Warning",
                                "Failed to generate heatmap, please try again!",
                                QMessageBox.Ok)

    def handle_fine_up(self):
        """理Up按钮点击的逻辑"""
        if self.fine_up_button.styleSheet() == self.selected_style:
            # If already selected, cancel selection
            self.show_view.set_fine_tune_mode(None)
            self.fine_up_button.setStyleSheet(self.normal_style)
        else:
            # If not selected, select
            self.show_view.set_fine_tune_mode('up')
            self.fine_up_button.setStyleSheet(self.selected_style)
            self.fine_down_button.setStyleSheet(self.normal_style)

    def handle_fine_down(self):
        """处理Down按钮点击的逻辑"""
        if self.fine_down_button.styleSheet() == self.selected_style:
            # If already selected, cancel selection
            self.show_view.set_fine_tune_mode(None)
            self.fine_down_button.setStyleSheet(self.normal_style)
        else:
            # If not selected, select
            self.show_view.set_fine_tune_mode('down')
            self.fine_down_button.setStyleSheet(self.selected_style)
            self.fine_up_button.setStyleSheet(self.normal_style)

    def handle_save(self):
        """处理保存按钮点击的逻辑"""
        if not self.show_view.quality_map is not None or \
           not self.show_view.angle_map is not None or \
           not self.show_view.width_map is not None:
            QMessageBox.warning(self.widget,
                                "Warning",
                                "Please generate heatmap first!",
                                QMessageBox.Ok)
            return

        # Get current image file name (without extension)
        current_item = self.show_view.current_pixmap
        if not current_item:
            QMessageBox.warning(self.widget,
                                "Warning",
                                "Please select an image first!",
                                QMessageBox.Ok)
            return

        # Get original image size
        original_height = self.show_view.current_pixmap.height()
        original_width = self.show_view.current_pixmap.width()

        # Create label folder
        folder_path = os.path.dirname(
            os.path.dirname(self.show_view.current_file_path))
        label_folder = os.path.join(folder_path, 'labels')
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)

        # Get original file name (without extension)
        base_name = os.path.splitext(os.path.basename(
            self.show_view.current_file_path))[0]
        save_path = os.path.join(label_folder, f"{base_name}.mat")

        try:
            # Resize heatmap to original image size
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

            # Save as .dat file
            combined_data.tofile(save_path)

            # Display save path in output box
            self.output_list.addItem(f"Saved to: {save_path}")
            # Scroll to latest item
            self.output_list.scrollToBottom()

        except Exception as e:
            # Pop up error prompt
            QMessageBox.critical(self.widget,
                                 "Error",
                                 f"Save failed: {str(e)}",
                                 QMessageBox.Ok)

            # Clear all annotations for current image
            self.show_view.grasp_lines = []  # Clear grasp line information
            self.show_view.current_grasp_line = None  # Clear current selected grasp line
            self.show_view.quality_map = None  # Clear quality map
            self.show_view.angle_map = None  # Clear angle map
            self.show_view.width_map = None  # Clear width map
            self.show_view.temp_pixmap = None  # Clear temporary image
            self.show_view.is_drawing = False  # Reset drawing state
            self.show_view.start_point = None  # Clear start point
            self.show_view.end_point = None  # Clear end point
            self.show_view.fine_tune_mode = None  # Reset fine-tuning mode

            # Clear scale
            self.show_view.colorbar_label.clear()
            self.show_view.width_colorbar_label.clear()
            self.show_view.angle_colorbar_label.clear()

            # Clear label text
            self.show_view.quality_label.setText("")
            self.show_view.angle_label.setText("")
            self.show_view.width_label.setText("")

            # Reload original image
            if self.show_view.current_pixmap:
                self.show_view.origin_image.setPixmap(
                    self.show_view.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

            # Display error information in output box
            self.output_list.addItem(f"Save failed: {str(e)}")
            self.output_list.scrollToBottom()
