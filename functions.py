import pathlib
import random
import xml.etree.ElementTree as Et
from zipfile import ZipFile
import shutil
import json
# for element in root.findall('.//{' + namespace_igr + '}element'): ищется в конкретном аттрибуте
# for element in root.findall('.'): ищется в корневой теге


def write_to_json_file_result_codes(path_to_file, data):
    """
    :param path_to_file: путь, где будет создан файл
    :param data: данные, которые будут записаны в файл
    :return: записывает в файл
    """
    with open(path_to_file, 'w') as json_file:
        json.dump(data, json_file)


def get_result_codes_from_json(path_to_file):
    """
    :param path_to_file: путь к json файлу
    :return: структуру из json файла
    """
    with open(path_to_file, 'r') as json_file:
        return json.load(json_file)


def create_directory(directory_name):
    """
    :param directory_name: имя для нового каталога
    :return: создает временный каталог в директории с файлом
    """
    return pathlib.Path.cwd().joinpath(directory_name).mkdir(parents=True, exist_ok=True)


def delete_tmp_directory(directory_name):
    """
    :param directory_name: имя для нового каталога
    :return: удаляет временный каталог в директории
    """
    temp_path = pathlib.Path.cwd().joinpath(directory_name)
    return shutil.rmtree(temp_path, ignore_errors=True)


def get_fullpath_to_files_from_arhive(directory_name, suffix='.zip'):
    """
    :param directory_name: путь к каталогу, в котором лежат файлы из архива
    :param suffix:
    :return: список файлов с расширением .zip (расширение вшито)
    """
    files_in_directory_list = []
    for file in pathlib.Path(directory_name).iterdir():
        if pathlib.Path(file).suffix == suffix:
            files_in_directory_list.append(str(file))
    return files_in_directory_list


def extract_files_from_arhive_to_directory(path_to_arhive, directory_name):
    """
    :param path_to_arhive: путь к архиву, из которого извлекаются файлы
    :param directory_name: путь, куда будут помещены файлы
    :return: извлеченные файлы из архива
    """
    with ZipFile(path_to_arhive, 'r') as arhive:
        arhive.extractall(directory_name)


def converts_name():
    """
    :return: выдает имена формата ###-###-###-###-### в шестнадцатиричной системе для интеграционных конвертов
    """
    first_part = str(hex(random.randint(1000000000, 9999999999)))
    second_part = str(hex(random.randint(10000, 99999)))
    third_part = str(hex(random.randint(10000, 99999)))
    fourth_part = str(hex(random.randint(10000, 99999)))
    fifth_part = str(hex(random.randint(100000000000000, 999999999999999)))
    return f'{first_part[2:10]}-{second_part[2:6]}-{third_part[2:6]}-{fourth_part[2:6]}-{fifth_part[2:14]}'


def create_envelope_xml(xsd_path, out_directory_path, out_filename, esod_name, routeinfo_name):
    """
    :param xsd_path: путь к xsd файлу, из которого берется пространство имен из атрибута targetNamespace
    :param out_directory_path: путь к каталогу, где будет создана xml
    :param out_filename: имя xml файла
    :param esod_name: имя для файла esod receipt
    :param routeinfo_name: имя для файла route info
    :return: xml файл
    """
    xsd_root = Et.parse(xsd_path).getroot()
    for element in xsd_root.findall('.'):
        main_namespace = element.attrib['targetNamespace']
        Et.register_namespace('igr', main_namespace)
    dict_file_names = dict(ESODReceipt=esod_name, RouteInfo=routeinfo_name)
    root_element = Et.Element('{' + main_namespace + '}Body')
    child_files = Et.SubElement(root_element, '{' + main_namespace + '}Files')
    subchild_file0 = Et.SubElement(child_files, '{' + main_namespace + '}File')
    subchild_file1 = Et.SubElement(child_files, '{' + main_namespace + '}File')
    for count, (name, filename) in enumerate(dict_file_names.items()):
        file_attribs = dict(
            fileType=name,
            fileName=f'{name}.xml',
            fileIdentity=filename
        )
        for key, value in file_attribs.items():
            exec(f'subchild_file{count}.attrib[key] = value')
        exec(f'subchild_file{count}.text = " "')
    out_xml_path = pathlib.Path(out_directory_path).joinpath(out_filename)
    Et.ElementTree(root_element).write(out_xml_path, xml_declaration=True, encoding='utf-8')


