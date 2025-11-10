from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from datetime import date
from ..data_manager import load_entries, save_entries
from .mood_slider import MoodSlider
from ..summarizer import summarize_last_week


class EditorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QTextEdit()
        self.save_button = QPushButton("Save Entry")
        self.save_button.clicked.connect(self.save_current_entry)
        self.mood_slider = MoodSlider()
        self.summarize_button = QPushButton("🧠 Summarize My Week")
        self.summarize_button.clicked.connect(self.generate_summary)


        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.mood_slider)
        layout.addWidget(self.save_button)
        layout.addWidget(self.summarize_button)
        self.setLayout(layout)

        self.current_date = None
        self.entries = {}

    def load_entry(self, iso_date: str):
        """Load an entry when user clicks on a date in sidebar."""
        self.current_date = iso_date
        self.entries = load_entries()

        entry = self.entries.get(iso_date, {})
        self.text.setText(entry.get("text", ""))
        self.mood_slider.slider.setValue(entry.get("mood", 0))

    def save_current_entry(self):
        """Save current text and mood to entries.json."""
        if not self.current_date:
            self.current_date = date.today().isoformat()

        text_content = self.text.toPlainText().strip()
        mood_value = self.mood_slider.mood_value

        entries = load_entries()
        entries[self.current_date] = {
            "text": text_content,
            "mood": mood_value
        }
        save_entries(entries)
        print(f"Saved entry for {self.current_date} (mood={mood_value})")

    def generate_summary(self):
        """Generate a weekly reflection summary and save it."""
        result = summarize_last_week()
        if isinstance(result, tuple):
            summary_id, summary_text = result
            self.text.setText(summary_text)
            print(f"✅ Weekly summary added as {summary_id}")
        else:
            self.text.setText(result)