import sys, random, webbrowser, json
from functools import partial
from collections import defaultdict
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QDialog, QDialogButtonBox, QLineEdit, QDateEdit, QFormLayout,
    QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QSettings
from PySide6.QtGui import QTextCharFormat, QFont


# ---------- Dialog to add a single exam ----------
class ExamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Exam")

        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("e.g., Stochastik")
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        form = QFormLayout()
        form.addRow("Exam name:", self.name_edit)
        form.addRow("Date:", self.date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        name = self.name_edit.text().strip()
        date = self.date_edit.date()
        return name, date


# ---------- Dialog to view all exams in calendar + list ----------
class ExamsOverviewDialog(QDialog):
    def __init__(self, exams, parent=None):
        super().__init__(parent)
        self.setWindowTitle("All Exams")
        self.resize(520, 420)

        self.exams = list(exams)  # list of {"name": str, "date": "YYYY-MM-DD"}

        from PySide6.QtWidgets import QCalendarWidget
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)

        self.list = QListWidget(self)

        # Layout: Calendar left, list right
        h = QHBoxLayout()
        h.addWidget(self.calendar, 1)
        h.addWidget(self.list, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)  # not shown, but harmless
        buttons.button(QDialogButtonBox.Close).clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addLayout(h)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # Populate calendar + list
        self._populate_calendar_and_list()

        # Wire interactions
        self.calendar.clicked.connect(self._on_calendar_clicked)
        self.list.itemClicked.connect(self._on_list_clicked)

    def _fmt_days_left(self, qd: QDate):
        today = QDate.currentDate()
        diff = today.daysTo(qd)
        if diff == 0:
            return "today"
        if diff == 1:
            return "in 1 day"
        if diff > 1:
            return f"in {diff} days"
        # past
        diff = qd.daysTo(today)
        if diff == 1:
            return "1 day ago"
        return f"{diff} days ago"

    def _populate_calendar_and_list(self):
        self.list.clear()
        # clear any previous formats
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        # group exams by date
        grouped = defaultdict(list)
        for ex in self.exams:
            try:
                y, m, d = map(int, ex["date"].split("-"))
                qd = QDate(y, m, d)
            except Exception:
                continue
            grouped[qd].append(ex["name"])

        # highlight dates
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        # (No explicit colors; uses theme. Add colors if you want.)
        for qd in grouped.keys():
            self.calendar.setDateTextFormat(qd, fmt)

        # populate list (sorted by date)
        items_by_date = []
        for qd in sorted(grouped.keys()):
            for name in grouped[qd]:
                items_by_date.append((qd, name))

        for qd, name in items_by_date:
            when = qd.toString("dd.MM.yyyy")
            tail = self._fmt_days_left(qd)
            text = f"{when} — {name}  ({tail})"
            item = QListWidgetItem(text)
            # store date for selection sync
            item.setData(Qt.UserRole, qd)
            self.list.addItem(item)

        # jump calendar to next upcoming (or last if all past)
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
            # also select first matching list item
            for i in range(self.list.count()):
                it = self.list.item(i)
                if it.data(Qt.UserRole) == target:
                    self.list.setCurrentItem(it)
                    break

    def _on_calendar_clicked(self, qdate: QDate):
        # select first list item with this date
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


