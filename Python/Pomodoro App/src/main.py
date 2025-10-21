import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro App")

        # modes
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.is_work_mode = True  

        # widgets
        self.counter = self.work_duration
        self.label = QLabel(self.format_time(self.counter))
        self.button = QPushButton("Start")
        self.button.clicked.connect(self.start_timer)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def format_time(self, total_seconds: int) -> str:
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(1000)  
            self.button.setText("Stop")
        else:
            self.timer.stop()
            self.button.setText("Start")

    def update_timer(self):
        if self.counter > 0:
            self.counter -= 1
            self.label.setText(self.format_time(self.counter))
        else:
            self.timer.stop()

            if self.is_work_mode:
                self.label.setText("Break time! ☕")
                self.counter = self.break_duration
            else:
                self.label.setText("Back to work! 💪")
                self.counter = self.work_duration

            self.is_work_mode = not self.is_work_mode
            self.button.setText("Start")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
