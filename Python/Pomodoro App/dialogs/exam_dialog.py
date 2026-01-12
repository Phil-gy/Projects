from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QLineEdit, QDateEdit, QFormLayout, QDialogButtonBox, QVBoxLayout
)


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
