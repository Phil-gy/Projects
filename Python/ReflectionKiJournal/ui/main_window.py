from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout
from .sidebar import Sidebar
from .editor_panel import EditorPanel
from .mood_slider import MoodSlider
import os
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QVariantAnimation
from PySide6.QtGui import QColor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reflection Journal")
        self.resize(900, 600)

        self.sidebar = Sidebar()
        self.editor = EditorPanel()
        self.mood_slider = MoodSlider()
        self.load_stylesheet()

        # Layouts
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.editor)
       # right_layout.addWidget(self.mood_slider)  # ⬅ here under the text editor

        self.sidebar.entry_selected.connect(self.editor.load_entry)

        right_container = QWidget()
        right_container.setLayout(right_layout)

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(right_container)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_stylesheet(self):
        """Loads global QSS file."""
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        with open(qss_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
