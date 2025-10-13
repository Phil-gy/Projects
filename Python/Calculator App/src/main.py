import sys
import math
import re
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox
)

class SafeCalc:
    OPS = {"+", "-", "*", "/", "^"}
    PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
    RIGHT_ASSOC = {"^"}  

    @staticmethod
    def normalize(expr: str) -> str:
        expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        expr = expr.replace(",", ".")  
        return "".join(expr.split())

    @staticmethod
    def tokenize(expr: str):
        tokens = []
        i, n = 0, len(expr)
        prev = None  

        while i < n:
            ch = expr[i]

            if ch.isdigit() or ch == ".":
                j = i + 1
                while j < n and (expr[j].isdigit() or expr[j] == "."):
                    j += 1
                tokens.append(expr[i:j])
                prev = tokens[-1]
                i = j
                continue

            if ch in "+-*/^()":
                # unary minus handling: if '-' followed by number and (start or after operator or '(')
                if ch == "-" and (prev is None or prev in SafeCalc.OPS or prev == "(") and i + 1 < n and (expr[i+1].isdigit() or expr[i+1] == "."):
                    j = i + 2
                    while j < n and (expr[j].isdigit() or expr[j] == "."):
                        j += 1
                    tokens.append(expr[i:j])  
                    prev = tokens[-1]
                    i = j
                    continue
                tokens.append(ch)
                prev = ch
                i += 1
                continue

            # invalid character
            raise ValueError(f"Invalid character: {ch!r}")

        return tokens

    @staticmethod
    def to_rpn(tokens):
        out = []
        stack = []
        for tok in tokens:
            if SafeCalc.is_number(tok):
                out.append(tok)
            elif tok in SafeCalc.OPS:
                while stack and stack[-1] in SafeCalc.OPS:
                    top = stack[-1]
                    if (top not in SafeCalc.RIGHT_ASSOC and SafeCalc.PRECEDENCE[top] >= SafeCalc.PRECEDENCE[tok]) or \
                       (top in SafeCalc.RIGHT_ASSOC and SafeCalc.PRECEDENCE[top] > SafeCalc.PRECEDENCE[tok]):
                        out.append(stack.pop())
                    else:
                        break
                stack.append(tok)
            elif tok == "(":
                stack.append(tok)
            elif tok == ")":
                while stack and stack[-1] != "(":
                    out.append(stack.pop())
                if not stack:
                    raise ValueError("Mismatched parentheses")
                stack.pop()  # remove '('
            else:
                raise ValueError(f"Unknown token: {tok}")
        while stack:
            if stack[-1] in ("(", ")"):
                raise ValueError("Mismatched parentheses")
            out.append(stack.pop())
        return out

    @staticmethod
    def eval_rpn(rpn):
        st = []
        for tok in rpn:
            if SafeCalc.is_number(tok):
                st.append(float(tok))
            else:
                if len(st) < 2:
                    raise ValueError("Malformed expression")
                b = st.pop()
                a = st.pop()
                if tok == "+":
                    st.append(a + b)
                elif tok == "-":
                    st.append(a - b)
                elif tok == "*":
                    st.append(a * b)
                elif tok == "/":
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    st.append(a / b)
                elif tok == "^":
                    st.append(a ** b)
                else:
                    raise ValueError(f"Unknown operator: {tok}")
        if len(st) != 1:
            raise ValueError("Malformed expression")
        val = st[0]
        if math.isnan(val) or math.isinf(val):
            raise ValueError("Invalid numeric result")
        return val

    @staticmethod
    def is_number(tok: str) -> bool:
        # token may be like "-3.14" or "2"
        return bool(re.fullmatch(r"-?\d+(\.\d+)?", tok))

    @staticmethod
    def evaluate(expr: str) -> float:
        expr = SafeCalc.normalize(expr)
        tokens = SafeCalc.tokenize(expr)
        rpn = SafeCalc.to_rpn(tokens)
        return SafeCalc.eval_rpn(rpn)

    @staticmethod
    def pretty_number(x: float) -> str:
        # show int if integer, else up to ~12 significant digits
        if abs(x - round(x)) < 1e-12:
            return str(int(round(x)))
        s = f"{x:.12g}"
        # strip trailing zeros in decimal form
        if "." in s and "e" not in s and "E" not in s:
            s = s.rstrip("0").rstrip(".")
        return s


