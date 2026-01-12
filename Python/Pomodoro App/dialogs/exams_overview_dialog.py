from collections import defaultdict

from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QDialog, QCalendarWidget, QListWidget, QListWidgetItem,
    QHBoxLayout, QVBoxLayout, QDialogButtonBox, QMenu
)


class ExamsOverviewDialog(QDialog):
    exams_updated = Signal(list)

    def __init__(self, exams, parent=None):
        super().__init__(parent)
        self.setWindowTitle("All Exams")
        self.resize(520, 420)

        self.exams = list(exams)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)

        self.list = QListWidget(self)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._on_ctx_menu)

        h = QHBoxLayout()
        h.addWidget(self.calendar, 1)
        h.addWidget(self.list, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        buttons.button(QDialogButtonBox.Close).clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addLayout(h)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self._populate_calendar_and_list()
        self.calendar.clicked.connect(self._on_calendar_clicked)
        self.list.itemClicked.connect(self._on_list_clicked)

    def _fmt_days_left(self, qd: QDate):
        today = QDate.currentDate()
        diff = today.daysTo(qd)
        if diff == 0:
            return "today"
        if diff == 1:
            return "in 1 day"

        if diff >= 2 and diff <= 7:
            return f"in {diff} days - LOCK IN JUNGE ES WIRD ERNST"
        if diff >= 8 and diff <= 14:
            return f"in {diff} days - ZIEH DURCH"
        if diff >= 15 and diff <= 29:
            return f"in {diff} days - Unter einen Monat, Get to work"
        if diff >= 30:
            return f"in {diff} days - Calm, behalte alles im Blick !!"

        diff = qd.daysTo(today)
        if diff == 1:
            return "1 day ago"
        return f"{diff} days ago"

    def _populate_calendar_and_list(self):
        self.list.clear()

        # reset formatting
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        grouped = defaultdict(list)
        for ex in self.exams:
            try:
                y, m, d = map(int, ex["date"].split("-"))
                qd = QDate(y, m, d)
            except Exception:
                continue
            grouped[qd].append(ex["name"])

        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)

        for qd in grouped.keys():
            self.calendar.setDateTextFormat(qd, fmt)

        items_by_date = []
        for qd in sorted(grouped.keys()):
            for name in grouped[qd]:
                items_by_date.append((qd, name))

        for qd, name in items_by_date:
            when = qd.toString("dd.MM.yyyy")
            tail = self._fmt_days_left(qd)
            text = f"{when} — {name}  ({tail})"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, qd)
            item.setData(Qt.UserRole + 1, name)
            self.list.addItem(item)

        today = QDate.currentDate()
        target = None
        future = [qd for qd in sorted(grouped.keys()) if qd >= today]
        if future:
            target = future[0]
        elif items_by_date:
            target = items_by_date[-1][0]

        if target:
            self.calendar.setSelectedDate(target)
            self.calendar.setCurrentPage(target.year(), target.month())
            for i in range(self.list.count()):
                it = self.list.item(i)
                if it.data(Qt.UserRole) == target:
                    self.list.setCurrentItem(it)
                    break

    def _on_calendar_clicked(self, qdate: QDate):
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(Qt.UserRole) == qdate:
                self.list.setCurrentItem(it)
                break

    def _on_list_clicked(self, item: QListWidgetItem):
        qd = item.data(Qt.UserRole)
        if isinstance(qd, QDate):
            self.calendar.setSelectedDate(qd)
            self.calendar.setCurrentPage(qd.year(), qd.month())

    def _on_ctx_menu(self, pos):
        item = self.list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        act_del = menu.addAction("Delete")
        action = menu.exec(self.list.mapToGlobal(pos))

        if action == act_del:
            qd = item.data(Qt.UserRole)
            name = item.data(Qt.UserRole + 1)
            iso = qd.toString("yyyy-MM-dd")
            self.exams = [
                ex for ex in self.exams
                if not (ex.get("name") == name and ex.get("date") == iso)
            ]
            self.exams_updated.emit(self.exams)
            self._populate_calendar_and_list()
