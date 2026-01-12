from PySide6.QtCore import QTimer, Qt, QDate, QSettings
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QVBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QMessageBox
)

from dialogs.exam_dialog import ExamDialog
from dialogs.exams_overview_dialog import ExamsOverviewDialog
from dialogs.information_popup import InformationPopUp
from utils.exams_storage import load_exams, save_exams


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Philipps Pomodoro Timer")
        self.resize(540, 440)

        self.settings = QSettings("Philipp", "PomodoroTimer")
        self.exams = load_exams(self.settings)

        self.work_duration = 60 * 60
        self.break_duration = 5 * 60
        self.is_work_mode = True
        self.counter = self.work_duration

       
        self.header = QLabel("🍅 Philipp’s Pomodoro")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFont(QFont("Segoe UI", 20, QFont.Bold))

        self.label = QLabel(self.format_time(self.counter))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Consolas", 72, QFont.Bold))

        self.next_exam_label = QLabel("", self)
        self.next_exam_label.setAlignment(Qt.AlignCenter)
        self.next_exam_label.setStyleSheet("font-size: 16px; padding: 10px; color: #c8d1da;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor("#111111"))
        self.label.setGraphicsEffect(shadow)

        self.choose_time = QPushButton("Choose time Interval")
        self.choose_time.setCursor(Qt.PointingHandCursor)
        self.choose_time.clicked.connect(self.choose_time_interval)

        self.button = QPushButton("▶ Start")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.clicked.connect(self.start_timer)

        self.add_exam_btn = QPushButton("➕ Add exam")
        self.add_exam_btn.setCursor(Qt.PointingHandCursor)
        self.add_exam_btn.clicked.connect(self.add_exam)

        self.view_exams_btn = QPushButton("📅 View exams")
        self.view_exams_btn.setCursor(Qt.PointingHandCursor)
        self.view_exams_btn.clicked.connect(self.view_exams)

        layout = QVBoxLayout()
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(18)
        layout.addWidget(self.header)
        layout.addWidget(self.label)
        layout.addWidget(self.next_exam_label)
        layout.addWidget(self.add_exam_btn)
        layout.addWidget(self.view_exams_btn)
        layout.addWidget(self.choose_time)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)

        frame = QFrame()
        frame.setLayout(layout)
        frame.setObjectName("MainFrame")
        self.setCentralWidget(frame)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.update_next_exam_label()
        self.set_theme("work")

    def format_time(self, total_seconds: int) -> str:
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(1000)
            self.button.setText("⏸ Stop")
        else:
            self.timer.stop()
            self.button.setText("▶ Start")

    def update_timer(self):
        if self.counter > 0:
            self.counter -= 1
            self.label.setText(self.format_time(self.counter))
            return

        self.timer.stop()

        if self.is_work_mode:
            dlg = InformationPopUp(self.is_work_mode, self)
            dlg.exec()
            self.is_work_mode = False
            self.counter = self.break_duration
            self.label.setText("Break Time ☕")
            self.set_theme("break")
        else:
            dlg = InformationPopUp(self.is_work_mode, self)
            dlg.exec()
            self.is_work_mode = True
            self.counter = self.work_duration
            self.label.setText("Back to Work 💪")
            self.set_theme("work")

        self.button.setText("▶ Start")

    def choose_time_interval(self):
        if self.work_duration == 25 * 60:
            self.work_duration = 60 * 60
        else:
            self.work_duration = 25 * 60

        if self.is_work_mode:
            self.counter = self.work_duration
            self.label.setText(self.format_time(self.counter))

        if self.work_duration == 25 * 60:
            self.choose_time.setText("Set to 60 min (Click to switch back)")
        else:
            self.choose_time.setText("Set to 25 min (Click to switch back)")

    def set_theme(self, mode: str):
        if mode == "work":
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #27293d, stop:1 #3b3b58);"
            accent = "#f06292"
        else:
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1b5e20, stop:1 #2e7d32);"
            accent = "#c8e6c9"

        self.setStyleSheet(f"""
            QMainWindow {{
                background: {bg_gradient};
            }}
            QLabel {{
                color: {accent};
            }}
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.08);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
                padding: 12px 30px;
                font-size: 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.18);
            }}
            QPushButton:pressed {{
               background-color: rgba(255, 255, 255, 0.25);
            }}
        """)

    # -------------------- Exams --------------------

    def add_exam(self):
        dlg = ExamDialog(self)
        if dlg.exec() == dlg.Accepted:
            name, qdate = dlg.get_data()
            if not name:
                QMessageBox.warning(self, "Invalid", "Exam name cannot be empty.")
                return

            iso = qdate.toString("yyyy-MM-dd")
            self.exams.append({"name": name, "date": iso})
            self.exams.sort(key=lambda x: x["date"])
            save_exams(self.settings, self.exams)
            self.update_next_exam_label()

    def view_exams(self):
        dlg = ExamsOverviewDialog(self.exams, self)
        dlg.exams_updated.connect(self._on_exams_updated)
        dlg.exec()

    def _on_exams_updated(self, exams):
        self.exams = list(exams)
        self.exams.sort(key=lambda x: x["date"])
        save_exams(self.settings, self.exams)
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
