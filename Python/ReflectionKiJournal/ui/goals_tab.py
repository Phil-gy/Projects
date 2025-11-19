from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit,
    QPushButton, QListWidgetItem, QCheckBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, Signal, QSize
from goal_manager import load_goals, save_goals



class GoalRow(QWidget):
    """
    A single goal row widget (checkbox + full-row click).
    Clicking anywhere on this widget toggles the checkbox.
    Emits toggled(goal_dict, checked_bool).
    """
    toggled = Signal(dict, bool)

    def __init__(self, goal: dict):
        super().__init__()
        self.goal = goal
        self.checkbox = QCheckBox(goal["text"])
        self.checkbox.setChecked(goal.get("done", False))
        self.checkbox.stateChanged.connect(self._on_state_changed)

        # Optional styling for completed goals
        if goal.get("done"):
            self.checkbox.setStyleSheet("text-decoration: line-through; color: #888;")
        else:
            self.checkbox.setStyleSheet("")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.addWidget(self.checkbox, 1, Qt.AlignVCenter)

    def _on_state_changed(self, state):
        checked = (state == Qt.Checked)
        # Update local appearance
        if checked:
            self.checkbox.setStyleSheet("text-decoration: line-through; color: #888;")
        else:
            self.checkbox.setStyleSheet("")
        self.toggled.emit(self.goal, checked)

    def mousePressEvent(self, event):
        # Toggle checkbox when clicking anywhere on the row
        self.checkbox.setChecked(not self.checkbox.isChecked())
        # Also pass the event up so QListWidget can select the item
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:
        return QSize(200, 34)


class GoalsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.goals = load_goals()

        self.list = QListWidget()
        self.list.setSpacing(2)
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setSelectionBehavior(QListWidget.SelectItems)
        self.list.setUniformItemSizes(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter a new goal...")

        self.add_button = QPushButton("➕ Add Goal")
        self.add_button.clicked.connect(self.add_goal)

        self.delete_button = QPushButton("🗑️ Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_goal)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        input_row.addWidget(self.add_button)

        root = QVBoxLayout(self)
        root.addLayout(input_row)
        root.addWidget(self.list)
        root.addWidget(self.delete_button)

        self.refresh_list()

    # --------------------
    # Rendering / refresh
    # --------------------
    def refresh_list(self):
        self.list.clear()
        for goal in self.goals:
            item = QListWidgetItem()
            # Make sure the item is selectable & enabled
            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            row = GoalRow(goal)
            row.toggled.connect(self._on_row_toggled)

            # Insert the row widget
            self.list.addItem(item)
            self.list.setItemWidget(item, row)
            item.setSizeHint(row.sizeHint())

    # --------------------
    # CRUD actions
    # --------------------
    def add_goal(self):
        text = self.input.text().strip()
        if not text:
            return
        new_goal = {"text": text, "done": False}
        self.goals.append(new_goal)
        save_goals(self.goals)
        self.input.clear()
        self.refresh_list()

    def delete_selected_goal(self):
        current_item = self.list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No selection", "Please select a goal to delete.")
            return

        row = self.list.itemWidget(current_item)
        if not isinstance(row, GoalRow):
            return

        goal_text = row.goal["text"]

        reply = QMessageBox.question(
            self,
            "Delete Goal?",
            f"Are you sure you want to delete “{goal_text}”?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Remove by identity
            self.goals = [g for g in self.goals if g is not row.goal]
            save_goals(self.goals)
            self.refresh_list()

    # --------------------
    # Event handlers
    # --------------------
    def _on_row_toggled(self, goal: dict, checked: bool):
        # Update model and persist
        goal["done"] = checked
        save_goals(self.goals)

        if checked:
            # Ask if we should remove completed goal
            reply = QMessageBox.question(
                self,
                "Remove completed goal?",
                f"You marked “{goal['text']}” as completed.\n\nDo you want to remove it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.goals = [g for g in self.goals if g is not goal]
                save_goals(self.goals)
                self.refresh_list()