# GUI
class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Calculator")
        self.setMinimumSize(QSize(320, 420))
        self.last_result = None  # for Ans

        central = QWidget(self)
        self.setCentralWidget(central)

        vbox = QVBoxLayout(central)
        vbox.setSpacing(8)

        self.history = QLabel("", alignment=Qt.AlignRight)
        self.history.setStyleSheet("color: gray; font-size: 12px;")
        vbox.addWidget(self.history)

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setPlaceholderText("0")
        self.display.setMaxLength(256)
        self.display.setStyleSheet("font-size: 24px; padding: 10px;")
        vbox.addWidget(self.display)

        grid = QGridLayout()
        grid.setSpacing(6)
        vbox.addLayout(grid)

        # Button labels laid out like a typical calculator
        rows = [
            ["C", "⌫", "(", ")"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["0", ".", "Ans", "+"],
            ["^", "±", "=", "="],  # make '=' wider (two cells)
        ]

        self.buttons = {}
        for r, row in enumerate(rows):
            c = 0
            while c < len(row):
                text = row[c]
                btn = QPushButton(text)
                btn.setMinimumHeight(48)
                btn.setStyleSheet("font-size: 18px;")
                self.buttons[(r, c)] = btn

                if text == "=" and c + 1 < len(row) and row[c+1] == "=":
                    grid.addWidget(btn, r, c, 1, 2)  # span 2 columns
                    c += 2
                else:
                    grid.addWidget(btn, r, c)
                    c += 1

        # Connect signals
        for (r, c), btn in self.buttons.items():
            btn.clicked.connect(lambda checked=False, t=btn.text(): self.on_button(t))

        # Status bar
        self.statusBar().showMessage("Ready")

        # Keyboard input
        self.display.returnPressed.connect(self.equals)

    # ---------- Button handling ----------
    def on_button(self, text: str):
        if text == "C":
            self.display.clear()
            self.history.clear()
            return
        if text == "⌫":
            self.display.backspace()
            return
        if text == "=":
            self.equals()
            return
        if text == "Ans":
            if self.last_result is not None:
                self.insert_text(SafeCalc.pretty_number(self.last_result))
            else:
                self.statusBar().showMessage("No previous result", 1500)
            return
        if text == "±":
            self.toggle_sign_last_number()
            return

        # Map pretty operators for display
        if text == "×":
            self.insert_text("×")
        elif text == "÷":
            self.insert_text("÷")
        elif text == "−":
            self.insert_text("−")
        else:
            self.insert_text(text)

    def insert_text(self, s: str):
        cursor = self.display.cursorPosition()
        txt = self.display.text()
        new = txt[:cursor] + s + txt[cursor:]
        self.display.setText(new)
        self.display.setCursorPosition(cursor + len(s))

    def toggle_sign_last_number(self):
        txt = self.display.text()
        # if whole display is a number, just toggle
        try:
            if txt and SafeCalc.is_number(SafeCalc.normalize(txt)):
                if txt.startswith("−") or txt.startswith("-"):
                    self.display.setText(txt[1:])
                else:
                    self.display.setText("−" + txt)
                return
        except Exception:
            pass

        # toggle sign of trailing number using regex
        m = re.search(r"(\d+(\.\d+)?)$", txt)
        if not m:
            self.statusBar().showMessage("No trailing number to toggle", 1200)
            return
        start, end = m.span(1)
        num = m.group(1)
        # check if already has unary minus directly before it
        if start > 0 and txt[start-1] in {"−", "-"}:
            new_txt = txt[:start-1] + txt[start:]  # remove the minus
        else:
            new_txt = txt[:start] + "−" + txt[start:]
        self.display.setText(new_txt)

    def equals(self):
        expr = self.display.text()
        if not expr.strip():
            return
        try:
            val = SafeCalc.evaluate(expr)
            pretty = SafeCalc.pretty_number(val)
            self.history.setText(f"{expr} =")
            self.display.setText(pretty)
            self.display.setCursorPosition(len(pretty))
            self.last_result = val
            self.statusBar().showMessage("OK", 1000)
        except ZeroDivisionError:
            self.error("Division by zero")
        except ValueError as e:
            self.error(str(e))
        except Exception as e:
            self.error(f"Error: {e}")

    def error(self, msg: str):
        self.statusBar().showMessage("Error", 1500)
        QMessageBox.warning(self, "Calculation Error", msg)

    # ---------- Keyboard shortcuts ----------
    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        # Evaluate on Enter
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.equals()
            return

        # Clear on Esc
        if key == Qt.Key_Escape:
            self.display.clear()
            self.history.clear()
            return

        mapping = {
            "*": "×",
            "/": "÷",
            "-": "−",
        }
        if text in mapping:
            self.insert_text(mapping[text])
            return

        if text and (text.isdigit() or text in {".", "+", "^", "(", ")"}):
            # Insert raw; normalization happens at evaluation
            self.insert_text(text)
            return

        super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    win = Calculator()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
