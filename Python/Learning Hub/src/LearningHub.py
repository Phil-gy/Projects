import sys, random, webbrowser, json
from functools import partial
from collections import defaultdict
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QDialog, QDialogButtonBox, QLineEdit, QDateEdit, QFormLayout,
    QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, QDate, QSettings, Signal
from PySide6.QtGui import QTextCharFormat, QFont


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


class ExamsOverviewDialog(QDialog):
    exams_updated = Signal(list)

    def __init__(self, exams, parent=None):
        super().__init__(parent)
        self.setWindowTitle("All Exams")
        self.resize(520, 420)

        self.exams = list(exams)  

        from PySide6.QtWidgets import QCalendarWidget
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
        if diff > 1:
            return f"in {diff} days"

        diff = qd.daysTo(today)
        if diff == 1:
            return "1 day ago"
        return f"{diff} days ago"

    def _populate_calendar_and_list(self):
        self.list.clear()

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
            self.exams = [ex for ex in self.exams if not (ex.get("name") == name and ex.get("date") == iso)]
            self.exams_updated.emit(self.exams)
            self._populate_calendar_and_list()


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

        self.settings = QSettings("LearningHub", "StudyApp")  

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
        self.todoist = QPushButton("Todoist")
        self.AddExam = QPushButton("Add Exam")
        self.ViewExams = QPushButton("View Exams") 
        self.close_btn = QPushButton("Close App")

        self.close_btn.setStyleSheet("""
            background-color: #b91c1c;   /* red */
            color: #ffffff;
            border: 1px solid #ef4444;
            border-radius: 10px;
            """)

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
        layout.addWidget(self.todoist)
        layout.addWidget(self.AddExam)
        layout.addWidget(self.ViewExams)   
        layout.addWidget(self.close_btn)
        layout.addSpacing(6)
        layout.addWidget(self.next_exam_label)  
        self.setLayout(layout)

        self.close_btn.clicked.connect(self.close)
        self.pomodoro_rain50.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=Je0WXbgrWtQ"))
        self.pomodoro_rain25.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=KcsUCEAG9Q8"))
        self.River_Rain.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=y9yhdPuP8QE"))
        self.River_Thunder.clicked.connect(partial(self.open_link, "https://www.youtube.com/watch?v=coU3dfhYSZ0"))
        self.Entspannte_Musik.clicked.connect(partial(self.open_link, "https://open.spotify.com/playlist/76t3u3MWoKGMD4Mkw2yq3r?si=856149b4afcd4dd1"))
        self.Mareux.clicked.connect(partial(self.open_link, "https://open.spotify.com/playlist/2IKeogGKce4bsccrruSEvX?si=95228b72643f4ec2"))
        self.pomodoroSite.clicked.connect(partial(self.open_link, "https://pomofocus.io/"))
        self.todoist.clicked.connect(partial(self.open_link, "https://app.todoist.com/app/inbox"))
        self.AddExam.clicked.connect(self.add_exam)
        self.ViewExams.clicked.connect(self.view_exams) 

        # Data
        self.exams = self.load_exams()  

        # Startup
        self.show_random_quote()
        self.update_next_exam_label()
    
    def center_window(self):
        screen = self.screen() or QApplication.primaryScreen()
        geo = screen.availableGeometry()
        center = geo.center()
        frame = self.frameGeometry()
        frame.moveCenter(center)
        self.move(frame.topLeft())

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
            self.exams.sort(key=lambda x: x["date"])
            self.save_exams()
            self.update_next_exam_label()

    def view_exams(self):
        dlg = ExamsOverviewDialog(self.exams, self)
        dlg.exams_updated.connect(self._on_exams_updated)
        dlg.exec()

    def _on_exams_updated(self, exams):
        self.exams = exams
        self.exams.sort(key=lambda x: x["date"])
        self.save_exams()
        self.update_next_exam_label()

    def update_next_exam_label(self):
        if not self.exams:
            self.next_exam_label.setText("No exams saved. Add one to start your countdown.")
            return

        today = QDate.currentDate()
        upcoming = None
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
    window.center_window()
    sys.exit(app.exec())
