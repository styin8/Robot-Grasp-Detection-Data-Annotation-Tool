from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QListWidget, QPushButton, QLabel, QGroupBox
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtGui import QPixmap, QImageReader, QImage,QFont
from typing import Tuple


class ShowView():
    def __init__(self) -> None:

        # Component
        self.origin_image = QLabel("Please add images and select an image :)")
        font = QFont()
        font.setPointSize(20)  # 设置字体大小为20
        self.origin_image.setFont(font)
        self.origin_image.setAlignment(Qt.AlignCenter)
        self.origin_image.setGeometry(100, 100, 640, 480)
        self.origin_image.setFixedSize(640, 480)
        self.quality_image = QLabel()
        self.angle_image = QLabel()
        self.width_image = QLabel()

        # Layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Prigin Image
        self.origin_groupbox = QGroupBox("Origin Image")
        self.origin_groupbox.setAlignment(Qt.AlignCenter)
        self.origin_layout = QHBoxLayout()
        self.origin_layout.addWidget(self.origin_image)
        self.origin_groupbox.setLayout(self.origin_layout)

        # Preview
        self.preview_groupbox = QGroupBox("Preview Image")
        self.preview_groupbox.setAlignment(Qt.AlignCenter)
        self.preview_layout = QHBoxLayout()
        self.preview_layout.setAlignment(Qt.AlignCenter)
        self.preview_layout.addWidget(self.quality_image)
        self.preview_layout.addWidget(self.angle_image)
        self.preview_layout.addWidget(self.width_image)
        self.preview_groupbox.setLayout(self.preview_layout)

        self.layout.addWidget(self.origin_groupbox, 3)
        self.layout.addWidget(self.preview_groupbox, 2)

    @staticmethod
    def init_label_image(width, height) -> Tuple[np.ndarray, QImage]:
        image = np.zeros((height, width), dtype=np.float32)
        qimage = QImage(image.data,
                        image.shape[1], image.shape[0], QImage.Format_Grayscale8)

        return image, qimage
