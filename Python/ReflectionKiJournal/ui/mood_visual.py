import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPainter, QColor, QPainterPath, Qt


DARK_BG = QColor(5, 5, 20)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
    return QColor(
        int(lerp(c1.red(),   c2.red(),   t)),
        int(lerp(c1.green(), c2.green(), t)),
        int(lerp(c1.blue(),  c2.blue(),  t)),
        int(lerp(c1.alpha(), c2.alpha(), t)),
    )


class MoodVisual(QWidget):
    """
    Mood flower inspired by the Apple Health mental health slider:

    - mood in [-100, 100]
    - layered petal shapes
    - subtle breathing + slow rotation
    - smooth warm → neutral → cool color mapping
    """

    def __init__(self):
        super().__init__()

        self.mood = 0         
        self.phase = 0.0      
        self.rotation = 0.0   

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)  # ~33 FPS

        self.setMinimumHeight(160)

    def set_mood(self, value: int):
        self.mood = max(-100, min(100, value))
        self.update()


    def animate(self):
        self.phase += 0.04
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi

        self.rotation += 0.003
        if self.rotation > 2 * math.pi:
            self.rotation -= 2 * math.pi

        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        painter.fillRect(rect, DARK_BG)

        w = rect.width()
        h = rect.height()
        cx = rect.center().x()
        cy = rect.center().y()
        base_radius = min(w, h) * 0.22

        t = (self.mood + 100) / 200.0  
        neg = QColor(255, 140, 90)
        mid = QColor(190, 150, 255)
        pos = QColor(80, 220, 255)

        if t < 0.5:
            base_color = lerp_color(neg, mid, t * 2.0)
        else:
            base_color = lerp_color(mid, pos, (t - 0.5) * 2.0)

        petals = 7

    
        layers = [
            {"scale": 0.9, "amp": 0.18, "alpha": 210},
            {"scale": 1.4, "amp": 0.14, "alpha": 130},
            {"scale": 1.9, "amp": 0.10, "alpha": 70},
        ]

        painter.translate(cx, cy)
        painter.rotate(math.degrees(self.rotation))

        for i, layer in enumerate(layers):
            scale = layer["scale"]
            amp = layer["amp"]
            alpha = layer["alpha"]

            layer_phase = self.phase * (1.0 + 0.1 * i)

            path = QPainterPath()
            points = 120
            for k in range(points + 1):
                angle = 2 * math.pi * k / points

                r_mod = 1.0 + amp * math.sin(petals * angle + layer_phase)

                breathe = 1.0 + 0.03 * math.sin(self.phase + i * 0.7)

                r = base_radius * scale * r_mod * breathe
                x = r * math.cos(angle)
                y = r * math.sin(angle)

                if k == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)

            color = QColor(base_color)
            color.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawPath(path)

        core_radius = base_radius * 0.32 * (1.0 + 0.03 * math.sin(self.phase * 1.5))
        core_color = QColor(255, 255, 255, 230)
        painter.setBrush(core_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            -core_radius,
            -core_radius,
            core_radius * 2,
            core_radius * 2,
        )
