import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("media.ico"))  

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
