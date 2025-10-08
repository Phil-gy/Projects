import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QMessageBox

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Life Point Counter")
        self.setGeometry(400, 400, 400, 400)  # x, y, width, height
        self.active_player = 1
        #lps
        self.life_points_p1 = 8000
        self.life_points_p2 = 8000

        # --- Widgets ---
        self.player1 = QPushButton("Player 1 ")
        self.label_player1 = QLabel(str(self.life_points_p1))
        self.player2 = QPushButton("Player 2 ")
        self.label_player2 = QLabel(str(self.life_points_p2))
        self.label_current_string = QLabel("Currently selected Player: ")
        self.label_active_player = QLabel(str(self.active_player))

        self.minus_50 = QPushButton("-50")
        self.minus_100 = QPushButton("-100")
        self.minus_200 = QPushButton("-200")
        self.minus_500 = QPushButton("-500")
        self.minus_1000 = QPushButton("-1000")
       
        
        # --- Layout ---
        layout = QGridLayout()
        # Players
        layout.addWidget(self.player1, 0 ,0)
        layout.addWidget(self.player2, 0 ,3)
        layout.addWidget(self.label_player1, 1 ,0)
        layout.addWidget(self.label_player2, 1 ,1)
        layout.addWidget(self.label_active_player, 0 ,2)
        layout.addWidget(self.label_current_string, 0 ,1)
        # Buttons
        layout.addWidget(self.minus_50, 2, 0 )
        layout.addWidget(self.minus_100, 2, 1 )
        layout.addWidget(self.minus_200, 2, 2 )
        layout.addWidget(self.minus_500, 2, 3 )
        layout.addWidget(self.minus_1000, 2, 4 )
        self.setLayout(layout)

        self.player1.clicked.connect(lambda: self.set_active_player(1))
        self.player2.clicked.connect(lambda: self.set_active_player(2))

        self.minus_50.clicked.connect(lambda: self.change_lp(self.active_player,-50))
        self.minus_100.clicked.connect(lambda: self.change_lp(self.active_player,-100))
        self.minus_200.clicked.connect(lambda: self.change_lp(self.active_player,-200))
        self.minus_500.clicked.connect(lambda: self.change_lp(self.active_player,-500))
        self.minus_1000.clicked.connect(lambda: self.change_lp(self.active_player,-1000))

    def set_active_player(self, player):
        self.active_player = player
        self.label_active_player.setText(str(self.active_player))

    def start_new_game():  
        msg = QMessageBox()
        msg.setWindowTitle("New game ? ")
        msg.setText("Start a new game ? ")
        msg.setIcon(QMessageBox.Information)
        msg.exec()

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
            self.start_new_game()
            QMessageBox.information(self, "Game Over", "Player 1 wins!")

          



# --- Main Entry ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())