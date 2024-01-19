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

    def displayImage(self, item):
        # origin image
        file_path = os.path.join(self.folder_path, item.text())
        origin = QPixmap(file_path)
        self.ShowViewIns.origin_image.setPixmap(
            origin.scaled(640, 480, Qt.KeepAspectRatio))

        # init quality image
        self.ShowViewIns.quality, qimage = ShowView.init_label_image(640, 480)
        self.ShowViewIns.quality_image.setPixmap(
            QPixmap.fromImage(qimage).scaled(320, 240, Qt.KeepAspectRatio))

        # init angle image
        self.ShowViewIns.angle, qimage = ShowView.init_label_image(640, 480)
        self.ShowViewIns.angle_image.setPixmap(
            QPixmap.fromImage(qimage).scaled(320, 240, Qt.KeepAspectRatio))

        # init width image
        self.ShowViewIns.width, qimage = ShowView.init_label_image(640, 480)
        self.ShowViewIns.width_image.setPixmap(
            QPixmap.fromImage(qimage).scaled(320, 240, Qt.KeepAspectRatio))

    def clearList(self):
        self.list_widget.clear()
        self.ShowViewIns.origin_image.setText("Please add images and select an image :)")
        self.ShowViewIns.quality_image.setText(" ")
        self.ShowViewIns.angle_image.setText(" ")
        self.ShowViewIns.width_image.setText(" ")
