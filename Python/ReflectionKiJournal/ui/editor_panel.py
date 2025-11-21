from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PySide6.QtCore import Signal
from datetime import date, datetime
from data_manager import load_entries, save_entries
from .mood_slider import MoodSlider
from summarizer import summarize_last_week
from .charts_panel import ChartsPanel


class EditorPanel(QWidget):
    # emitted whenever entries.json changes (save or summary)
    entries_changed = Signal()

    def __init__(self):
        super().__init__()

        # widgets
        self.text = QTextEdit()
        self.mood_slider = MoodSlider()

        self.save_button = QPushButton("Save Entry")
        self.save_button.clicked.connect(self.save_current_entry)

        self.summarize_button = QPushButton("🧠 Summarize My Week")
        self.summarize_button.clicked.connect(self.generate_summary)

        # chart for last 7 days
        self.charts_panel = ChartsPanel(
            sentiments=self.compute_week_sentiments()
        )

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.mood_slider)
        layout.addWidget(self.charts_panel)      # chart under slider
        layout.addWidget(self.save_button)
        layout.addWidget(self.summarize_button)
        self.setLayout(layout)

        # state
        self.current_date = None   # ISO "YYYY-MM-DD"
        self.entries = {}

    # ---------------- load/save ----------------

    def load_entry(self, date_str: str):
        """Load an entry when user clicks a date in the sidebar."""
        self.current_date = date_str
        self.entries = load_entries()

        entry = self.entries.get(date_str, {})
        self.text.setText(entry.get("text", ""))
        self.mood_slider.slider.setValue(entry.get("mood", 0))

        # refresh chart when switching day
        self.charts_panel.update_sentiments(self.compute_week_sentiments())

    def save_current_entry(self):
        """Save current text + mood to entries.json."""
        if not self.current_date:
            self.current_date = date.today().isoformat()

        text_content = self.text.toPlainText().strip()
        mood_value = self.mood_slider.mood_value

        entries = load_entries()
        entries[self.current_date] = {
            "text": text_content,
            "mood": mood_value,
        }
        save_entries(entries)
        self.entries = entries

        # update chart AFTER saving
        self.charts_panel.update_sentiments(self.compute_week_sentiments())

        # tell the rest of the app (sidebar) that entries changed
        self.entries_changed.emit()

        print(f"Saved entry for {self.current_date} (mood={mood_value})")

    # ---------------- AI summary ----------------

    def generate_summary(self):
        """Generate a weekly reflection summary and save it."""
        result = summarize_last_week()
        if isinstance(result, tuple):
            summary_id, summary_text = result
            self.text.setText(summary_text)
            print(f"✅ Weekly summary added as {summary_id}")
        else:
            self.text.setText(result)

        # entries.json was modified by summarizer → refresh sidebar & chart
        self.entries_changed.emit()
        self.charts_panel.update_sentiments(self.compute_week_sentiments())

    # ---------------- chart data ----------------

    def compute_week_sentiments(self):
        """
        Return list of (label, mood) for the last 7 days that have entries.
        Used by ChartsPanel.
        """
        entries = load_entries()
        if not entries:
            return []

        # only ISO dates, ignore keys like "summary-2025-11-11"
        iso_dates = [
            k for k in entries.keys()
            if len(k) == 10 and k[4] == "-" and k[7] == "-"
        ]
        if not iso_dates:
            return []

        # newest → oldest, keep last 7, then flip (oldest → newest)
        iso_dates_sorted = sorted(iso_dates, reverse=True)
        last7 = list(reversed(iso_dates_sorted[:7]))

        result = []
        for iso in last7:
            entry = entries.get(iso, {})
            mood = entry.get("mood", 0)

            try:
                dt = datetime.strptime(iso, "%Y-%m-%d")
                label = dt.strftime("%d.%m.")  # e.g. "10.11."
            except ValueError:
                label = iso

            result.append((label, mood))

        return result
