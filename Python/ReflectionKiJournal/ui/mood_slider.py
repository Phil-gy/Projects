from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCharts import QChart, QLineSeries, QChartView, QValueAxis
from PySide6.QtCore import QMargins

from .mood_visual import MoodVisual
from ..data_manager import load_entries


class MoodSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.mood_value = 0  # -100 (bad) → 100 (good)

        # Label above slider
        self.label = QLabel("Neutral", alignment=Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        # Mood slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-100, 100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.update_mood)

        # Gradient style for slider groove
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

        # Animated mood orb
        self.visual = MoodVisual()
        self.visual.setMinimumHeight(150)

        # Create chart
        self.chart_view = self.create_mood_chart()

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 10)
        layout.addWidget(self.visual, stretch=2)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        if self.chart_view:
            layout.addWidget(self.chart_view)
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

    def create_mood_chart(self):
        """Create a compact mood history chart for the last 7 days."""
        entries = load_entries()
        if not entries:
            return None

        # Sort by date and keep the last 7 entries
        sorted_items = sorted(entries.items())[-7:]

        series = QLineSeries()
        for i, (day, entry) in enumerate(sorted_items):
            y = entry.get("mood", 0)
            series.append(i, y)  # use index instead of len()

        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.legend().hide()
        chart.setBackgroundBrush(Qt.transparent)
        chart.setContentsMargins(10, 0, 10, 0)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setPlotAreaBackgroundVisible(False)

        # Y-axis (mood level)
        axis_y = QValueAxis()
        axis_y.setRange(-100, 100)
        axis_y.setTickCount(5)
        axis_y.setTitleText("Mood Level")
        axis_y.setLabelsColor(Qt.white)
        axis_y.setTitleBrush(QColor("white"))
        axis_y.setGridLineColor(QColor(100, 100, 100))

        # X-axis (hidden, since it's just last 7 days)
        axis_x = QValueAxis()
        axis_x.setRange(0, len(sorted_items) - 1)
        axis_x.setVisible(False)

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        # Line style
        pen = series.pen()
        pen.setColor(QColor(0, 255, 255, 200))
        pen.setWidth(3)
        series.setPen(pen)
        series.setBrush(QColor(0, 255, 255, 60))

        # Chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(160)
        chart_view.setStyleSheet("""
            QChartView {
                background: transparent;
                border: none;
            }
        """)

        return chart_view
