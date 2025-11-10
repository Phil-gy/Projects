from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt
from datetime import date, datetime
from ..data_manager import load_entries, save_entries



class Sidebar(QWidget):
    entry_selected = Signal(str)  # emits ISO date (e.g. "2025-11-10")

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

        self.display_to_iso = {}
        self.refresh_list()
        self.list.itemClicked.connect(self.on_item_clicked)

        # Internal mapping: display text -> ISO key
       

    def refresh_list(self):
        """Reload the list of entries from the JSON file."""
        self.list.clear()
        entries = load_entries()
        if entries:
            for d in sorted(entries.keys(), reverse=True):
                # detect AI-generated summaries
                if d.startswith("summary-"):
                    label = f"🧠 Weekly Summary ({d[8:]})"
                else:
                    label = d
                self.list.addItem(label)
        else:
            self.list.addItem("No entries yet.")


    def add_today_entry(self):
        """Add an entry for today's date if it doesn't exist."""
        today_iso = date.today().isoformat()  # 'YYYY-MM-DD'
        entries = load_entries()

        if today_iso not in entries:
            entries[today_iso] = {"text": ""}
            save_entries(entries)
            self.refresh_list()

        today_german = date.today().strftime("%d.%m.%Y")
        items = self.list.findItems(today_german, Qt.MatchExactly)
        if items:
            self.list.setCurrentItem(items[0])
            self.entry_selected.emit(today_iso)

    def delete_current_entry(self):
        """Delete the currently selected entry."""
        current_item = self.list.currentItem()
        if not current_item:
            return

        german_str = current_item.text()
        if german_str in self.display_to_iso:
            iso_date = self.display_to_iso[german_str]
            entries = load_entries()
            if iso_date in entries:
                del entries[iso_date]
                save_entries(entries)
                self.refresh_list()

    def refresh_list(self):
        """Reload the list of entries from the JSON file."""
        self.list.clear()
        self.display_to_iso = {}

        entries = load_entries()
        if entries:
            for iso_date in sorted(entries.keys(), reverse=True):
                # Convert from ISO → German for display
                german_date = datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d.%m.%Y")
                self.display_to_iso[german_date] = iso_date
                self.list.addItem(german_date)
        else:
            self.list.addItem("Keine Einträge vorhanden.")

    def on_item_clicked(self, item):
        """Emit the ISO date string when a list item is clicked."""
        german_str = item.text()
        iso_date = self.display_to_iso.get(german_str)
        if iso_date:
            self.entry_selected.emit(iso_date)

