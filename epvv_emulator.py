import pathlib
import random
import xml.etree.ElementTree as Et
from zipfile import ZipFile
import shutil
# for element in root.findall('.//{' + namespace_igr + '}element'): ищется в конкретном аттрибуте
# for element in root.findall('.'): ищется в корневой теге

TEMP_DIRECTORY = 'tmp'


def create_tmp_directory(directory_name):
    """
    :param directory_name: имя для нового каталога
    :return: создает временный каталог в директории с файлом
    """
    return pathlib.Path.cwd().joinpath(directory_name)


def delete_tmp_directory(directory_name):
    """
    :param directory_name: имя для нового каталога
    :return: удаляет временный каталог в директории
    """
    temp_path = pathlib.Path.cwd().joinpath(directory_name)
    return shutil.rmtree(temp_path, ignore_errors=True)


def get_fullpath_to_files_from_arhive(directory_name):
    """
    :param directory_name: имя каталога, в котором лежат файлы из архива
    :return: список файлов
    """
    files_in_directory_list = []

    for file in pathlib.Path(directory_name).iterdir():
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


def create_envelope_xml(xsd_path, out_directory_path, filename):
    """
    :param xsd_path: путь к xsd файлу, из которого берется пространство имен из атрибута targetNamespace
    :param out_directory_path: путь к каталогу, где будет создана xml
    :param filename: имя xml файла
    :return: xml файл
    """
    xsd_root = Et.parse(xsd_path).getroot()
    for element in xsd_root.findall('.'):
        main_namespace = element.attrib['targetNamespace']
        Et.register_namespace('igr', main_namespace)
    dict_file_names = dict(ESODReceipt=ESODReceipt_filename, RouteInfo=RouteInfo_filename)
    root_element = Et.Element('{' + main_namespace + '}Body')
    child_files = Et.Element('{' + main_namespace + '}Files')
    root_element.append(child_files)
    subchild_file0 = Et.Element('{' + main_namespace + '}File')
    subchild_file1 = Et.Element('{' + main_namespace + '}File')
    for count, (name, filename) in enumerate(dict_file_names.items()):
        file_attribs = dict(
            fileType=name,
            fileName=f'{name}.xml',
            fileIdentity=filename
        )
        for key, value in file_attribs.items():
            exec(f'subchild_file{count}.attrib[key] = value')
        exec(f'subchild_file{count}.text = " "')
    child_files.append(subchild_file0)
    child_files.append(subchild_file1)
    out_xml_path = pathlib.Path(out_directory_path).joinpath(filename)
    Et.ElementTree(root_element).write(out_xml_path, xml_declaration=True, encoding='utf-8')


