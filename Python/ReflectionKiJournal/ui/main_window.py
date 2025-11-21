# ui/main_window.py
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
)
from PySide6.QtCore import Qt

from .sidebar import Sidebar
from .editor_panel import EditorPanel
from .goals_tab import GoalsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Reflection KI Journal")
        self.resize(1200, 700)

        # widgets
        self.sidebar = Sidebar()
        self.editor = EditorPanel()
        self.goals_tab = GoalsTab()

        # connect: click on date → load entry
        self.sidebar.entry_selected.connect(self.editor.load_entry)

        # connect: whenever entries.json changes → refresh sidebar list
        self.editor.entries_changed.connect(self.sidebar.refresh_list)

        # tabs on right side
        tabs = QTabWidget()
        tabs.addTab(self.editor, "Journal")
        tabs.addTab(self.goals_tab, "Goals")

        # left/right splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(tabs)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(splitter)

        self.setCentralWidget(container)

        self.load_stylesheet()

    def load_stylesheet(self):
        """
        Load style.qss.

        - When running from source: project root / style.qss
        - When frozen as EXE: folder next to the EXE / style.qss
        """
        if getattr(sys, "frozen", False):
            # Running from the PyInstaller EXE
            base_dir = Path(sys.executable).parent
        else:
            # Running from source
            base_dir = Path(__file__).resolve().parent.parent

        qss_path = base_dir / "style.qss"
        if qss_path.exists():
            try:
                with qss_path.open("r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                print(f"Loaded stylesheet from: {qss_path}")
            except Exception as e:
                print(f"Failed to load stylesheet: {e}")
        else:
            print(f"No style.qss found at: {qss_path}")
