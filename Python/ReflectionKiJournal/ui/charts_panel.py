# ui/charts_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ChartsPanel(QWidget):
    def __init__(self, sentiments):
        super().__init__()
        self.sentiments = sentiments  # e.g., list of (date, polarity)
        layout = QVBoxLayout()

        # Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_sentiment_trend()

    def plot_sentiment_trend(self):
        ax = self.figure.add_subplot(111)
        ax.clear()

        dates = [d for d, _ in self.sentiments]
        moods = [s for _, s in self.sentiments]
        ax.plot(dates, moods, marker="o")
        ax.set_title("Mood over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sentiment Score (-1 to 1)")
        self.canvas.draw()
