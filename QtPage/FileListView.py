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
        self.select_folder_button = QPushButton("选择文件夹")

        # 设置固定宽度
        self.widget = QWidget()
        self.widget.setFixedWidth(200)  # 设置固定宽度为200像素
        
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.file_list_groupbox = QGroupBox("文件列表")
        self.file_list_groupbox.setAlignment(Qt.AlignCenter)

        # 设置列表控件的固定宽度
        self.list_widget.setFixedWidth(180)  # 设置列表控件的宽度略小于容器宽度

        # 设置按钮的固定宽度
        self.clear_button.setFixedWidth(180)
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
        if not item:  # 如果没有选中项，直接返回
            return

        # 清空之前的所有信息
        self.ShowViewIns.grasp_lines = []  # 清空抓取线信息
        self.ShowViewIns.current_grasp_line = None  # 清空当前选中的抓取线
        self.ShowViewIns.quality_map = None  # 清空质量图
        self.ShowViewIns.angle_map = None  # 清空角度图
        self.ShowViewIns.width_map = None  # 清空宽度图
        self.ShowViewIns.temp_pixmap = None  # 清空临时图像
        self.ShowViewIns.is_drawing = False  # 重置绘制状态
        self.ShowViewIns.start_point = None  # 清空起点
        self.ShowViewIns.end_point = None  # 清空终点
        self.ShowViewIns.fine_tune_mode = None  # 重���微调模式

        # 清空比例尺
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

        # 更新图片显示区域信息
        self.ShowViewIns.update_image_rect()

        # 获取实际显示尺寸
        display_rect = self.ShowViewIns.image_rect
        if display_rect:
            # 计算预览图尺寸（使用显示尺寸的一半）
            preview_width = display_rect.width() // 2
            preview_height = display_rect.height() // 2

            # 显示标签文字
            self.ShowViewIns.quality_label.setText("质量图")
            self.ShowViewIns.angle_label.setText("角度图")
            self.ShowViewIns.width_label.setText("宽度图")

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
        self.ShowViewIns.origin_image.setText("请添加并选择一张图片 :)")
        self.ShowViewIns.quality_image.clear()
        self.ShowViewIns.angle_image.clear()
        self.ShowViewIns.width_image.clear()

        # 清除标签文字
        self.ShowViewIns.quality_label.setText("")
        self.ShowViewIns.angle_label.setText("")
        self.ShowViewIns.width_label.setText("")

        # 清除比例尺
        self.ShowViewIns.colorbar_label.clear()
        self.ShowViewIns.width_colorbar_label.clear()
        self.ShowViewIns.angle_colorbar_label.clear()

    def showFirstImage(self):
        if self.list_widget.count() > 0:
            first_item = self.list_widget.item(0)
            self.list_widget.setCurrentItem(first_item)
            self.displayImage(first_item)
