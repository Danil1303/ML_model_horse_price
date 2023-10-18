import get_data
from time import time
from PyQt5.QtCore import QThread, pyqtSignal


class ParseThread(QThread):
    signal_parse_finish = pyqtSignal(str)

    def __init__(self, log_plain_text_edit):
        QThread.__init__(self)
        self.flag = True
        self.log_plain_text_edit = log_plain_text_edit

    def run(self) -> None:
        self.run_parse_thread()

    def run_parse_thread(self):
        self.log_plain_text_edit.insertPlainText(f'Старт парсинга.\n\n')
        parse_start = time()
        parse_parameters = get_data.parse_initialize()
        data = parse_parameters[5]
        p = 0
        while self.flag:
            parse_status = get_data.parse(parse_parameters, p, self.log_plain_text_edit)
            if not parse_status:
                break
            p += 1
        get_data.create_df(data)
        parse_time = time() - parse_start
        minutes = int(parse_time / 60)
        seconds = round(parse_time - minutes * 60, 2)
        self.log_plain_text_edit.insertPlainText(
            f'Парсинг занял {str(minutes) + " мин. " if minutes else ""}{seconds} сек., получено '
            f'{len(data)} записей.\n\n')
        self.signal_parse_finish.emit('parse_finish')
        get_data.clear_data(self.log_plain_text_edit)

    def stop(self):
        self.flag = False
