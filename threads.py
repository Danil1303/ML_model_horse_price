import sys
import socket
import get_data
from time import localtime, strftime, sleep
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QPlainTextEdit, QPushButton, \
    QMessageBox


class ParseThread(QThread):
    def __init__(self, log_plain_text_edit):
        QThread.__init__(self)
        self.flag = True
        self.log_plain_text_edit = log_plain_text_edit

    def run(self) -> None:
        self.run_parse_thread()

    def run_parse_thread(self):
        # get_data.clear_data(self.log_plain_text_edit)
        parse_parameters = get_data.parse_initialize(self.log_plain_text_edit)
        data = parse_parameters[5]
        p = 0
        while self.flag:
            get_data.parse(parse_parameters, p , self.log_plain_text_edit)
            p+=1
        get_data.create_df(data)
        get_data.clear_data(self.log_plain_text_edit)
    def stop(self):
        self.flag = False
