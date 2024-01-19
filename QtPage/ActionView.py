from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QListWidget, QPushButton, QLabel, QGroupBox, QSlider
from PyQt5.QtCore import Qt


class ActionView():
    def __init__(self) -> None:

        # Layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Action
        self.action_groupbox = QGroupBox("Action")
        self.action_groupbox.setAlignment(Qt.AlignCenter)
        # self.action_groupbox.setFixedSize(200, 300)
        self.action_layout = QVBoxLayout()

        # Action/Component
        select_text = QLabel("Select the grasp center axis")
        select_text.setAlignment(Qt.AlignCenter)
        select_button = QPushButton("Select")
        select_button.setFixedWidth(200)
        self.action_layout.addWidget(select_text)
        self.action_layout.addWidget(select_button)
        self.action_layout.setAlignment(select_button, Qt.AlignCenter)

        mark_text = QLabel("Mark the grasp width")
        mark_text.setAlignment(Qt.AlignCenter)
        mark_slider = QSlider(Qt.Horizontal)
        mark_slider.setFixedWidth(200)
        mark_slider.setTickPosition(QSlider.TicksBelow)
        mark_slider.setMinimum(0)
        mark_slider.setMaximum(10)
        mark_slider.setValue(5)
        generate_button = QPushButton("Generate")
        generate_button.setFixedWidth(200)
        self.action_layout.addWidget(mark_text)
        self.action_layout.addWidget(generate_button)
        self.action_layout.addWidget(mark_slider)
        self.action_layout.setAlignment(mark_slider, Qt.AlignCenter)
        self.action_layout.setAlignment(generate_button, Qt.AlignCenter)

        fine_text = QLabel("Select the area to fine-tune")
        fine_text.setAlignment(Qt.AlignCenter)
        fine_button = QPushButton("Select")
        fine_button.setFixedWidth(200)
        self.action_layout.addWidget(fine_text)
        self.action_layout.addWidget(fine_button)
        self.action_layout.setAlignment(fine_button, Qt.AlignCenter)

        self.action_layout.addSpacing(20)

        save_button = QPushButton("Save")
        save_button.setFixedWidth(200)
        self.action_layout.addWidget(save_button)
        self.action_layout.setAlignment(save_button, Qt.AlignCenter)

        self.action_groupbox.setLayout(self.action_layout)

        # Output
        self.output_groupbox = QGroupBox("Output")
        self.output_groupbox.setAlignment(Qt.AlignCenter)
        self.output_layout = QVBoxLayout()

        # Output/Component
        output = QListWidget()
        self.output_layout.addWidget(output)
        self.output_groupbox.setLayout(self.output_layout)

        # Add to Layout
        self.layout.addWidget(self.action_groupbox)
        self.layout.addWidget(self.output_groupbox)
