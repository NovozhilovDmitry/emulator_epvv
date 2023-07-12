import sys
import traceback
import pathlib
from log_settings import logger
from datetime import datetime
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QRunnable, QThreadPool, QSettings, QObject, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtWidgets import (QMainWindow,
                             QWidget,
                             QLabel,
                             QGridLayout,
                             QApplication,
                             QLineEdit,
                             QPushButton,
                             QFileDialog,
                             QComboBox,
                             QMessageBox)
from functions import (create_directory,
                       write_to_json_file_result_codes,
                       get_result_codes_from_json,
                       get_fullpath_to_files_from_arhive,
                       extract_files_from_arhive_to_directory,
                       converts_name,
                       create_envelope_xml,
                       create_esodreceipt_xml,
                       create_routeinfo_xml,
                       find_routeinfo_file_in_directory,
                       get_arhive,
                       move_files,
                       deleting_directories)
WINDOW_WIDTH = 460
WINDOW_HEIGHT = 100
TEMP_DIRECTORY_NAME = 'temp'
TEMP_DIRECTORY_FOR_XML = 'tmp'
ARCHIVE_DIRECTORY = 'arh'
OUT_DIRECTORY = 'out'
FILENAME_JSON = 'result_codes.json'
RESULT_CODE_DICT = {
    '0000': 'Сообщение успешно сформировано',
    '1005': 'Сообщение не будет обработано, поскольку архив сформирован неверно',
    '1006': 'Сообщение не будет обработано, поскольку служебный конверт не соответствует требуемой структуре',
    '3003': 'Сообщение заражено вирусом',
    '3004': 'Сообщение не будет обработано, поскольку адресная информация указана некорректно',
    '4002': 'Ошибка проверки подписи',
    '4010': 'Неизвестная ошибка',
    '9001': 'Общая ошибка обработки сообщения'
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
        self.get_settings()
        self.check_json_file()
        self.fill_combox()

    def print_output(self, s):  # слот для сигнала из потока о завершении выполнения функции
        logger.info(s)

    def thread_complete(self):  # слот для сигнала о завершении потока
        dlg = QMessageBox()
        dlg.setWindowTitle('ЭМУЛЯТОР ЕПВВ')
        text_message = f'Функция выполнена.\nНа выполнение затрачено {self.count_time}'
        dlg.setText(text_message)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()
        logger.info(f'Функция выполнена за {self.count_time}')

    def thread_handle_files(self):
        logger.info('Начато выполнение функции по формированию ответных интеграционных конвертов')
        worker = Worker(self.fn_main)  # функция, которая выполняется в потоке
        worker.signals.result.connect(self.print_output)  # сообщение после завершения выполнения задачи
        worker.signals.finish.connect(self.thread_complete)  # сообщение после завершения потока
        self.threadpool.start(worker)

    def fn_main(self, progress_callback):
        """
        :param progress_callback: результат выполнения функции в потоке
        :return: выполненная функция
        """
        start_time = datetime.now()
        temp_files_list = get_fullpath_to_files_from_arhive(self.lineedit_path_to_file.text())
        envelope_xsd = self.xsd_schema1.text()
        main_esodreceipt_xsd = self.xsd_schema2.text()
        sub_esodreceipt_xsd = self.xsd_schema3.text()
        routeinfo_xsd = self.xsd_schema4.text()
        envelope_name = 'envelope.xml'
        esod_name = converts_name()
        routeinfo_name = converts_name()
        temp_path = pathlib.Path(TEMP_DIRECTORY_FOR_XML)
        if self.paths_validation():
            self.create_directories()
            for convert in temp_files_list:
                extract_files_from_arhive_to_directory(convert, TEMP_DIRECTORY_NAME)
                dict_from_xml = self.merge_dict()
                create_envelope_xml(envelope_xsd, TEMP_DIRECTORY_FOR_XML, envelope_name, esod_name, routeinfo_name)
                create_esodreceipt_xml(main_esodreceipt_xsd,
                                       sub_esodreceipt_xsd, TEMP_DIRECTORY_FOR_XML, esod_name, dict_from_xml)
                create_routeinfo_xml(routeinfo_xsd, TEMP_DIRECTORY_FOR_XML, routeinfo_name, dict_from_xml)
                param1_archive_name = pathlib.Path(OUT_DIRECTORY).joinpath(dict_from_xml['main_archive_name']+'.zip')
                param2_envelope_name = temp_path.joinpath(envelope_name)
                param3_esod_name = temp_path.joinpath(esod_name)
                param4_routeinfo_name = temp_path.joinpath(routeinfo_name)
                get_arhive(param1_archive_name, param2_envelope_name, param3_esod_name, param4_routeinfo_name)
                for file in pathlib.Path(TEMP_DIRECTORY_NAME).glob('*'):
                    try:
                        file.unlink()
                    except OSError as e:
                        logger.error(f'Ошибка: {file} : {e.strerror}')
                try:
                    move_files(convert, ARCHIVE_DIRECTORY)
                except:
                    pathlib.Path(ARCHIVE_DIRECTORY).joinpath(dict_from_xml['DocumentPackID']+'.zip').unlink()
                    move_files(convert, ARCHIVE_DIRECTORY)
                    logger.info('ИК в архивном каталоге был заменен')
            list_directories_for_deleting = [TEMP_DIRECTORY_NAME, TEMP_DIRECTORY_FOR_XML]
            for directory in list_directories_for_deleting:
                deleting_directories(directory)
            logger.info('Функция по формированию ответных интеграционных конвертов выполнена')
        end_time = datetime.now()
        self.count_time = end_time - start_time
        return f'функция {traceback.extract_stack()[-1][2]} выполнена'

    def check_json_file(self):
        """
        :return: проверяет json-файл. Создает файл, если его нет. Если он есть, то проверяет что в нем
        """
        if pathlib.Path.exists(pathlib.Path.cwd().joinpath(FILENAME_JSON)):
            self.result_codes_dict = get_result_codes_from_json(pathlib.Path.cwd().joinpath(FILENAME_JSON))
        else:
            write_to_json_file_result_codes(pathlib.Path.cwd().joinpath(FILENAME_JSON), RESULT_CODE_DICT)
            self.result_codes_dict = get_result_codes_from_json(pathlib.Path.cwd().joinpath(FILENAME_JSON))

    def create_directories(self):
        """
        :return: создаются директории: временная, архивная, выходная
        """
        list_names = [TEMP_DIRECTORY_NAME, ARCHIVE_DIRECTORY, OUT_DIRECTORY, TEMP_DIRECTORY_FOR_XML]
        for name in list_names:
            if not pathlib.Path.exists(pathlib.Path.cwd().joinpath(name)):
                create_directory(name)

    def fill_dictionary_constants(self, new_dict=None):
        """
        :return: словарь констант
        :param new_dict: новый словарь, если нужно заменить своими значениями
        """
        constants = {}
        if new_dict is None:
            constants.setdefault('a_type', '1')
            constants.setdefault('child_to', 'ext')
            constants.setdefault('child_from', 'int')
            constants.setdefault('child_type', '3')
            constants.setdefault('child_priority', '4')
        else:
            constants.setdefault('a_type', new_dict['a_type'])
            constants.setdefault('child_to', new_dict['child_to'])
            constants.setdefault('child_from', new_dict['child_from'])
            constants.setdefault('child_type', new_dict['child_type'])
            constants.setdefault('child_priority', new_dict['child_priority'])
        return constants

    def fill_dict_from_interface(self):
        temp_dict = {
            'result_code': self.result_code.currentText(),
            'result_text': self.result_text.text(),
            'main_archive_name': converts_name(),
            'creation_send_datetime': datetime.now().isoformat('T', 'seconds') + 'Z'
        }
        return temp_dict

    def merge_dict(self):
        routeinfo_tags = ['Task', 'DocumentPackID']
        constants_dict = self.fill_dictionary_constants()
        routeinfo_dict = find_routeinfo_file_in_directory(TEMP_DIRECTORY_NAME, routeinfo_tags)
        interface_dict = self.fill_dict_from_interface()
        if routeinfo_dict is None:
            return None
        else:
            z = {**constants_dict, **routeinfo_dict}
            merged_dict = {**interface_dict, **z}
            return merged_dict

    def fill_combox(self):
        """
        :return: заполняет поле кодов результата
        """
        for i in self.result_codes_dict:
            self.result_code.addItem(i)
        self.result_text.setText(self.result_codes_dict[self.result_code.currentText()])

    def get_result_text(self):
        """
        :return: заполняет поле текстового описания кодов результата
        """
        self.result_text.setText(self.result_codes_dict[self.result_code.currentText()])
        self.result_text.setCursorPosition(1)

    def paths_validation(self):
        full_str_error = []
        for i in range(1, 5):
            if not pathlib.Path(eval('self.xsd_schema' + str(i) + '.text()')).exists():
                full_str_error.append(eval('self.xsd_schema' + str(i) + '.text()'))
        print(full_str_error)
        if len(full_str_error) == 0:
            logger.info('Успешная валидация путей')
            return True
        if len(full_str_error) > 0:
            error_message = 'Проверьте корректность следующих введенных путей:\n'
            for i in full_str_error:
                error_message = error_message + i + '\n'
            dlg = QMessageBox()
            dlg.setWindowTitle('Ошибка валидации путей')
            dlg.setText(error_message)
            dlg.setStandardButtons(QMessageBox.StandardButton.Close)
            dlg.exec()
            logger.error('Ошибка валидации путей')
            return False

    def header_layout(self):
        """
        :return: добавление виджетов в верхнюю часть интерфейса на главном окне
        """
        self.label_path_to_file = QLabel('Путь к файлу')
        self.lineedit_path_to_file = QLineEdit()
        self.lineedit_path_to_file.setPlaceholderText('Укажите каталог с интеграционными конвертами')
        self.xsd_schema1 = QLineEdit()
        self.xsd_schema1.setPlaceholderText('Путь к envelope.xsd')
        self.xsd_schema1.setToolTip('Путь к файлу: AppContext-> XMLSchemas-> epvv-> igr')
        self.xsd_schema2 = QLineEdit()
        self.xsd_schema2.setPlaceholderText('Путь к soap-envelope.xsd')
        self.xsd_schema2.setToolTip('Путь к файлу: AppContext-> XMLSchemas-> epvv')
        self.xsd_schema3 = QLineEdit()
        self.xsd_schema3.setPlaceholderText('Путь к cbr_msg_props.xsd')
        self.xsd_schema3.setToolTip('Путь к файлу: AppContext-> XMLSchemas-> epvv')
        self.xsd_schema4 = QLineEdit()
        self.xsd_schema4.setPlaceholderText('Путь к routeinfo.xsd')
        self.xsd_schema4.setToolTip('Путь к файлу: AppContext-> XMLSchemas-> epvv-> igr')
        self.result_code = QComboBox()
        self.result_code.activated.connect(self.get_result_text)
        self.result_code.setEditable(True)
        self.result_text = QLineEdit()
        self.btn_set_path = self.lineedit_path_to_file.addAction(QIcon(self.btn_icon),
                                                                 QLineEdit.ActionPosition.TrailingPosition)
        self.btn_xsd1 = self.xsd_schema1.addAction(QIcon(self.btn_icon), QLineEdit.ActionPosition.TrailingPosition)
        self.btn_xsd2 = self.xsd_schema2.addAction(QIcon(self.btn_icon), QLineEdit.ActionPosition.TrailingPosition)
        self.btn_xsd3 = self.xsd_schema3.addAction(QIcon(self.btn_icon), QLineEdit.ActionPosition.TrailingPosition)
        self.btn_xsd4 = self.xsd_schema4.addAction(QIcon(self.btn_icon), QLineEdit.ActionPosition.TrailingPosition)
        self.btn_set_path.triggered.connect(self.get_path)
        self.btn_xsd1.triggered.connect(self.get_xsd_path)
        self.btn_xsd2.triggered.connect(self.get_xsd_path)
        self.btn_xsd3.triggered.connect(self.get_xsd_path)
        self.btn_xsd4.triggered.connect(self.get_xsd_path)
        self.btn_handler = QPushButton('Обработать файлы в каталоге')
        self.btn_handler.clicked.connect(self.thread_handle_files)
        self.main_layout.addWidget(self.label_path_to_file, 0, 0)
        self.main_layout.addWidget(self.lineedit_path_to_file, 0, 1)
        self.main_layout.addWidget(self.xsd_schema1, 1, 0, 1, 2)
        self.main_layout.addWidget(self.xsd_schema2, 2, 0, 1, 2)
        self.main_layout.addWidget(self.xsd_schema3, 3, 0, 1, 2)
        self.main_layout.addWidget(self.xsd_schema4, 4, 0, 1, 2)
        self.main_layout.addWidget(self.result_code, 5, 0, 1, 2)
        self.main_layout.addWidget(self.result_text, 6, 0, 1, 2)
        self.main_layout.addWidget(self.btn_handler, 7, 0, 1, 2)

    def get_path(self):
        get_dir = QFileDialog.getExistingDirectory(self, caption='Выбрать каталог')
        if get_dir:
            get_dir = get_dir
        else:
            get_dir = 'Путь не выбран'
        self.lineedit_path_to_file.setText(get_dir)

    def get_xsd_path(self):
        button = self.sender()
        get_dir = QFileDialog.getOpenFileName(self, caption='Выбрать файл')
        if get_dir:
            get_dir = get_dir
        else:
            get_dir = 'Путь не выбран'
        for i in range(1, 5):
            if button is eval('self.btn_xsd' + str(i)):
                eval('self.xsd_schema' + str(i) + '.setText(get_dir[0])')

    def get_settings(self):
        """
        :return: заполнение полей из настроек
        """
        try:
            width = int(self.settings.value('GUI/width'))
            height = int(self.settings.value('GUI/height'))
            x = int(self.settings.value('GUI/x'))
            y = int(self.settings.value('GUI/y'))
            self.setGeometry(x, y, width, height)
            logger.info('Настройки размеров окна загружены.')
        except:
            logger.warning('Настройки размеров окна НЕ загружены. Установлены размеры по умолчанию')
        self.xsd_schema1.setText(self.settings.value('XSD/envelope'))
        self.xsd_schema2.setText(self.settings.value('XSD/soap-envelope'))
        self.xsd_schema3.setText(self.settings.value('XSD/cbr_msg_props'))
        self.xsd_schema4.setText(self.settings.value('XSD/routeinfo'))
        logger.info('Файл с пользовательскими настройками проинициализирован')

    def closeEvent(self, event):
        """
        :param event: событие, которое можно принять или переопределить при закрытии
        :return: охранение настроек при закрытии приложения
        """
        self.settings.beginGroup('GUI')
        self.settings.setValue('width', self.geometry().width())
        self.settings.setValue('height', self.geometry().height())
        self.settings.setValue('x', self.geometry().x())
        self.settings.setValue('y', self.geometry().y())
        self.settings.endGroup()
        self.settings.beginGroup('XSD')
        self.settings.setValue('envelope', self.xsd_schema1.text())
        self.settings.setValue('soap-envelope', self.xsd_schema2.text())
        self.settings.setValue('cbr_msg_props', self.xsd_schema3.text())
        self.settings.setValue('routeinfo', self.xsd_schema4.text())
        self.settings.endGroup()
        logger.info(f'Пользовательские настройки сохранены. Файл {__file__} закрыт')


if __name__ == '__main__':
    logger.info(f'Запущен файл {__file__}')
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
