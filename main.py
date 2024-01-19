from PyQt5.QtWidgets import QApplication
from QtPage.MainWindow import MainWindow


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
