import sys
import traceback
import pathlib
from log_settings import logger
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QRunnable, QThreadPool, QSettings, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QMainWindow,
                             QWidget,
                             QLabel,
                             QGridLayout,
                             QApplication,
                             QLineEdit,
                             QPushButton,
                             QFileDialog)
from functions import (create_directory,
                       write_to_json_file_result_codes,
                       get_result_codes_from_json,
                       get_fullpath_to_files_from_arhive,
                       extract_files_from_arhive_to_directory)
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 100
TEMP_DIRECTORY_NAME = 'temp'
ARCHIVE_DIRECTORY = 'arh'
OUT_DIRECTORY = 'out'
FILENAME_JSON = 'result_codes.json'
data_result_codes = {
    '0000': 'OK',
    '9999': 'NOT OK'
}

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
        self.btn_icon = QPixmap("others/folder.png")
        self.layout = QWidget()
        self.main_layout = QGridLayout()
        self.settings = QSettings('config.ini', QSettings.Format.IniFormat)
        self.threadpool = QThreadPool()
        self.header_layout()  # функция с добавленными элементами интерфейса для верхней части
        self.layout.setLayout(self.main_layout)
        self.setCentralWidget(self.layout)
        # self.initialization_settings()  # вызов функции с инициализацией сохраненных значений
        # self.set_settings()
        self.check_json_file()
        self.create_directories()

    def print_output(self, s):  # слот для сигнала из потока о завершении выполнения функции
        logger.info(s)

    def thread_complete(self):  # слот для сигнала о завершении потока
        logger.info(self)

    def thread_handle_files(self):
        logger.info('')
        worker = Worker(self.fn_main)  # функция, которая выполняется в потоке
        worker.signals.result.connect(self.print_output)  # сообщение после завершения выполнения задачи
        worker.signals.finish.connect(self.thread_complete)  # сообщение после завершения потока
        self.threadpool.start(worker)

    def fn_main(self, progress_callback):
        temp_files_list = get_fullpath_to_files_from_arhive(self.lineedit_path_to_file.text())
        for convert in temp_files_list:
            extract_files_from_arhive_to_directory(convert, TEMP_DIRECTORY_NAME)
        return f'функция {traceback.extract_stack()[-1][2]} выполнена'

    def check_json_file(self):
        if pathlib.Path.exists(pathlib.Path.cwd().joinpath(FILENAME_JSON)):
            self.result_codes_dict = get_result_codes_from_json(pathlib.Path.cwd().joinpath(FILENAME_JSON))
        else:
            write_to_json_file_result_codes(pathlib.Path.cwd().joinpath(FILENAME_JSON), data_result_codes)

    def create_directories(self):
        list_names = [TEMP_DIRECTORY_NAME, ARCHIVE_DIRECTORY, OUT_DIRECTORY]
        for name in list_names:
            if pathlib.Path.exists(pathlib.Path.cwd().joinpath(name)):
                pass
            else:
                create_directory(name)

    def a(self):
        pass

    def header_layout(self):
        """
        :return: добавлние виджетов в верхнюю часть интерфейса на главном окне
        """
        self.label_path_to_file = QLabel('Путь к файлу')
        self.lineedit_path_to_file = QLineEdit()
        self.lineedit_path_to_file.setPlaceholderText('Укажите путь к интеграционным конвертам')
        self.btn_set_path = self.lineedit_path_to_file.addAction(QIcon(self.btn_icon),
                                                                 QLineEdit.ActionPosition.TrailingPosition)
        self.btn_set_path.triggered.connect(self.get_path)
        self.btn_handler = QPushButton('Обработать файлы в каталоге')
        self.btn_handler.clicked.connect(self.fn_main)
        self.statusbar = self.statusBar()
        self.main_layout.addWidget(self.label_path_to_file, 0, 0)
        self.main_layout.addWidget(self.lineedit_path_to_file, 0, 1)
        self.main_layout.addWidget(self.btn_handler, 1, 0, 1, 2)

    def get_path(self):
        get_dir = QFileDialog.getExistingDirectory(self, caption='Выбрать файл')
        if get_dir:
            get_dir = get_dir
        else:
            get_dir = 'Путь не выбран'
        self.lineedit_path_to_file.setText(get_dir)

    # def get_settings(self):
    #     """
    #     :return: заполнение полей из настроек
    #     """
    #     self.editline_credit_jdbc_username.setText(self.settings.value('server_account/jdbc_username'))
    #     logger.debug('Файл с пользовательскими настройками проинициализирован')

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


if __name__ == '__main__':
    # logger.info(f'Запущен файл {__file__}')
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