# ---------- Main App ----------
class LearningHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Learning Hub")
        self.setGeometry(400, 400, 420, 560)

        self.setStyleSheet("""
            QWidget { background-color: #13161a; color: #E6EDF3; font-size: 14px; }
            QLabel#Hint  { color: #9aa4af; font-size: 12px; }
            QLabel { padding: 2px 4px; }
            QPushButton {
                background: #21262d; border: 1px solid #30363d; border-radius: 10px;
                padding: 10px 14px; font-weight: 600;
            }
            QPushButton:hover   { background: #2a3139; }
            QPushButton:pressed { background: #1d2228; }
        """)

        # persistent store
        self.settings = QSettings("LearningHub", "StudyApp")  # org/app ids

        self.quotes = [
            "Leg dein Handy Weg",
            "You got this ! Dont stop now !!!!",
            "You dont need more time—you need more focus.",
            "Lern gut, sonst 14 Semester Regelstudienzeit !",
            "3 Versuch !!!",
            "Straff dich !",
            "LOCK IN ! Your future depends on today !",
        ]

        # UI
        self.quote = QLabel("", self)
        self.quote.setAlignment(Qt.AlignCenter)
        self.quote.setWordWrap(True)
        self.quote.setStyleSheet("font-size:18px; padding:12px;")

        self.pomodoro_rain50 = QPushButton("Pomodoro Rain 50/10")
        self.pomodoro_rain25 = QPushButton("Pomodoro Rain 25/5")
        self.River_Rain = QPushButton("River + Rain")
        self.River_Thunder = QPushButton("River + Thunder")
        self.Entspannte_Musik = QPushButton("Entspannte Musik")
        self.Mareux = QPushButton("Mareux Music")
        self.pomodoroSite = QPushButton("Pomodoro Site")
        self.AddExam = QPushButton("Add Exam")
        self.ViewExams = QPushButton("View Exams")  # NEW
        self.close_btn = QPushButton("Close App")

        # footer for next exam
        self.next_exam_label = QLabel("", self)
        self.next_exam_label.setAlignment(Qt.AlignCenter)
        self.next_exam_label.setStyleSheet(
            "font-size: 16px; padding: 10px; color: #c8d1da;"
        )

        layout = QVBoxLayout()
        layout.addWidget(self.quote)
        layout.addSpacing(10)
        layout.addWidget(self.pomodoro_rain50)
        layout.addWidget(self.pomodoro_rain25)
        layout.addWidget(self.River_Rain)
        layout.addWidget(self.River_Thunder)
        layout.addWidget(self.Entspannte_Musik)
        layout.addWidget(self.Mareux)
        layout.addWidget(self.pomodoroSite)
        layout.addWidget(self.AddExam)
        layout.addWidget(self.ViewExams)   # NEW
        layout.addWidget(self.close_btn)
        layout.addSpacing(6)
        layout.addWidget(self.next_exam_label)  # always at bottom
        self.setLayout(layout)

        # Connections
        self.close_btn.clicked.connect(self.close)
        self.pomodoro_rain50.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=Je0WXbgrWtQ"))
        self.pomodoro_rain25.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=KcsUCEAG9Q8"))
        self.River_Rain.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=y9yhdPuP8QE"))
        self.River_Thunder.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=coU3dfhYSZ0"))
        self.Entspannte_Musik.clicked.connect(partial(self.open_link, "https://open.spotify.com/playlist/76t3u3MWoKGMD4Mkw2yq3r?si=856149b4afcd4dd1"))
        self.Mareux.clicked.connect(partial(self.open_link, "https://open.spotify.com/playlist/2IKeogGKce4bsccrruSEvX?si=95228b72643f4ec2"))
        self.pomodoroSite.clicked.connect(partial(self.open_link, "https://pomofocus.io/"))
        self.AddExam.clicked.connect(self.add_exam)
        self.ViewExams.clicked.connect(self.view_exams)  # NEW

        # Data
        self.exams = self.load_exams()  # list of {"name": str, "date": "YYYY-MM-DD"}

        # Startup
        self.show_random_quote()
        self.update_next_exam_label()

    # ---------- persistence ----------
    def load_exams(self):
        raw = self.settings.value("exams_json", "")
        if not raw:
            return []
        try:
            data = json.loads(raw)
            out = []
            for item in data:
                if isinstance(item, dict) and "name" in item and "date" in item:
                    out.append(item)
            return out
        except Exception:
            return []

    def save_exams(self):
        self.settings.setValue("exams_json", json.dumps(self.exams, ensure_ascii=False))

    # ---------- helpers ----------
    def show_random_quote(self):
        self.quote.setText(random.choice(self.quotes))

    def open_link(self, url: str):
        webbrowser.open(url)

    def add_exam(self):
        dlg = ExamDialog(self)
        if dlg.exec() == QDialog.Accepted:
            name, qdate = dlg.get_data()
            if not name:
                QMessageBox.warning(self, "Invalid", "Exam name cannot be empty.")
                return
            iso = qdate.toString("yyyy-MM-dd")
            self.exams.append({"name": name, "date": iso})
            # keep exams sorted by date ascending
            self.exams.sort(key=lambda x: x["date"])
            self.save_exams()
            self.update_next_exam_label()

    def view_exams(self):
        # Open the overview dialog with the current list
        dlg = ExamsOverviewDialog(self.exams, self)
        dlg.exec()

    def update_next_exam_label(self):
        if not self.exams:
            self.next_exam_label.setText("No exams saved. Add one to start your countdown.")
            return

        today = QDate.currentDate()
        upcoming = None
        # ensure sorted
        self.exams.sort(key=lambda x: x["date"])
        for ex in self.exams:
            try:
                y, m, d = map(int, ex["date"].split("-"))
                qd = QDate(y, m, d)
            except Exception:
                continue
            if qd >= today:
                upcoming = (ex["name"], qd)
                break

        if upcoming is None:
            # all in the past -> show most recent past with days overdue
            last = max(self.exams, key=lambda x: x["date"])
            y, m, d = map(int, last["date"].split("-"))
            qd = QDate(y, m, d)
            days = qd.daysTo(today)
            self.next_exam_label.setText(
                f"Last exam '{last['name']}' was on {qd.toString('dd.MM.yyyy')} — {days} day(s) ago."
            )
            return

        name, date = upcoming
        days_left = today.daysTo(date)
        if days_left == 0:
            msg = f"Next exam: '{name}' is TODAY ({date.toString('dd.MM.yyyy')}) — LOCK IN."
        elif days_left == 1:
            msg = f"Next exam: '{name}' in 1 day — {date.toString('dd.MM.yyyy')}."
        else:
            msg = f"Next exam: '{name}' in {days_left} days — {date.toString('dd.MM.yyyy')}."
        self.next_exam_label.setText(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LearningHub()
    window.show()
    sys.exit(app.exec())
