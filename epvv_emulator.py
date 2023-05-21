import sys
import traceback
from log_settings import logger
from PyQt6.QtCore import QRunnable, QThreadPool, QSettings, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QMainWindow,
                             QWidget,
                             QLabel,
                             QGridLayout,
                             QApplication,
                             QLineEdit,
                             QPushButton)
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 100


class WorkerSignals(QObject):
    finish = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:  # выполняем переданный из window метод
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()  # формирует ошибку
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:  # если ошибок не было, то формируем сигнал .result и передаем результат `result`
            self.signals.result.emit(result)  # Вернуть результат обработки
        finally:
            self.signals.finish.emit()  # Готово


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle('Эмулятор ЕПВВ')  # заголовок главного окна
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.layout = QWidget()
        self.main_layout = QGridLayout()
        self.settings = QSettings('config.ini', QSettings.Format.IniFormat)
        self.threadpool = QThreadPool()
        self.header_layout()  # функция с добавленными элементами интерфейса для верхней части
        # добавление на макеты
        self.layout.setLayout(self.main_layout)
        self.setCentralWidget(self.layout)
        # self.initialization_settings()  # вызов функции с инициализацией сохраненных значений
        # self.set_settings()

    def print_output(self, s):  # слот для сигнала из потока о завершении выполнения функции
        logger.info(s)

    def thread_complete(self):  # слот для сигнала о завершении потока
        logger.info(self)

    def thread_check_pdb(self):
        logger.info('')
        worker = Worker(self.fn_test)  # функция, которая выполняется в потоке
        worker.signals.result.connect(self.print_output)  # сообщение после завершения выполнения задачи
        worker.signals.finish.connect(self.thread_complete)  # сообщение после завершения потока
        self.threadpool.start(worker)

    def fn_test(self, progress_callback):
        return f'функция {traceback.extract_stack()[-1][2]} выполнена'

    # def closeEvent(self, event):
    #     """
    #     :param event: событие, которое можно принять или переопределить при закрытии
    #     :return: охранение настроек при закрытии приложения
    #     """
    #     # сохранение размеров и положения окна
    #     self.settings.beginGroup('GUI')
    #     self.settings.setValue('width', self.geometry().width())
    #     self.settings.endGroup()
    #     logger.info('Пользовательские настройки сохранены')
    #     logger.info(f'Файл {__file__} закрыт')

    def header_layout(self):
        """
        :return: добавлние виджетов в верхнюю часть интерфейса на главном окне
        """
        self.label_path_to_file = QLabel('Путь к файлу')
        self.lineedit_path_to_file = QLineEdit()
        self.btn_handler = QPushButton('Обработать файлы в каталоге')
        self.btn_handler.clicked.connect(self.thread_check_pdb)


        self.main_layout.addWidget(self.label_path_to_file, 0, 0)
        self.main_layout.addWidget(self.lineedit_path_to_file, 0, 1)
        self.main_layout.addWidget(self.btn_handler, 1, 0, 1, 2)

    # def initialization_settings(self):
    #     """
    #     :return: заполнение полей из настроек
    #     """
    #     self.editline_credit_jdbc_username.setText(self.settings.value('server_account/jdbc_username'))
        # logger.debug('Файл с пользовательскими настройками проинициализирован')

    # def set_settings(self):
    #     """
    #     :return:
    #     """
    #     self.editline_pdb_name.setText(get_config('files/jdbc.properties', 'jdbc.url'))
    #     logger.debug('Файл с пользовательскими настройками проинициализирован')


if __name__ == '__main__':
    # logger.info(f'Запущен файл {__file__}')
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
