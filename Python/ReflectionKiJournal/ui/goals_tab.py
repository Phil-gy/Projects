from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt

from goal_manager import load_goals, save_goals


class GoalsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter a new goal...")
        self.input.returnPressed.connect(self.add_goal)

        self.add_button = QPushButton("➕ Add Goal")
        self.add_button.clicked.connect(self.add_goal)

        top_row = QHBoxLayout()
        top_row.addWidget(self.input)
        top_row.addWidget(self.add_button)

        self.list = QListWidget()
        self.list.itemChanged.connect(self.on_item_changed)
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setMinimumHeight(200)

        self.delete_button = QPushButton("🗑 Remove selected goal")
        self.delete_button.clicked.connect(self.delete_goal)

        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addWidget(self.list)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

        self.goals = load_goals() or []
        self.refresh_list()


    def refresh_list(self):
        """Rebuild list widget from self.goals."""
        self.list.blockSignals(True)
        self.list.clear()

        for goal in self.goals:
            text = goal.get("text", "")
            done = bool(goal.get("done", False))

            item = QListWidgetItem(text)
            item.setFlags(
                item.flags()
                | Qt.ItemIsUserCheckable
                | Qt.ItemIsSelectable
                | Qt.ItemIsEnabled
            )
            item.setCheckState(Qt.Checked if done else Qt.Unchecked)
            self.list.addItem(item)

        self.list.blockSignals(False)

    def add_goal(self):
        text = self.input.text().strip()
        if not text:
            return

        self.goals.append({"text": text, "done": False})
        save_goals(self.goals)

        self.input.clear()
        self.refresh_list()
        self.list.setCurrentRow(len(self.goals) - 1)

    def delete_goal(self):
        item = self.list.currentItem()
        if not item:
            return

        row = self.list.row(item)
        if row < 0 or row >= len(self.goals):
            return

        reply = QMessageBox.question(
            self,
            "Remove goal",
            f"Do you really want to remove this goal?\n\n{item.text()}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        del self.goals[row]
        save_goals(self.goals)
        self.refresh_list()

    def on_item_changed(self, item: QListWidgetItem):
        """Update 'done' state when user ticks/unticks a goal."""
        row = self.list.row(item)
        if row < 0 or row >= len(self.goals):
            return

        self.goals[row]["done"] = item.checkState() == Qt.Checked
        save_goals(self.goals)
