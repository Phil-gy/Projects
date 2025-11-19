from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

from .mood_visual import MoodVisual


class MoodSlider(QWidget):
    def __init__(self):
        super().__init__()

        self.mood_value = 0  # -100 .. 100

        self.visual = MoodVisual()

        self.label = QLabel("Neutral")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-100, 100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.update_mood)

        layout = QVBoxLayout()
        layout.addWidget(self.visual, stretch=3)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def update_mood(self, value: int):
        self.mood_value = value
        self.visual.set_mood(value)
        self.label.setText(self.describe_mood(value))

    @staticmethod
    def describe_mood(value: int) -> str:
        if value < -60:
            return "Very Unpleasant"
        elif value < -20:
            return "Slightly Unpleasant"
        elif value < 20:
            return "Neutral"
        elif value < 60:
            return "Pleasant"
        else:
            return "Very Pleasant"