def create_esodreceipt_xml(main_xsd_path, sub_xsd_path, out_directory_path, out_filename, dict_from_xml):
    """
    :param main_xsd_path: путь к основному xsd файлу, из которого берется основное пространство имен
    :param sub_xsd_path: путь к xsd файлу, из которого берется пространство имен для тегов
    :param out_directory_path: путь к каталогу, где будет создана xml
    :param out_filename: имя xml файла
    :param dict_from_xml: словарь из данных, полученных из входящего xml файла
    :return: xml файл
    """
    main_xsd_root = Et.parse(main_xsd_path).getroot()
    for element in main_xsd_root.findall('.'):
        main_namespace = element.attrib['targetNamespace']
        Et.register_namespace('env', main_namespace)
    sub_xsd_root = Et.parse(sub_xsd_path).getroot()
    for element in sub_xsd_root.findall('.'):
        sub_namespace = element.attrib['targetNamespace']
        Et.register_namespace('props', sub_namespace)
    root_element = Et.Element('{' + main_namespace + '}Envelope')
    child_header = Et.SubElement(root_element, '{' + main_namespace + '}Header')
    child_body = Et.SubElement(root_element, '{' + main_namespace + '}Body')
    subchild_a_info = Et.SubElement(child_header, '{' + sub_namespace + '}AcknowledgementInfo')
    subchild_message = Et.SubElement(child_header, '{' + sub_namespace + '}MessageInfo')
    a_type = Et.SubElement(subchild_a_info, '{' + sub_namespace + '}AcknowledgementType')
    result_code = Et.SubElement(subchild_a_info, '{' + sub_namespace + '}ResultCode')
    result_text = Et.SubElement(subchild_a_info, '{' + sub_namespace + '}ResultText')
    child_to = Et.SubElement(subchild_message, '{' + sub_namespace + '}To')
    child_from = Et.SubElement(subchild_message, '{' + sub_namespace + '}From')
    child_id = Et.SubElement(subchild_message, '{' + sub_namespace + '}MessageID')
    child_correliation_id = Et.SubElement(subchild_message, '{' + sub_namespace + '}CorrelationMessageID')
    child_type = Et.SubElement(subchild_message, '{' + sub_namespace + '}MessageType')
    child_priority = Et.SubElement(subchild_message, '{' + sub_namespace + '}Priority')
    child_creation_time = Et.Element('{' + sub_namespace + '}CreateTime')
    child_send_time = Et.SubElement(subchild_message, '{' + sub_namespace + '}SendTime')
    a_type.text = dict_from_xml['a_type']
    result_code.text = dict_from_xml['result_code']
    result_text.text = dict_from_xml['result_text']
    child_to.text = dict_from_xml['child_to']
    child_from.text = dict_from_xml['child_from']
    child_id.text = dict_from_xml['main_archive_name']
    child_correliation_id.text = dict_from_xml['DocumentPackID']
    child_type.text = dict_from_xml['child_type']
    child_priority.text = dict_from_xml['child_priority']
    child_creation_time.text = dict_from_xml['creation_send_datetime']
    child_send_time.text = dict_from_xml['creation_send_datetime']
    out_xml_path = pathlib.Path(out_directory_path).joinpath(out_filename)
    Et.ElementTree(root_element).write(out_xml_path, xml_declaration=True, encoding='utf-8')


def create_routeinfo_xml(xsd_path, out_directory_path, out_filename, dict_from_xml):
    """
        :param xsd_path: путь к xsd файлу, из которого берется пространство имен из атрибута targetNamespace
        :param out_directory_path: путь к каталогу, где будет создана xml
        :param out_filename: имя xml файла
        :param dict_from_xml: словарь из данных, полученных из входящего xml файла
        :return: xml файл
        """
    xsd_root = Et.parse(xsd_path).getroot()
    for element in xsd_root.findall('.'):
        main_namespace = element.attrib['targetNamespace']
        Et.register_namespace('igr', main_namespace)
    root_element = Et.Element('{' + main_namespace + '}RouteInfo')
    child_task = Et.SubElement(root_element, '{' + main_namespace + '}Task')
    child_doc_id = Et.SubElement(root_element, '{' + main_namespace + '}DocumentPackID')
    child_doc_correlation_id = Et.SubElement(root_element, '{' + main_namespace + '}DocumentPackCorrelationID')
    child_datetime = Et.SubElement(root_element, '{' + main_namespace + '}DateTime')
    child_sender = Et.SubElement(root_element, '{' + main_namespace + '}Sender')
    subchild_feature1 = Et.SubElement(child_sender, '{' + main_namespace + '}Feature')
    subchild_feature2 = Et.SubElement(child_sender, '{' + main_namespace + '}Feature')
    subchild_feature3 = Et.SubElement(child_sender, '{' + main_namespace + '}Feature')
    subchild_feature4 = Et.SubElement(child_sender, '{' + main_namespace + '}Feature')
    subchild_code1 = Et.SubElement(subchild_feature1, '{' + main_namespace + '}Code')
    subchild_value1 = Et.SubElement(subchild_feature1, '{' + main_namespace + '}Value')
    subchild_code2 = Et.SubElement(subchild_feature2, '{' + main_namespace + '}Code')
    subchild_value2 = Et.SubElement(subchild_feature2, '{' + main_namespace + '}Value')
    subchild_code3 = Et.SubElement(subchild_feature3, '{' + main_namespace + '}Code')
    subchild_value3 = Et.SubElement(subchild_feature3, '{' + main_namespace + '}Value')
    subchild_code4 = Et.SubElement(subchild_feature4, '{' + main_namespace + '}Code')
    subchild_value4 = Et.SubElement(subchild_feature4, '{' + main_namespace + '}Value')
    child_task.text = dict_from_xml['Task']
    child_doc_id.text = dict_from_xml['main_archive_name']
    child_doc_correlation_id.text = dict_from_xml['DocumentPackID']
    child_datetime.text = dict_from_xml['creation_send_datetime']
    subchild_code1.text = 'INN'
    subchild_value1.text = dict_from_xml['INN']
    subchild_code2.text = 'OGRN'
    subchild_value2.text = dict_from_xml['OGRN']
    subchild_code3.text = 'BIC'
    subchild_value3.text = dict_from_xml['BIC']
    subchild_code4.text = 'RegNum'
    subchild_value4.text = dict_from_xml['RegNum']
    out_xml_path = pathlib.Path(out_directory_path).joinpath(out_filename)
    with open(out_xml_path, 'wb') as out_file:
        out_file.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
        Et.ElementTree(root_element).write(out_file, xml_declaration=False, encoding='utf-8')


