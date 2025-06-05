from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QListWidget, QPushButton, QLabel, QGroupBox
from PyQt5.QtGui import QPixmap, QImageReader, QImage
from PyQt5.QtCore import Qt
import os
import numpy as np
from QtPage.ShowView import ShowView


class FileListView():
    def __init__(self, ShowViewIns) -> None:
        # variable
        self.file_path = []
        self.folder_path = ""
        self.ShowViewIns = ShowViewIns

        # Component
        self.list_widget = QListWidget()
        self.clear_button = QPushButton("Clear List")
        self.select_folder_button = QPushButton("Select Folder")

        # Set fixed width
        self.widget = QWidget()
        self.widget.setFixedWidth(200)  # Set fixed width to 200 pixels

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.file_list_groupbox = QGroupBox("File List")
        self.file_list_groupbox.setAlignment(Qt.AlignCenter)

        # Set fixed width for list widget
        self.list_widget.setFixedWidth(150)  # Set list widget width slightly smaller than container

        # Set fixed width for buttons
        self.clear_button.setFixedWidth(160)
        self.select_folder_button.setFixedWidth(180)

        self.file_layout = QVBoxLayout()
        self.file_layout.addWidget(self.list_widget)
        self.file_layout.addWidget(self.clear_button)
        self.file_list_groupbox.setLayout(self.file_layout)

        self.layout.addWidget(self.file_list_groupbox)

        # Connect Function
        self.list_widget.itemClicked.connect(self.displayImage)
        self.clear_button.clicked.connect(self.clearList)
        self.list_widget.currentItemChanged.connect(self.displayImage)

    def displayImage(self, item):
        if not item:  # If no item is selected, return immediately
            return

        # Clear all previous information
        self.ShowViewIns.grasp_lines = []  # Clear grasp line information
        self.ShowViewIns.current_grasp_line = None  # Clear current selected grasp line
        self.ShowViewIns.quality_map = None  # Clear quality map
        self.ShowViewIns.angle_map = None  # Clear angle map
        self.ShowViewIns.width_map = None  # Clear width map
        self.ShowViewIns.temp_pixmap = None  # Clear temporary image
        self.ShowViewIns.is_drawing = False  # Reset drawing state
        self.ShowViewIns.start_point = None  # Clear start point
        self.ShowViewIns.end_point = None  # Clear end point
        self.ShowViewIns.fine_tune_mode = None  # Reset fine-tune mode

        # Clear scale
        self.ShowViewIns.colorbar_label.clear()
        self.ShowViewIns.width_colorbar_label.clear()
        self.ShowViewIns.angle_colorbar_label.clear()

        # origin image
        file_path = os.path.join(self.folder_path, item.text())
        self.ShowViewIns.current_file_path = file_path
        origin = QPixmap(file_path)
        scaled_pixmap = origin.scaled(640, 480, Qt.KeepAspectRatio)
        self.ShowViewIns.current_pixmap = scaled_pixmap.copy()
        self.ShowViewIns.origin_image.setPixmap(scaled_pixmap)

        # Update image display area information
        self.ShowViewIns.update_image_rect()

        # Get actual display size
        display_rect = self.ShowViewIns.image_rect
        if display_rect:
            # Calculate preview size (use half of display size)
            preview_width = display_rect.width() // 2
            preview_height = display_rect.height() // 2

            # Display label text
            self.ShowViewIns.quality_label.setText("Quality Map")
            self.ShowViewIns.angle_label.setText("Angle Map")
            self.ShowViewIns.width_label.setText("Width Map")

            # init quality image
            self.ShowViewIns.quality, qimage = ShowView.init_label_image(
                preview_width, preview_height)
            self.ShowViewIns.quality_image.setPixmap(QPixmap.fromImage(qimage))
            self.ShowViewIns.quality_image.setFixedSize(
                preview_width, preview_height)

            # init angle image
            self.ShowViewIns.angle, qimage = ShowView.init_label_image(
                preview_width, preview_height)
            self.ShowViewIns.angle_image.setPixmap(QPixmap.fromImage(qimage))
            self.ShowViewIns.angle_image.setFixedSize(
                preview_width, preview_height)

            # init width image
            self.ShowViewIns.width, qimage = ShowView.init_label_image(
                preview_width, preview_height)
            self.ShowViewIns.width_image.setPixmap(QPixmap.fromImage(qimage))
            self.ShowViewIns.width_image.setFixedSize(
                preview_width, preview_height)

    def clearList(self):
        self.list_widget.clear()
        self.ShowViewIns.origin_image.setText("Please add and select an image :)")
        self.ShowViewIns.quality_image.clear()
        self.ShowViewIns.angle_image.clear()
        self.ShowViewIns.width_image.clear()

        # Clear label text
        self.ShowViewIns.quality_label.setText("")
        self.ShowViewIns.angle_label.setText("")
        self.ShowViewIns.width_label.setText("")

        # Clear scale
        self.ShowViewIns.colorbar_label.clear()
        self.ShowViewIns.width_colorbar_label.clear()
        self.ShowViewIns.angle_colorbar_label.clear()

    def showFirstImage(self):
        if self.list_widget.count() > 0:
            first_item = self.list_widget.item(0)
            self.list_widget.setCurrentItem(first_item)
            self.displayImage(first_item)
