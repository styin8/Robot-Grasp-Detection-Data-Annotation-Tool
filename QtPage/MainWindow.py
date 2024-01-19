from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QImageReader
from QtPage.ActionView import ActionView
from QtPage.FileListView import FileListView
from QtPage.ShowView import ShowView
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.setWindowTitle("Data Collection Tool for Grasp Detection")

        # Set Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        select_file_action = file_menu.addAction("Select Flie")
        select_folder_action = file_menu.addAction("Select Folder")

        select_file_action.triggered.connect(self.selectFiles)
        select_folder_action.triggered.connect(self.selectFolder)

        # Load layout

        self.ShowViewIns = ShowView()
        self.ActionViewIns = ActionView()
        self.FileListViewIns = FileListView(self.ShowViewIns)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.FileListViewIns.widget,1)
        main_layout.addWidget(self.ShowViewIns.widget,4)
        main_layout.addWidget(self.ActionViewIns.widget,1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def selectFiles(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setNameFilter("Images (*.jpg *.jpeg *.png *.gif *.bmp)")

        if dialog.exec_() == QFileDialog.Accepted:
            file_paths = dialog.selectedFiles()

            self.FileListViewIns.file_path = file_paths
            self.FileListViewIns.folder_path = os.path.dirname(file_paths[0])
            self.FileListViewIns.list_widget.clear()

            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                self.FileListViewIns.list_widget.addItem(file_name)

    def selectFolder(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec_() == QFileDialog.Accepted:
            folder_path = dialog.selectedFiles()[0]

            self.FileListViewIns.file_path = []
            self.FileListViewIns.folder_path = folder_path
            self.FileListViewIns.list_widget.clear()

            # 遍历文件夹中的内容，并添加图片文件到列表控件中
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                file_info = QFileInfo(file_path)
                if file_info.isFile() and self.isImageFile(file_info):
                    self.FileListViewIns.list_widget.addItem(file_name)
                    self.FileListViewIns.file_path.append(file_path)

    def isImageFile(self, file_info):
        # 获取文件的扩展名
        file_extension = file_info.suffix().lower()

        # 使用 QImageReader 来判断扩展名是否为图片格式
        image_reader = QImageReader()
        image_reader.setFileName(file_info.filePath())
        return image_reader.canRead() and file_extension in ["jpg", "jpeg", "png", "gif", "bmp"]
