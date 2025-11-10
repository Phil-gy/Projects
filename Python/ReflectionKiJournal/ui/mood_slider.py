from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from .mood_visual import MoodVisual  # make sure this import matches your folder structure


class MoodSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.mood_value = 0  # -100 (bad) → 100 (good)

        # Label
        self.label = QLabel("Neutral", alignment=Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-100, 100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.update_mood)

        # Style the slider bar to have a subtle gradient
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4b4b, stop:0.5 #00ffff, stop:1 #4b8cff);
            }
            QSlider::handle:horizontal {
                background: white;
                border-radius: 9px;
                width: 18px;
                margin: -5px 0;
            }
        """)

        # Visual (animated background)
        self.visual = MoodVisual()
        self.visual.setMinimumHeight(150)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.visual, stretch=3)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def update_mood(self, value):
        """Update mood visuals and text when slider moves."""
        self.mood_value = value
        self.visual.set_mood(value)
        self.label.setText(self.describe_mood(value))

    def describe_mood(self, value):
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
