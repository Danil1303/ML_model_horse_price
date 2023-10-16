import sys
import glob
import threads
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPlainTextEdit, QPushButton, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        QMainWindow.__init__(self)

        self.df = None

        self.parse_thread = None

        self.setWindowTitle('Horse price')
        self.setFixedSize(175, 90)

        self.log_label = QLabel(self)
        self.log_label.setVisible(True)
        self.log_label.setText('Лог событий')
        self.log_label.adjustSize()
        self.log_label.move(180, 10)

        self.log_plain_text_edit = QPlainTextEdit(self)
        self.log_plain_text_edit.setGeometry(15, 30, 400, 420)

        self.message_box = QMessageBox(self)
        self.setFixedSize(600, 500)

        self.exit_button = QPushButton(self)
        self.exit_button.setText('Выход')
        self.exit_button.setGeometry(10, 460, 580, 30)
        self.exit_button.setVisible(True)
        self.exit_button.clicked.connect(self.exit)

        self.parse_button = QPushButton(self)
        self.parse_button.setText('Запустить парсер')
        self.parse_button.setGeometry(420, 30, 150, 30)
        self.parse_button.setVisible(True)
        self.parse_button.clicked.connect(self.start_parse)

        self.stop_parse_button = QPushButton(self)
        self.stop_parse_button.setText('Остановить парсер')
        self.stop_parse_button.setGeometry(420, 70, 150, 30)
        self.stop_parse_button.setVisible(True)
        self.stop_parse_button.setEnabled(False)
        self.stop_parse_button.clicked.connect(self.stop_parse)

        self.stop_parse_button = QPushButton(self)
        self.stop_parse_button.setText('Обучение модели')
        self.stop_parse_button.setGeometry(420, 110, 150, 30)
        self.stop_parse_button.setVisible(True)
        self.stop_parse_button.setEnabled(True)
        # self.stop_parse_button.clicked.connect(self.combine_data)

    def combine_data(self) -> None:
        self.df = pd.concat([pd.read_csv(file) for file in glob.glob('clean_data/equestrian*')], ignore_index=True)
        self.log_plain_text_edit.insertPlainText(f'Загружено строк: {len(self.df.index)}.\n')
        self.df.drop_duplicates(keep='first', inplace=True)
        self.log_plain_text_edit.insertPlainText(f'Количество строк после удаления дубликатов: {len(self.df.index)}.\n')

    def start_parse(self) -> None:
        self.parse_thread = threads.ParseThread(self.log_plain_text_edit)
        self.parse_thread.start()
        self.parse_button.setEnabled(False)
        self.stop_parse_button.setEnabled(True)

    def stop_parse(self) -> None:
        self.parse_thread.stop()
        self.parse_thread = None
        self.parse_button.setEnabled(True)
        self.stop_parse_button.setEnabled(False)

    def exit(self) -> None:
        if self.parse_thread:
            self.parse_thread.stop()
            self.parse_thread = None
        sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
