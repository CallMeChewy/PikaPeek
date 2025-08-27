import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel

class TestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Test")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()
        label = QLabel("Test Input:")
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Should see this input box")

        layout.addWidget(label)
        layout.addWidget(self.test_input)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec())
