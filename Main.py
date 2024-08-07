import sys
import time

from PyQt5.QtGui import QCursor, QMouseEvent, QIcon, QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLineEdit, QMessageBox, QLabel, QPushButton
from PyQt5.QtCore import Qt, QEvent, QTimer, QPoint, QSize
import random


class WordleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_row = 0
        self.current_col = 0
        self.guess = None
        self.turns = 0
        self.get_random_word(WORDS)
        self.game_ended = False
        self.streak = 0
        self.won = False

    def initUI(self):
        self.setWindowIcon(QIcon('Images/logo.png'))
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(400, 555)
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(5)
        self.text_boxes = []

        self.gif = QLabel(self)
        self.gif.setAlignment(Qt.AlignRight | Qt.AlignTop)
        movie = QMovie('Images/streak.gif')
        self.gif.setMovie(movie)
        movie.start()
        self.gif.setVisible(False)
        self.grid_layout.addWidget(self.gif, 0, 4, 1, 1)

        self.button = QPushButton(self)
        self.button.setIcon(QIcon('Images/restart.png'))
        self.button.setIconSize(QSize(40, 40))
        self.button.clicked.connect(self.restart_game)
        self.button.setFixedSize(40, 40)
        self.button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.grid_layout.addWidget(self.button, 0, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        # Add an empty widget to the remaining space in the first row
        spacer = QWidget(self)
        self.grid_layout.addWidget(spacer, 0, 1, 1, 3)

        # Add vertical spacer to create a 50-pixel gap
        vertical_spacer = QWidget(self)
        vertical_spacer.setFixedHeight(50)
        self.grid_layout.addWidget(vertical_spacer, 1, 0, 1, 5)

        for i in range(6):
            row = []
            for j in range(5):
                text_box = QLineEdit(self)
                text_box.setReadOnly(True)
                text_box.setFixedSize(70, 70)
                text_box.setAlignment(Qt.AlignCenter)  # Align text to center
                text_box.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #33364f;
                        border-radius: 10px;
                        font-size: 32px;
                        color: white;
                        font-weight: bold;
                        text-align: center;
                    }
                """)
                self.grid_layout.addWidget(text_box, i + 2, j, Qt.AlignCenter)  # Align widget to center
                row.append(text_box)
            self.text_boxes.append(row)

        self.setLayout(self.grid_layout)
        self.setWindowTitle('Wordle')
        self.setFocusPolicy(Qt.StrongFocus)
        self.button.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("background-color: #252636;")

        # Ensure all columns have equal width
        for col in range(5):
            self.grid_layout.setColumnStretch(col, 1)

    def get_random_word(self, words) -> None:
        random_number = random.randint(0, len(words) - 1)
        self.word = WORDS[random_number].upper()
        print(self.word)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if Qt.Key_A <= key <= Qt.Key_Z and self.game_ended is False:
                if self.current_col > 4:
                    return True
                char = chr(key).upper()
                self.text_boxes[self.current_row][self.current_col].setText(char)
                self.current_col += 1
            elif Qt.Key_1 <= key <= Qt.Key_9:
                self.restart_game()
            elif key == Qt.Key_Backspace:
                if self.current_col > 0:
                    self.current_col -= 1
                    self.text_boxes[self.current_row][self.current_col].setText('')
            elif (key == Qt.Key_Return or key == Qt.Key_Enter) and self.current_col == 5:
                guess = ''.join([x.text() for x in self.text_boxes[self.current_row]])
                self.guess = guess
                if not self.guess_in_word():
                    self.show_message(2)
                else:
                    self.give_feedback()
                    self.current_row += 1
                    self.current_col = 0
            return True
        return False

    def guess_in_word(self) -> bool:
        word = self.guess.lower()
        return word in WORDS

    def showEvent(self, event) -> None:
        for row in self.text_boxes:
            for text_box in row:
                text_box.installEventFilter(self)

    def create_word_dict(self, word: str) -> dict[chr: int]:
        d = {}
        for c in word:
            if c in d.keys():
                d[c] += 1
            else:
                d[c] = 1
        return d

    def give_feedback(self) -> None:
        guess = self.guess
        feedback = [None, None, None, None, None]
        word_dict = self.create_word_dict(self.word)

        for i in range(0, 5):
            char = guess[i]
            if char == self.word[i]:
                feedback[i] = 'V'
                word_dict[char] -= 1

        for i in range(0, 5):
            if not feedback[i]:
                char = guess[i]
                if char in word_dict.keys() and word_dict[char] > 0:
                    feedback[i] = '-'
                    word_dict[char] -= 1
                else:
                    feedback[i] = 'X'

        feedback = ''.join(feedback)
        self.color_characters(feedback)
        self.turns += 1

        if all(x == 'V' for x in feedback):
            self.handle_win()

        elif self.turns == 6:
            self.handle_loss()

    def handle_win(self):
        self.show_message(0)
        self.game_ended = True
        self.streak += 1
        self.check_streak()
        self.won = True

    def handle_loss(self):
        self.streak = 0
        self.check_streak()
        self.show_message(1)
        self.game_ended = True
        self.won = False


    def color_characters(self, feedback: str) -> None:
        color_dict = {'V': '#179931', '-': '#dbb90f', 'X': 'gray'}

        for i in range(5):
            color = color_dict[feedback[i]]
            self.text_boxes[self.current_row][i].setStyleSheet(f"""
                                        QLineEdit {{
                                            border-radius: 10px;
                                            padding: 5px;
                                            width: 70px;
                                            height: 70px;
                                            font-size: 32px;
                                            background-color: {color};
                                            text-align: center;
                                            color: white;
                                            font-weight: bold;
                                        }}
                                    """)
            self.text_boxes[self.current_row][i].setAlignment(Qt.AlignCenter)

    def restart_game(self) -> None:
        self.get_random_word(WORDS)
        self.clear_grid()

        if self.text_boxes and self.text_boxes[0]:
            self.text_boxes[0][0].setFocus()

        if not self.won:
            self.streak = 0
        self.game_ended = False
        self.check_streak()
        self.won = False

    def check_streak(self):
        if self.streak >= 3:
            self.gif.setVisible(True)
        else:
            self.gif.setVisible(False)

    def clear_grid(self) -> None:
        for i in range(6):
            for j in range(5):
                self.text_boxes[i][j].setText('')
                self.text_boxes[i][j].setStyleSheet(f"""
                                        QLineEdit {{
                                            border: 2px solid #33364f;
                                            border-radius: 10px;
                                            padding: 5px;
                                            width: 70px;
                                            height: 70px;
                                            font-size: 32px;
                                            text-align: center;
                                            color: white;
                                            font-weight: bold;
                                        }}
                                    """)
        self.current_row = 0
        self.current_col = 0
        self.turns = 0
        self.setFocus()

    def show_message(self, message_id: int) -> None:
        messages_list = [["Unbelievable!!", "Amazing!", "Great!", "Well Done", "Nice One", "Phew.."], self.word,
                         'Invalid word']
        if message_id == 0:
            text = messages_list[0][self.current_row]
        else:
            text = messages_list[message_id]

        message = QLabel(text, self)
        message.setGeometry(self.geometry().center().x() - 95, self.geometry().center().y() - 240, 190, 50)

        message.setStyleSheet("""
                    QLabel {
                        background-color: #2a3233;
                        color: white;
                        font-size: 16px;
                        padding: 10px;
                        border-radius: 20px;
                    }
                """)
        message.setAlignment(Qt.AlignCenter)
        message.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)

        message.show()

        QTimer.singleShot(1500, message.close)


def get_words() -> list[str]:
    with open('words.txt', 'r') as f:
        lines = f.readlines()
        return [line.strip() for line in lines]


WORDS = get_words()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WordleGUI()
    ex.show()
    sys.exit(app.exec_())
