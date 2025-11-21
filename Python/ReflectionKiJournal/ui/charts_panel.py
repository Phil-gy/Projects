# ui/charts_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


DARK_BG = "#151521"    
AX_BG   = "#1b1b2b"    
GRID    = "#3a3a4a"
LINE    = "#40e0d0"    
TICK    = "#dddddd"
LABEL   = "#ffffff"


class ChartsPanel(QWidget):
    def __init__(self, sentiments):
        """
        sentiments: list of (label, value), where value is -100..100
        """
        super().__init__()
        self.sentiments = sentiments or []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.figure = Figure(figsize=(4, 1.5), tight_layout=True)
        self.figure.patch.set_facecolor(DARK_BG)

        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet(f"background-color: {DARK_BG}; border: none;")

        layout.addWidget(self.canvas)
        self.setMinimumHeight(140)

        self.plot_sentiment_trend()

    def update_sentiments(self, sentiments):
        """Call this when entries/moods change."""
        self.sentiments = sentiments or []
        self.plot_sentiment_trend()

    def plot_sentiment_trend(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.set_facecolor(AX_BG)

        if not self.sentiments:
            ax.text(
                0.5, 0.5,
                "Noch keine Stimmungsdaten",
                ha="center", va="center",
                color=LABEL, fontsize=9,
                transform=ax.transAxes,
            )
            ax.set_axis_off()
        else:
            labels = [d for d, _ in self.sentiments]
            values = [v for _, v in self.sentiments]

            ax.plot(
                values,
                marker="o",
                linewidth=1.8,
                markersize=5,
                color=LINE,
            )

            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=0, fontsize=8, color=TICK)

            ax.set_ylabel("Mood", color=LABEL, fontsize=9)
            ax.set_ylim(-100, 100)
            ax.grid(color=GRID, alpha=0.5, linewidth=0.7)

            for spine in ax.spines.values():
                spine.set_color(GRID)

            ax.tick_params(colors=TICK, labelsize=8)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        self.canvas.draw_idle()
