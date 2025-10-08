import sys, random
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt

class LearningHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Learning Hub")
        self.setGeometry(400, 400, 400, 400)

        self.setStyleSheet("""
            QWidget { background-color: #13161a; color: #E6EDF3; font-size: 14px; }
            QLabel#Hint  { color: #9aa4af; font-size: 12px; }
            QLabel { padding: 2px 4px; }
            QPushButton {
                background: #21262d; border: 1px solid #30363d; border-radius: 10px;
                padding: 10px 14px; font-weight: 600;
            }
            QPushButton:hover   { background: #2a3139; }
            QPushButton:pressed { background: #1d2228; }
        """)

        self.quotes = [
            "Leg dein Handy Weg",
            "You got this ! Dont stop now !!!!",
            "You dont need more time—you need more focus.",
            "Lern gut, sonst 14 Semester Regelstudienzeit !",
            "3 Versuch !!!",
            "Straff dich !",
            "LOCK IN ! Your future depends on today !",
        ]

        # UI
        self.quote = QLabel("", self)
        self.quote.setAlignment(Qt.AlignCenter)
        self.quote.setWordWrap(True)
        self.quote.setStyleSheet("font-size:18px; padding:12px;")

        self.pomodoro_rain50 = QPushButton("Pomodoro Rain 50/10")
        self.pomodoro_rain25 = QPushButton("Pomodoro Rain 25/5")
        self.River_Rain = QPushButton("River + Rain")
        self.River_Thunder = QPushButton("River + Thunder")
        self.Entspannte_Musik = QPushButton("Entspannte Musik")
        self.pomodoroSite = QPushButton("Pomodoro Site")
        self.close_btn = QPushButton("Close App")  # don't shadow QWidget.close

        # Single layout (don’t overwrite it later)
        layout = QVBoxLayout(self)
        layout.addWidget(self.quote)
        layout.addSpacing(10)
        layout.addWidget(self.motivation)
        layout.addWidget(self.pomodoro_rain50)
        layout.addWidget(self.pomodoro_rain25)
        layout.addWidget(self.River_Rain)
        layout.addWidget(self.River_Thunder)
        layout.addWidget(self.Entspannte_Musik)
        layout.addWidget(self.pomodoroSite)
        layout.addWidget(self.close_btn)

        # Show a quote on startup
        self.show_random_quote()

    def show_random_quote(self):
        self.quote.setText(random.choice(self.quotes))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LearningHub()
    window.show()
    sys.exit(app.exec())