def get_dict_from_xml_tags(xml_path, tags_list: list):
    """
    :param xml_path: путь к xml файлу
    :param tags_list: список тегов, которые ищутся в xml
    :return: словарь с ключами, переданными в списке
    """
    dict_tags = {}
    root = Et.parse(xml_path).getroot()
    for element in root.findall('.//*'):
        for i in tags_list:
            if i in element.tag:
                dict_tags[i] = element.text
    return dict_tags


def get_dict_inn_ogrn_bic_regnum_from_routeinfo(xml_path):
    """
    :param xml_path: путь к xml файлу
    :return: словарь с ИНН, ОГРН, БИК и номером КО из xml файла
    """
    tag_list = ['INN', 'OGRN', 'BIC', 'RegNum']
    temp_list = []
    root = Et.parse(xml_path).getroot()
    for element in root.findall('.//*'):
        if 'Value' in element.tag:
            if element.text is None:
                temp_list.append('')
            else:
                temp_list.append(element.text)
    return dict(zip(tag_list, temp_list))


def find_routeinfo_file_in_directory(directory_name, tags_list: list):
    """
    :param directory_name: путь к директории с файлами
    :param tags_list: теги, которые нужны в файле RouteInfo
    :return: словарь с инн, огрн, бик, рег номером КО, задачей и именем архива из АС ДКО
    """
    for file in pathlib.Path(directory_name).iterdir():
        if file.name != '.DS_Store':
            root = Et.parse(file).getroot()
            for element in root.findall('.'):
                if 'RouteInfo' in element.tag:
                    taxes_tags = get_dict_inn_ogrn_bic_regnum_from_routeinfo(file)
                    needed_tags = get_dict_from_xml_tags(file, tags_list)
                    merged_dict = {**taxes_tags, **needed_tags}
    try:
        return merged_dict
    except UnboundLocalError:
        return None


def get_arhive(path, *files):
    """
    :param path: путь, где будет создан архив
    :param files: файлы, которые будут помещаться в архив
    :return: архив
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


def deleting_files(*args):
    """
    :param args: полный путь к файлу
    :return: удаление файла
    """
    for arg in args:
        temp_path = pathlib.Path(arg)
        temp_path.unlink()


def deleting_directories(temp_path):
    """
    :param temp_path: путь к директории
    :return: удаление директории
    """
    shutil.rmtree(temp_path, ignore_errors=True)


# envelope_xsd_data = 'XMLSchema/igr/envelope.xsd'
# main_esodreceipt_xsd_data = 'XMLSchema/soap-envelope.xsd'
# sub_esodreceipt_xsd_data = 'XMLSchema/cbr_msg_props_v2017.2.0.xsd'
# routeinfo_xsd_data = 'XMLSchema/igr/RouteInfo.xsd'
# arhive_path = '1111/in/8987485f-f9e7-4fd2-8f8f-b992c4b5b669.zip'
# routeinfo_path = 'tmp/b017a438-00e2-4e12-a1d7-eec9127cb62a'  # routeinfo
# envelope_path = 'tmp/envelope.xml'  # envelope
# routeinfo_tags = ['Task', 'DocumentPackID']

# print(find_routeinfo_file_in_directory('tmp', routeinfo_tags))
