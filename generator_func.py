import xml.etree.ElementTree as Et
import random
import pathlib
import shutil
from zipfile import ZipFile


def name_for_ik():
    """
    :return: выдает имена формата ###-###-###-###-### в шестнадцатиричной системе для интеграционных конвертов
    """
    first_part = str(hex(random.randint(1000000000, 9999999999)))
    second_part = str(hex(random.randint(10000, 99999)))
    third_part = str(hex(random.randint(10000, 99999)))
    fourth_part = str(hex(random.randint(10000, 99999)))
    fifth_part = str(hex(random.randint(100000000000000, 999999999999999)))
    return f'{first_part[2:10]}-{second_part[2:6]}-{third_part[2:6]}-{fourth_part[2:6]}-{fifth_part[2:14]}'


def application_sum_generator(char_value):  # 17 символов для имени файла ED, 9 символов для номера договора
    """
    :param char_value: количество знаков в срезе
    :return: случайное число, которое зависит от системной даты и времени
    """
    a = str(random.randint(10, 99999999999))
    rv = random.randint(1, char_value - 1)
    final_countdown = int(a[len(a) + rv - char_value::])
    if final_countdown <= 0:
        final_countdown = random.randint(10, 99999999)
    return final_countdown  # рандомное число от 1 символа return a[len(a) - char_value::]


def attribute_generator(min_rand_length,
                        max_rand_length):  # 17 символов для имени файла ED, 9 символов для номера договора
    """
    :param min_rand_length: минимальное количество знаков в случайном числе (int)
    :param max_rand_length: максимальное количество знаков в случайном числе (int)
    :return: случайное число внутри указанного диапазона (int)
    """
    if min_rand_length == 1:
        start = min_rand_length
    else:
        start = 1 * 10 ** (min_rand_length - 1)
    if max_rand_length == 1:
        stop = max_rand_length
    else:
        stop = 1 * 10 ** max_rand_length - 1
    
    return random.randrange(start, stop)


def envelope_change_attrib(namespaceprefix, namespaceuri, xml_source_file_path, tags, paramreplace, path_to_save_xml):
    """
    Изменение аттрибутов в файле Envelope
    :param namespaceprefix: префикс пространства имен в файле envelope (igr)
    :param namespaceuri: ссылка пространства имен в envelope
    :param xml_source_file_path: путь к файлу envelope
    :param tags: теги, по которым идет поиск
    :param paramreplace: словарь из параметров тегов и их новых значений
    :param path_to_save_xml: путь и имя для готового файла
    :return: запись в файл в том же каталоге
    """
    Et.register_namespace(namespaceprefix, namespaceuri)  # для записи в файле необходимо передать prefix и uri
    tree = Et.parse(xml_source_file_path)  # открываем xml файл и парсим
    root = tree.getroot()
    for tag in tags:
        for element in root.findall('.//*[@{' + namespaceuri + '}' + tag + ']'):  #
            for key, value in paramreplace.items():
                if element.attrib['{' + namespaceuri + '}' + tag] in 'Document':
                    element.attrib['{' + namespaceuri + '}fileName'] = value
                if element.attrib['{' + namespaceuri + '}' + tag] in key:
                    if len(str(element.text).strip()) > 0:
                        if element.text is None:
                            element.attrib['{' + namespaceuri + '}fileIdentity'] = value
                        else:
                            element.text = value
                    else:
                        element.attrib['{' + namespaceuri + '}fileIdentity'] = value
    tree.write(path_to_save_xml)


def ed421_change_attrib(namespaceprefix, namespaceuri, xml_source_file_path, path_to_save_xml, **kwargs):
    """
    Изменение аттрибутов в файле ED421
    :param namespaceprefix: префикс пространства имен в файле ED421 (пусто)
    :param namespaceuri: ссылка пространства имен в файле ED421
    :param xml_source_file_path: путь к файлу ED421
    :param path_to_save_xml: путь и имя для готового файла
    :param kwargs: аттрибуты тега и их новые значения
    :return:
    """
    Et.register_namespace(namespaceprefix, namespaceuri)
    tree = Et.parse(xml_source_file_path)
    root = tree.getroot()
    for key, value in kwargs.items():
        if root.findall(f'.[@{key}]'):  # поиск атрибута в корневом элементе
            root.attrib[key] = value
        elif root.findall(f'.//*[@{key}]'):  # поиск атрибута в дочерних элементах
            root.find(f'.//*[@{key}]').set(key, value)
    tree.write(path_to_save_xml, encoding='UTF-8', xml_declaration=True)  # сохранение xml файла


def routeinfo_change_attrib(namespaceprefix, namespaceuri, xml_source_file_path, path_to_save_xml, new_text):
    """
    Редактирование RouteInfo
    :param namespaceprefix: префикс пространства имен в файле ED421 (igr)
    :param namespaceuri: ссылка пространства имен в файле ED421
    :param xml_source_file_path: путь к файлу
    :param path_to_save_xml: путь и имя для готового файла
    :param new_text: текст, который будет записан между тегами
    :return: запись в xml-файл
    """
    Et.register_namespace(namespaceprefix, namespaceuri)

    tree = Et.parse(xml_source_file_path)
    root = tree.getroot()
    root.find('{' + namespaceuri + '}DocumentPackID').text = new_text
    tree.write(path_to_save_xml)  # сохранение xml файла


