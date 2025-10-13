import sys, random
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QMessageBox, QDialog, QVBoxLayout 
from PySide6.QtCore import QTimer, Qt

class LPCounter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Life Point Counter")
        self.setGeometry(400, 400, 400, 400)  # x, y, width, height
        self.active_player = 1

        self.setStyleSheet("""
            QWidget { background-color: #13161a; color: #E6EDF3; font-size: 14px; }
            QLabel#BigLP { font-size: 48px; font-weight: 700; letter-spacing: 0.5px; }
            QLabel#Hint  { color: #9aa4af; font-size: 12px; }
            QLabel { padding: 2px 4px; }
            QPushButton {
                background: #21262d; border: 1px solid #30363d; border-radius: 10px;
                padding: 10px 14px; font-weight: 600;
            }
            QPushButton:hover   { background: #2a3139; }
            QPushButton:pressed { background: #1d2228; }
            QPushButton#Danger  { background: #7a1a1a; border-color: #a52a2a; }
            QPushButton#Dice    { padding: 10px 20px; font-size: 16px; }
        """)

        # lps
        self.life_points_p1 = 8000
        self.life_points_p2 = 8000

        # --- Widgets ---
        self.player1 = QPushButton("Player 1 ")
        self.player2 = QPushButton("Player 2 ")

        self.label_player1 = QLabel(str(self.life_points_p1))
        self.label_player2 = QLabel(str(self.life_points_p2))
        self.label_player1.setObjectName("BigLP")
        self.label_player2.setObjectName("BigLP")
        self.label_player1.setAlignment(Qt.AlignCenter)
        self.label_player2.setAlignment(Qt.AlignCenter)

        self.label_current_string = QLabel("Currently selected Player: ")
        self.label_current_string.setObjectName("Hint")
        self.label_active_player = QLabel(str(self.active_player))
        self.label_active_player.setAlignment(Qt.AlignLeft)

        self.minus_50 = QPushButton("-50")
        self.minus_100 = QPushButton("-100")
        self.minus_200 = QPushButton("-200")
        self.minus_500 = QPushButton("-500");  self.minus_500.setObjectName("Danger")
        self.minus_1000 = QPushButton("-1000"); self.minus_1000.setObjectName("Danger")

        self.dice = QPushButton("Dice Throw")
        self.dice.setObjectName("Dice")

        # --- layout
        layout = QGridLayout()

        layout.setContentsMargins(16, 12, 16, 12)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(16)
        # distribute columns better
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)

        layout.addWidget(self.player1, 0, 0)
        layout.addWidget(self.label_current_string, 0, 1, alignment=Qt.AlignRight)
        layout.addWidget(self.label_active_player, 0, 2, alignment=Qt.AlignLeft)
        layout.addWidget(self.player2, 0, 3)

        layout.addWidget(self.label_player1, 1, 0, 1, 2)
        layout.addWidget(self.label_player2, 1, 2, 1, 2)


        layout.addWidget(self.dice, 2, 0, 1, 4, alignment=Qt.AlignCenter)

        # Buttons row
        layout.addWidget(self.minus_50,   3, 0)
        layout.addWidget(self.minus_100,  3, 1)
        layout.addWidget(self.minus_200,  3, 2)
        layout.addWidget(self.minus_500,  3, 3)
        layout.addWidget(self.minus_1000, 3, 4)

        self.setLayout(layout)

        # --- Connections
        self.player1.clicked.connect(lambda: self.set_active_player(1))
        self.player2.clicked.connect(lambda: self.set_active_player(2))

        self.minus_50.clicked.connect(lambda: self.change_lp(self.active_player,-50))
        self.minus_100.clicked.connect(lambda: self.change_lp(self.active_player,-100))
        self.minus_200.clicked.connect(lambda: self.change_lp(self.active_player,-200))
        self.minus_500.clicked.connect(lambda: self.change_lp(self.active_player,-500))
        self.minus_1000.clicked.connect(lambda: self.change_lp(self.active_player,-1000))

        self.dice.clicked.connect(lambda: self.dice_throw())

    def dice_throw(self):
        # Unicode dice faces: ⚀ ⚁ ⚂ ⚃ ⚄ ⚅
        dice_faces = ["\u2680", "\u2681", "\u2682", "\u2683", "\u2684", "\u2685"]

        dialog = QDialog(self)
        dialog.setWindowTitle("Rolling Dice...")
        dialog.setModal(True)

        vbox = QVBoxLayout(dialog)
        label = QLabel("–", dialog)
        label.setAlignment(Qt.AlignCenter)
        f = label.font()
        f.setPointSize(64)
        label.setFont(f)
        vbox.addWidget(label)

        counter = {"ticks": 0, "max": random.randint(15, 25), "interval": 60}
        timer = QTimer(dialog)

        def update_roll():
            face = random.randint(1, 6)
            label.setText(dice_faces[face - 1])
            counter["ticks"] += 1

            if counter["ticks"] > counter["max"] // 2:
                counter["interval"] += 25
                timer.setInterval(counter["interval"])

            if counter["ticks"] >= counter["max"]:
                timer.stop()
                final = random.randint(1, 6)
                label.setText(dice_faces[final - 1])
                QTimer.singleShot(500, dialog.accept)
                # QMessageBox.information(self, "Dice Result", f"You rolled a {final}!")

        timer.timeout.connect(update_roll)
        timer.start(counter["interval"])
        dialog.exec()

    def set_active_player(self, player):
        self.active_player = player
        self.label_active_player.setText(str(self.active_player))

    def start_new_game(self):  
        msg = QMessageBox(self)
        msg.setWindowTitle("New game ? ")
        msg.setText("Start a new game ? ")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        result = msg.exec()
        if result == QMessageBox.Yes:
            self.life_points_p1 = 8000
            self.life_points_p2 = 8000
            self.label_player1.setText(str(self.life_points_p1))
            self.label_player2.setText(str(self.life_points_p2))
        else:
            self.close()

    def change_lp(self,active_player, amount):
        if active_player == 1:
            self.life_points_p1 += amount
            self.label_player1.setText(str(self.life_points_p1))
        else:
            self.life_points_p2 += amount
            self.label_player2.setText(str(self.life_points_p2))
        if self.life_points_p1 <= 0:
            QMessageBox.information(self, "Game Over", "Player 2 wins!")
            self.start_new_game()
        elif self.life_points_p2 <= 0:
            QMessageBox.information(self, "Game Over", "Player 1 wins!")
            self.start_new_game()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LPCounter()
    window.show()
    sys.exit(app.exec())
