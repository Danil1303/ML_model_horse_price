import sys
import glob

import get_data
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

        self.label_log = QLabel(self)
        self.label_log.setVisible(True)
        self.label_log.setText('Лог событий')
        self.label_log.adjustSize()
        self.label_log.move(180, 10)
        self.label_log.setVisible(False)

        self.log_plain_text_edit = QPlainTextEdit(self)
        self.log_plain_text_edit.setGeometry(15, 30, 400, 420)
        self.log_plain_text_edit.setVisible(False)

        self.message_box = QMessageBox(self)
        self.setFixedSize(300, 300)

        self.button_parse_mode = QPushButton(self)
        self.button_parse_mode.setText('Парсер')
        self.button_parse_mode.setGeometry(10, 200, 100, 30)
        self.button_parse_mode.clicked.connect(self.parse_mode)

        self.button_exit = QPushButton(self)
        self.button_exit.setText('Назад')
        self.button_exit.setGeometry(10, 460, 580, 30)
        self.button_exit.setVisible(False)
        self.button_exit.clicked.connect(self.predictions_mode)

        self.button_start_parse = QPushButton(self)
        self.button_start_parse.setText('Запустить парсер')
        self.button_start_parse.setGeometry(420, 30, 150, 30)
        self.button_start_parse.setVisible(False)
        self.button_start_parse.clicked.connect(self.start_parse)

        self.button_stop_parse = QPushButton(self)
        self.button_stop_parse.setText('Остановить парсер')
        self.button_stop_parse.setGeometry(420, 70, 150, 30)
        self.button_stop_parse.setVisible(False)
        self.button_stop_parse.clicked.connect(self.stop_parse)

        self.button_start_train = QPushButton(self)
        self.button_start_train.setText('Обучение модели')
        self.button_start_train.setGeometry(420, 110, 150, 30)
        self.button_start_train.setVisible(False)
        self.button_start_train.setEnabled(True)
        self.button_start_train.clicked.connect(self.start_train)

    def parse_mode(self) -> None:
        self.setFixedSize(600, 500)

        self.button_parse_mode.setVisible(False)
        self.label_log.setVisible(True)
        self.log_plain_text_edit.setVisible(True)
        self.button_exit.setVisible(True)
        self.button_start_parse.setVisible(True)
        self.button_stop_parse.setVisible(True)
        self.button_stop_parse.setEnabled(False)
        self.button_start_train.setVisible(True)

    def combine_data(self) -> None:
        self.df = pd.concat([pd.read_csv(file) for file in glob.glob('clean_data/equestrian*')], ignore_index=True)
        self.log_plain_text_edit.insertPlainText(f'Загружено строк: {len(self.df.index)}.\n')
        self.df.drop_duplicates(keep='first', inplace=True)
        self.log_plain_text_edit.insertPlainText(f'Количество строк после удаления дубликатов: {len(self.df.index)}.\n')

    def start_parse(self) -> None:
        self.parse_thread = threads.ParseThread(self.log_plain_text_edit)
        self.parse_thread.signal_parse_finish.connect(self.stop_parse)
        self.parse_thread.start()
        self.button_start_parse.setEnabled(False)
        self.button_stop_parse.setEnabled(True)
        self.button_start_train.setEnabled(False)

    def stop_parse(self) -> None:
        self.parse_thread.stop()
        self.button_start_parse.setEnabled(True)
        self.button_stop_parse.setEnabled(False)
        self.button_start_train.setEnabled(True)

    def predictions_mode(self) -> None:
        if self.parse_thread:
            self.parse_thread.stop()

        self.setFixedSize(300, 300)

        self.button_parse_mode.setVisible(True)
        self.label_log.setVisible(False)
        self.log_plain_text_edit.setVisible(False)
        self.button_exit.setVisible(False)
        self.button_start_parse.setVisible(False)
        self.button_stop_parse.setVisible(False)
        self.button_stop_parse.setEnabled(False)
        self.button_start_train.setVisible(False)

    def start_train(self) -> None:
        get_data.combine_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