def create_esodreceipt_xml(main_xsd_path, sub_xsd_path, out_directory_path, filename, dict_from_xml):
    """
    :param main_xsd_path: путь к основному xsd файлу, из которого берется основное пространство имен
    :param sub_xsd_path: путь к xsd файлу, из которого берется пространство имен для тегов
    :param out_directory_path: путь к каталогу, где будет создана xml
    :param filename: имя xml файла
    :param dict_from_xml: словарь из данных, полученных из xml файла
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
    child_header = Et.Element('{' + main_namespace + '}Header')
    child_body = Et.Element('{' + main_namespace + '}Body')
    root_element.append(child_header)
    root_element.append(child_body)
    subchild_a_info = Et.Element('{' + sub_namespace + '}AcknowledgementInfo')
    subchild_message = Et.Element('{' + sub_namespace + '}MessageInfo')
    child_header.append(subchild_a_info)
    child_header.append(subchild_message)
    for key, value in dict_from_xml:
        print(key)
        print(value)
    a_type = Et.Element('{' + sub_namespace + '}AcknowledgementType')
    # a_type.text = '1'
    result_code = Et.Element('{' + sub_namespace + '}ResultCode')
    # result_code.text = '0000'
    result_text = Et.Element('{' + sub_namespace + '}ResultText')
    # result_text.text = 'Its OK'
    subchild_a_info.append(a_type)
    subchild_a_info.append(result_code)
    subchild_a_info.append(result_text)
    child_to = Et.Element('{' + sub_namespace + '}To')
    # child_to.text = 'ext'
    child_from = Et.Element('{' + sub_namespace + '}From')
    # child_from.text = 'int'
    child_id = Et.Element('{' + sub_namespace + '}MessageID')
    # child_id.text = '5f2693ac-f1d7-4227-a53d-1633dd30710d'
    child_correliation_id = Et.Element('{' + sub_namespace + '}CorrelationMessageID')
    # child_correliation_id.text = '8987485f-f9e7-4fd2-8f8f-b992c4b5b669'
    child_type = Et.Element('{' + sub_namespace + '}MessageType')
    # child_type.text = '3'
    child_priority = Et.Element('{' + sub_namespace + '}Priority')
    # child_priority.text = '4'
    child_creation_time = Et.Element('{' + sub_namespace + '}CreateTime')
    # child_creation_time.text = '2023-04-12T05:03:01Z'
    child_send_time = Et.Element('{' + sub_namespace + '}SendTime')
    # child_send_time.text = '2023-04-12T05:03:01Z'
    subchild_message.append(child_to)
    subchild_message.append(child_from)
    subchild_message.append(child_id)
    subchild_message.append(child_correliation_id)
    subchild_message.append(child_type)
    subchild_message.append(child_priority)
    subchild_message.append(child_creation_time)
    subchild_message.append(child_send_time)
    out_xml_path = pathlib.Path(out_directory_path).joinpath(filename)
    Et.ElementTree(root_element).write(out_xml_path, xml_declaration=True, encoding='utf-8')


def create_routeinfo_xml(xsd_path, out_directory_path, filename):
    """
        :param xsd_path: путь к xsd файлу, из которого берется пространство имен из атрибута targetNamespace
        :param out_directory_path: путь к каталогу, где будет создана xml
        :param filename: имя xml файла
        :return: xml файл
        """
    xsd_root = Et.parse(xsd_path).getroot()
    for element in xsd_root.findall('.'):
        main_namespace = element.attrib['targetNamespace']
        Et.register_namespace('igr', main_namespace)
    root_element = Et.Element('{' + main_namespace + '}RouteInfo')
    child_task = Et.Element('{' + main_namespace + '}Task')
    # child_task.text = 'ZadOut'
    child_doc_id = Et.Element('{' + main_namespace + '}DocumentPackID')
    # child_doc_id.text = '5f2693ac-f1d7-4227-a53d-1633dd30710d'
    child_doc_correlation_id = Et.Element('{' + main_namespace + '}DocumentPackCorrelationID')
    # child_doc_correlation_id.text = '8987485f-f9e7-4fd2-8f8f-b992c4b5b669'
    child_datetime = Et.Element('{' + main_namespace + '}DateTime')
    # child_datetime.text = '2023-04-12T05:03:01Z'
    child_sender = Et.Element('{' + main_namespace + '}Sender')
    root_element.append(child_task)
    root_element.append(child_doc_id)
    root_element.append(child_doc_correlation_id)
    root_element.append(child_datetime)
    root_element.append(child_sender)
    subchild_feature1 = Et.Element('{' + main_namespace + '}Feature')
    subchild_feature2 = Et.Element('{' + main_namespace + '}Feature')
    subchild_feature3 = Et.Element('{' + main_namespace + '}Feature')
    subchild_feature4 = Et.Element('{' + main_namespace + '}Feature')
    child_sender.append(subchild_feature1)
    child_sender.append(subchild_feature2)
    child_sender.append(subchild_feature3)
    child_sender.append(subchild_feature4)
    subchild_code1 = Et.Element('{' + main_namespace + '}Code')
    # subchild_code1.text = 'INN'
    subchild_value1 = Et.Element('{' + main_namespace + '}Value')
    # subchild_value1.text = '7710030411'
    subchild_feature1.append(subchild_code1)
    subchild_feature1.append(subchild_value1)
    subchild_code2 = Et.Element('{' + main_namespace + '}Code')
    # subchild_code2.text = 'OGRN'
    subchild_value2 = Et.Element('{' + main_namespace + '}Value')
    # subchild_value2.text = ' '
    subchild_feature2.append(subchild_code2)
    subchild_feature2.append(subchild_value2)
    subchild_code3 = Et.Element('{' + main_namespace + '}Code')
    # subchild_code3.text = 'BIC'
    subchild_value3 = Et.Element('{' + main_namespace + '}Value')
    # subchild_value3.text = '044525545'
    subchild_feature3.append(subchild_code3)
    subchild_feature3.append(subchild_value3)
    subchild_code4 = Et.Element('{' + main_namespace + '}Code')
    # subchild_code4.text = 'RegNum'
    subchild_value4 = Et.Element('{' + main_namespace + '}Value')
    # subchild_value4.text = '1'
    subchild_feature4.append(subchild_code4)
    subchild_feature4.append(subchild_value4)
    out_xml_path = pathlib.Path(out_directory_path).joinpath(filename)
    Et.ElementTree(root_element).write(out_xml_path, xml_declaration=True, encoding='utf-8')


def get_data_from_xml(xml_path):
    root = Et.parse(xml_path).getroot()
    for element in root.findall('.'):
        main_namespace = element.attrib['targetNamespace']
        Et.register_namespace('igr', main_namespace)


ESODReceipt_filename = converts_name()
RouteInfo_filename = converts_name()
envelope_xsd_data = 'XMLSchema/igr/envelope.xsd'
main_esodreceipt_xsd_data = 'XMLSchema/soap-envelope.xsd'
sub_esodreceipt_xsd_data = 'XMLSchema/cbr_msg_props_v2017.2.0.xsd'
routeinfo_xsd_data = 'XMLSchema/igr/RouteInfo.xsd'
arhive_path = '1111/in/8987485f-f9e7-4fd2-8f8f-b992c4b5b669.zip'
# xml_path = 'tmp/156091b7-e142-4c7e-9db0-d67a69f8d529'  # status
# xml_path = 'tmp/dbb3c2c7-238c-4ba0-bcf6-5e03c7f869f0'  # ed408
# xml_path = 'tmp/b017a438-00e2-4e12-a1d7-eec9127cb62a'  # routeinfo
xml_path = 'tmp/envelope.xml'  # envelope

root = Et.parse(xml_path).getroot()
for element in root.findall('.'):
    print('attrib', element.attrib)
    print('tag', element.tag)
# for i in root.findall('.//*'):
#     print(' ', i)
#     print('attrib', i.attrib)
#     print('tag', i.tag)
#     print('text', i.text)
