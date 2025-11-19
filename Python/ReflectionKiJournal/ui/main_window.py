from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QTabWidget
from .sidebar import Sidebar
from .editor_panel import EditorPanel
from .mood_slider import MoodSlider
import os
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QVariantAnimation
from PySide6.QtGui import QColor
from .goals_tab import GoalsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reflection KI Journal")
        self.resize(1200, 800)

        self.sidebar = Sidebar()
        self.editor = EditorPanel()
        self.goals_tab = GoalsTab()

        # --- Create tabs ---
        self.tabs = QTabWidget()
        self.tabs.addTab(self.editor, "📖 Journal")
        self.tabs.addTab(self.goals_tab, "🎯 Goals")

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # connect sidebar clicks
        self.sidebar.entry_selected.connect(self.editor.load_entry)

    def load_stylesheet(self):
        """Loads global QSS file."""
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        with open(qss_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
