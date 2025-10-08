import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Life Point Counter")
        self.setGeometry(400, 400, 400, 400)  # x, y, width, height

        #lps
        self.life_points_p1 = 8000
        self.life_points_p2 = 8000

        # --- Widgets ---
        self.player1 = QLabel("Player 1 ")
        self.label_player1 = QLabel(str(self.life_points_p1))
        self.label_player2 = QLabel(str(self.life_points_p2))
        self.player2 = QLabel("Player 2 ")
        self.minus_50 = QPushButton("-50")
        self.minus_100 = QPushButton("-100")
        self.minus_200 = QPushButton("-200")
        self.minus_500 = QPushButton("-500")
        self.minus_1000 = QPushButton("-1000")
       # self.button.clicked.connect(self.on_button_click)
        
        # --- Layout ---
        layout = QGridLayout()
        # Players
        layout.addWidget(self.player1, 0 ,0)
        layout.addWidget(self.player2, 0 ,1)
        layout.addWidget(self.label_player1, 1 ,0)
        layout.addWidget(self.label_player2, 1 ,1)
        # Buttons
        layout.addWidget(self.minus_50, 2, 0 )
        layout.addWidget(self.minus_100, 2, 1 )
        layout.addWidget(self.minus_200, 2, 2 )
        layout.addWidget(self.minus_500, 2, 3 )
        layout.addWidget(self.minus_1000, 2, 4 )
        self.setLayout(layout)



# --- Main Entry ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())