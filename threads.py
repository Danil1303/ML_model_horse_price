import get_data
from time import time
from PyQt5.QtCore import QThread


class ParseThread(QThread):
    def __init__(self, log_plain_text_edit):
        QThread.__init__(self)
        self.flag = True
        self.log_plain_text_edit = log_plain_text_edit

    def run(self) -> None:
        self.run_parse_thread()

    def run_parse_thread(self):
        self.log_plain_text_edit.insertPlainText(f'Старт парсинга.\n')
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
            f'{len(data)} записей.\n')
        get_data.clear_data(self.log_plain_text_edit)

    def stop(self):
        self.flag = False
