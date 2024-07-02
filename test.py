import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt


class SingleLetterBox(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Single Letter Box')

        self.layout = QVBoxLayout()

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setMaxLength(1)
        self.lineEdit.setReadOnly(True)

        self.layout.addWidget(self.lineEdit)

        self.setLayout(self.layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            print('a')  # Print 'a' when backspace is pressed
        elif event.text().isalpha() and len(event.text()) == 1:
            self.lineEdit.setText(event.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SingleLetterBox()
    ex.show()
    sys.exit(app.exec_())
