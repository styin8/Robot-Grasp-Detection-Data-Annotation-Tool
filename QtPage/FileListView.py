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

        # Layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.file_groupbox = QGroupBox("File List")
        self.file_groupbox.setAlignment(Qt.AlignCenter)

        self.file_layout = QVBoxLayout()
        self.file_layout.addWidget(self.list_widget)
        self.file_layout.addWidget(self.clear_button)
        self.file_groupbox.setLayout(self.file_layout)

        self.layout.addWidget(self.file_groupbox)

        # Connect Function
        self.list_widget.itemClicked.connect(self.displayImage)
        self.clear_button.clicked.connect(self.clearList)
        self.list_widget.currentItemChanged.connect(self.displayImage)

    def displayImage(self, item):
        if not item:  # 如果没有选中项，直接返回
            return

        # origin image
        file_path = os.path.join(self.folder_path, item.text())
        origin = QPixmap(file_path)
        scaled_pixmap = origin.scaled(640, 480, Qt.KeepAspectRatio)
        self.ShowViewIns.current_pixmap = scaled_pixmap.copy()
        self.ShowViewIns.origin_image.setPixmap(scaled_pixmap)

        # 更新图片显示区域信息
        self.ShowViewIns.update_image_rect()

        # 获取实际显示尺寸
        display_rect = self.ShowViewIns.image_rect
        if display_rect:
            # 使用原图的实际尺寸初始化热力图
            original_width = origin.width()
            original_height = origin.height()

            # init quality image
            self.ShowViewIns.quality_map = np.zeros((original_height, original_width), dtype=np.float32)
            quality_colored = self.ShowViewIns.apply_colormap(self.ShowViewIns.quality_map)
            quality_qimage = QImage(quality_colored.data, original_width, original_height, original_width * 3, QImage.Format_RGB888)
            self.ShowViewIns.quality_image.setPixmap(QPixmap.fromImage(quality_qimage))
            self.ShowViewIns.quality_image.setFixedSize(original_width, original_height)

            # init angle image
            self.ShowViewIns.angle_map = np.zeros((original_height, original_width), dtype=np.float32)
            angle_colored = self.ShowViewIns.apply_colormap(self.ShowViewIns.angle_map)
            angle_qimage = QImage(angle_colored.data, original_width, original_height, original_width * 3, QImage.Format_RGB888)
            self.ShowViewIns.angle_image.setPixmap(QPixmap.fromImage(angle_qimage))
            self.ShowViewIns.angle_image.setFixedSize(original_width, original_height)

            # init width image
            self.ShowViewIns.width_map = np.zeros((original_height, original_width), dtype=np.float32)
            width_colored = self.ShowViewIns.apply_colormap(self.ShowViewIns.width_map)
            width_qimage = QImage(width_colored.data, original_width, original_height, original_width * 3, QImage.Format_RGB888)
            self.ShowViewIns.width_image.setPixmap(QPixmap.fromImage(width_qimage))
            self.ShowViewIns.width_image.setFixedSize(original_width, original_height)

    def clearList(self):
        self.list_widget.clear()
        self.ShowViewIns.origin_image.setText("Please add images and select an image :)")
        self.ShowViewIns.quality_image.clear()
        self.ShowViewIns.angle_image.clear()
        self.ShowViewIns.width_image.clear()

    def showFirstImage(self):
        if self.list_widget.count() > 0:
            first_item = self.list_widget.item(0)
            self.list_widget.setCurrentItem(first_item)
            self.displayImage(first_item)
