from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt
from datetime import date, datetime
from ..data_manager import load_entries, save_entries


class Sidebar(QWidget):
    entry_selected = Signal(str)  # emits the JSON key (e.g. "2025-11-10" or "summary-2025-11-11")

    def __init__(self):
        super().__init__()

        self.list = QListWidget()

        self.add_button = QPushButton("➕ Neuer Eintrag (Heute)")
        self.add_button.clicked.connect(self.add_today_entry)

        self.delete_button = QPushButton("🗑️ Eintrag löschen")
        self.delete_button.clicked.connect(self.delete_current_entry)

        layout = QVBoxLayout()
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.list)
        self.setLayout(layout)

        # mapping: display text → JSON key (so we can delete/load correctly)
        self.display_to_key = {}

        self.refresh_list()
        self.list.itemClicked.connect(self.on_item_clicked)

    def refresh_list(self):
        """Reload all entries from JSON and populate the sidebar."""
        self.list.clear()
        self.display_to_key.clear()

        entries = load_entries()
        if not entries:
            self.list.addItem("Keine Einträge vorhanden.")
            return

        # sort newest first
        for key in sorted(entries.keys(), reverse=True):
            # --- Case 1: AI weekly summary ---
            if key.startswith("summary-"):
                date_str = key.replace("summary-", "")
                display_text = f"🧠 Weekly Summary ({date_str})"
                self.display_to_key[display_text] = key
                self.list.addItem(display_text)

            # --- Case 2: normal daily entry ---
            else:
                try:
                    german_date = datetime.strptime(key, "%Y-%m-%d").strftime("%d.%m.%Y")
                except ValueError:
                    # fallback if somehow malformed
                    german_date = key
                self.display_to_key[german_date] = key
                self.list.addItem(german_date)

    def add_today_entry(self):
        """Add an entry for today's date if it doesn't exist."""
        today_iso = date.today().isoformat()
        entries = load_entries()

        if today_iso not in entries:
            entries[today_iso] = {"text": "", "mood": 0}
            save_entries(entries)
            self.refresh_list()

        # select today's entry automatically
        today_german = date.today().strftime("%d.%m.%Y")
        for i in range(self.list.count()):
            if self.list.item(i).text() == today_german:
                self.list.setCurrentRow(i)
                self.entry_selected.emit(today_iso)
                break

    def delete_current_entry(self):
        """Delete whichever entry is currently selected."""
        current_item = self.list.currentItem()
        if not current_item:
            return

        display_text = current_item.text()
        key = self.display_to_key.get(display_text)
        if not key:
            return

        entries = load_entries()
        if key in entries:
            del entries[key]
            save_entries(entries)
            self.refresh_list()

    def on_item_clicked(self, item):
        """Emit the proper key (ISO date or summary ID) when clicked."""
        display_text = item.text()
        key = self.display_to_key.get(display_text)
        if key:
            self.entry_selected.emit(key)
