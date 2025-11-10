from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QRadialGradient
import math
from PySide6.QtCore import QTimer, Qt, Signal


class MoodVisual(QWidget):
    colorChanged = Signal(str)
    def __init__(self):
        super().__init__()
        self.mood = 0        # -100 to +100
        self.phase = 0       # animation phase
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)  # 30 ms → ~33 FPS

    def set_mood(self, value):
        self.mood = value
        # compute mood color (red→blue transition)
        ratio = (self.mood + 100) / 200.0
        r = int(255 * (1 - ratio))
        g = int(50 + 120 * ratio)
        b = int(255 * ratio)
        base_color = QColor(r, g, b)
        self.colorChanged.emit(base_color.name())  # emit hex string
        self.update()

    def animate(self):
        self.phase += 0.05
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(10, 10, 25))  # dark background

        # compute mood color (red→blue)
        ratio = (self.mood + 100) / 200.0
        r = int(255 * (1 - ratio))
        g = int(80 + 80 * ratio)
        b = int(255 * ratio)
        base_color = QColor(r, g, b)

        # subtle pulse radius
        width, height = self.width(), self.height()
        radius = min(width, height) / 3 * (1 + 0.05 * math.sin(self.phase))

        # radial gradient
        grad = QRadialGradient(width / 2, height / 2, radius)
        grad.setColorAt(0.0, base_color.lighter(150))
        grad.setColorAt(0.3, base_color)
        grad.setColorAt(1.0, QColor(10, 10, 25))

        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(width / 2 - radius, height / 2 - radius, radius * 2, radius * 2)
