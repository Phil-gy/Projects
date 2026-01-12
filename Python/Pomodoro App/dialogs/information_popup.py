from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel


class InformationPopUp(QDialog):
    def __init__(self, is_work_mode: bool, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowTitle("The Times up !!")
        self.resize(300, 200)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        if is_work_mode:
            message = QLabel("Time for a break !!")
        else:
            message = QLabel("Get back to work asap !!")

        message.setAlignment(Qt.AlignCenter)
        message.setFont(QFont("Segoe UI", 14, QFont.Bold))

        layout.addWidget(message)
        self.setLayout(layout)

        self.adjustSize()
        self.setFixedSize(self.sizeHint())