def create_new_directory(path_to_new_directory, directory_name):
    """
    :param path_to_new_directory: путь, где будет создан каталог path
    :param directory_name: имя для нового каталога
    :return: создает каталог temp по указанному пути, если каталог существут, то перезаписывает его
    """
    pathlib.Path(path_to_new_directory).joinpath(directory_name).mkdir(exist_ok=True)
    return pathlib.Path(path_to_new_directory).joinpath(directory_name)


def get_arhive(path, *files):
    """
    :param path: путь, где будет создан архив
    :param files: файлы, которые будут помещаться в архив
    :return:
    """
    with ZipFile(path, 'w') as new_zip:  # добавить после path функцию вызова нового имени
        for arg in files:
            filename = arg.name
            new_zip.write(arg, arcname=filename)
            pathlib.Path(arg).unlink()


def move_files(copy_from, copy_to):
    """
    :param copy_from: полный путь к файлу, который будет перемещен
    :param copy_to: каталог, в который будет перемещен файл
    :return: перемещает файл, переданный из copy_from в каталог copy_to
    """
    shutil.move(copy_from, copy_to)


def check_dir_emptiness(path_for_ik):
    """
    Проверка наличия файлов в каталоге сохранения ИК
    :param path_for_ik:
    :return: True or False
    """
    dir_for_size = path_for_ik
    for i in pathlib.Path(dir_for_size).iterdir():
        if pathlib.Path(i).is_dir():
            print(f'{i} - каталог')
        elif pathlib.Path(i).is_file():
            print(f'{i} - файл')
        else:
            print('Тип объекта не опознан')
    

# -----------------------------------------------------------
# сгенерировать имена для файлов
def create_ik(path_for_ik, ed_date, req_date_time):
    # -----------------------------------------------------------
    start_path = pathlib.Path.cwd()
    envelope_path = start_path.joinpath('sample/envelope.xml')
    routeinfo_path = start_path.joinpath('sample/RouteInfo.xml')
    ed421_path = start_path.joinpath('sample/ED421.xml')
    # -----------------------------------------------------------
    # создать каталоги temp, converts внутри каталога
    temp_path = create_new_directory(start_path, 'temp')
    convert_path = path_for_ik
    # -----------------------------------------------------------
    # переменные
    prefix_for_routeinfo_envelope = 'igr'
    prefix_ed421 = 'elk'
    uri_for_routeinfo_envelope = 'http://www.cbr.ru/igr/'
    uri_for_ed421 = 'urn:cbr-ru:elk:v2023.1.0'
    text_for_sign_file = 'test signature file'
    tags_attrib = ['name', 'fileType']  # теги для функции generate_xml_envelope
    
    # for i in range(1, iteration_count + 1):
    arhive_name = name_for_ik()  # имя для архива, в который будут упакованы все файлы
    ed421_name_for_arh = name_for_ik()  # имя для архива, в котором лежит ed421
    routeinfo_name = name_for_ik()  # имя для routeinfo
    sign_name = name_for_ik()  # имя для файла с ЭП
    # -----------------------------------------------------------
    file_name_ed421 = pathlib.Path('ED421' + str(attribute_generator(2, 17)) + '.xml')
    new_name_ed421 = temp_path.joinpath(file_name_ed421)
    new_name_routeinfo = temp_path.joinpath(routeinfo_name)
    new_name_envelope = temp_path.joinpath('envelope.xml')
    # -----------------------------------------------------------
    # создать файл с подписью
    with open(temp_path.joinpath(sign_name), 'w') as sign_file:
        sign_file.write(text_for_sign_file)
    # заполнение словаря значениями
    tags_dictionary = dict(RouteInfo=routeinfo_name,
                           Document=ed421_name_for_arh,
                           Sign=sign_name,
                           AssociatedFileIdentity=ed421_name_for_arh,
                           fileName='ED421' + str(attribute_generator(2, 17)) + '.xml')
    attributes_and_values = dict(EDNo=str(attribute_generator(2, 8)),
                                 EDDate=ed_date,
                                 ReqNum=str(attribute_generator(2, 10)),
                                 ReqDateTime=req_date_time,
                                 GrantDate=ed_date,
                                 ApplicationSum=str(application_sum_generator(12)))
    # изменение значений в ED421 и сохранение в другом каталоге
    ed421_change_attrib(prefix_ed421,
                        uri_for_ed421,
                        ed421_path,
                        new_name_ed421,
                        **attributes_and_values)
    # изменение значений в RouteInfo и сохранение в другом каталоге
    routeinfo_change_attrib(prefix_for_routeinfo_envelope,
                            uri_for_routeinfo_envelope,
                            routeinfo_path,
                            new_name_routeinfo,
                            arhive_name)
    # изменение значений в RouteInfo и сохранение в другом каталоге
    envelope_change_attrib(prefix_for_routeinfo_envelope,
                           uri_for_routeinfo_envelope,
                           envelope_path,
                           tags_attrib,
                           tags_dictionary,
                           new_name_envelope)
    # добавление ED421 в архив
    get_arhive(temp_path.joinpath(ed421_name_for_arh),
               new_name_ed421)
    # формирование целого конверта
    get_arhive(temp_path.joinpath(pathlib.Path(arhive_name + '.zip')),
               temp_path.joinpath(ed421_name_for_arh),
               new_name_routeinfo,
               new_name_envelope,
               temp_path.joinpath(sign_name))
    # переместить конверт
    move_files(temp_path.joinpath(pathlib.Path(arhive_name + '.zip')), convert_path)
    # после того как все операции выполнены удалить каталог temp без проверки содержимого (наличия подкаталогов)
    shutil.rmtree(temp_path, ignore_errors=True)
