import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QWidget, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QFont, QColor



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer – Philipp Edition")
        self.resize(540, 440)

        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.is_work_mode = True
        self.counter = self.work_duration

        self.header = QLabel("🍅 Philipp’s Pomodoro")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFont(QFont("Segoe UI", 20, QFont.Bold))

        self.label = QLabel(self.format_time(self.counter))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Consolas", 72, QFont.Bold))

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor("#111111"))
        self.label.setGraphicsEffect(shadow)

        self.button = QPushButton("▶ Start")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.clicked.connect(self.start_timer)

        layout = QVBoxLayout()
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(30)
        layout.addWidget(self.header)
        layout.addWidget(self.label)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)

        frame = QFrame()
        frame.setLayout(layout)
        frame.setObjectName("MainFrame")
        self.setCentralWidget(frame)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.set_theme("work")

    def format_time(self, total_seconds: int) -> str:
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(1000)
            self.button.setText("⏸ Stop")
        else:
            self.timer.stop()
            self.button.setText("▶ Start")

    def update_timer(self):
        if self.counter > 0:
            self.counter -= 1
            self.label.setText(self.format_time(self.counter))
        else:
            self.timer.stop()
            if self.is_work_mode:
                self.is_work_mode = False
                self.counter = self.break_duration
                self.label.setText("Break Time ☕")
                self.set_theme("break")
            else:
                self.is_work_mode = True
                self.counter = self.work_duration
                self.label.setText("Back to Work 💪")
                self.set_theme("work")
            self.button.setText("▶ Start")

    def set_theme(self, mode: str):
        """Switches between work/break mode colors."""
        if mode == "work":
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #27293d, stop:1 #3b3b58);"
            accent = "#f06292"
        else:
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1b5e20, stop:1 #2e7d32);"
            accent = "#c8e6c9"

        self.setStyleSheet(f"""
            QMainWindow {{
                background: {bg_gradient};
            }}
            QLabel {{
                color: {accent};
            }}
            QLabel#Header {{
                color: white;
                font-size: 22px;
            }}
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.08);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
                padding: 12px 30px;
                font-size: 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.18);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.25);
            }}
        """)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
