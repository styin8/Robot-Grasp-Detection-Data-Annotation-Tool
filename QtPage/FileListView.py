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
            preview_width = display_rect.width() // 2  # 预览图宽度为原图的一半
            preview_height = display_rect.height() // 2  # 预览图高度为原图的一半
            
            # init quality image
            self.ShowViewIns.quality, qimage = ShowView.init_label_image(preview_width, preview_height)
            self.ShowViewIns.quality_image.setPixmap(QPixmap.fromImage(qimage))
            self.ShowViewIns.quality_image.setFixedSize(preview_width, preview_height)

            # init angle image
            self.ShowViewIns.angle, qimage = ShowView.init_label_image(preview_width, preview_height)
            self.ShowViewIns.angle_image.setPixmap(QPixmap.fromImage(qimage))
            self.ShowViewIns.angle_image.setFixedSize(preview_width, preview_height)

            # init width image
            self.ShowViewIns.width, qimage = ShowView.init_label_image(preview_width, preview_height)
            self.ShowViewIns.width_image.setPixmap(QPixmap.fromImage(qimage))
            self.ShowViewIns.width_image.setFixedSize(preview_width, preview_height)

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
