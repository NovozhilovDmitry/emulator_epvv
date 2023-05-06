import pathlib
import random
import xml.etree.ElementTree as Et


TEMP_DIRECTORY = 'tmp'

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


ESODReceipt_filename = converts_name()
RouteInfo_filename = converts_name()
envelope_xsd_data = 'XMLSchema/igr/envelope.xsd'
main_esodreceipt_xsd_data = 'XMLSchema/soap-envelope.xsd'
sub_esodreceipt_xsd_data = 'XMLSchema/cbr_msg_props_v2017.2.0.xsd'
routeinfo_xsd_data = 'XMLSchema/igr/RouteInfo.xsd'


# for element in root.findall('.//{' + namespace_igr + '}element'): ищется в конкретном аттрибуте
# for element in root.findall('.'): ищется в корневой теге


def create_envelope_xml(xsd_path, out_xml_path):
    """
    :param xsd_path: путь к xsd файлу, из которого берется пространство имен из атрибута targetNamespace
    :param out_xml_path: путь, где будет создана xml
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
    doc = Et.ElementTree(root_element)
    doc.write(out_xml_path, xml_declaration=True, encoding='utf-8')


def create_esodreceipt_xml(main_xsd_path, sub_xsd_path, out_directory_path, filename):
    """
    :param main_xsd_path: путь к основному xsd файлу, из которого берется основное пространство имен
    :param sub_xsd_path: путь к xsd файлу, из которого берется пространство имен для тегов
    :param out_xml_path: путь, где будет создана xml
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
    a_type = Et.Element('{' + sub_namespace + '}AcknowledgementType')
    a_type.text = '1'
    result_code = Et.Element('{' + sub_namespace + '}ResultCode')
    result_code.text = '0000'
    result_text = Et.Element('{' + sub_namespace + '}ResultText')
    result_text.text = 'Its OK'
    subchild_a_info.append(a_type)
    subchild_a_info.append(result_code)
    subchild_a_info.append(result_text)
    child_to = Et.Element('{' + sub_namespace + '}To')
    child_to.text = 'ext'
    child_from = Et.Element('{' + sub_namespace + '}From')
    child_from.text = 'int'
    child_id = Et.Element('{' + sub_namespace + '}MessageID')
    child_id.text = '5f2693ac-f1d7-4227-a53d-1633dd30710d'
    child_correliation_id = Et.Element('{' + sub_namespace + '}CorrelationMessageID')
    child_correliation_id.text = '8987485f-f9e7-4fd2-8f8f-b992c4b5b669'
    child_type = Et.Element('{' + sub_namespace + '}MessageType')
    child_type.text = '3'
    child_priority = Et.Element('{' + sub_namespace + '}Priority')
    child_priority.text = '4'
    child_creation_time = Et.Element('{' + sub_namespace + '}CreateTime')
    child_creation_time.text = '2023-04-12T05:03:01Z'
    child_send_time = Et.Element('{' + sub_namespace + '}SendTime')
    child_send_time.text = '2023-04-12T05:03:01Z'
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


def create_routeinfo_xml(xsd_path, out_xml_path):
    # xsd_path = ''
    # out_xml_path = ''
    """
        :param xsd_path: путь к xsd файлу, из которого берется пространство имен из атрибута targetNamespace
        :param out_xml_path: путь, где будет создана xml
        :return: xml файл
        """
    xsd_root = Et.parse(xsd_path).getroot()
    for element in xsd_root.findall('.'):
        namespace_igr = element.attrib['targetNamespace']
        Et.register_namespace('igr', namespace_igr)
    dict_file_names = dict(ESODReceipt=ESODReceipt_filename, RouteInfo=RouteInfo_filename)
    root_element = Et.Element('{' + namespace_igr + '}Body')
    child_files = Et.Element('{' + namespace_igr + '}Files')
    root_element.append(child_files)
    subchild_file0 = Et.Element('{' + namespace_igr + '}File')
    subchild_file1 = Et.Element('{' + namespace_igr + '}File')
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
    doc = Et.ElementTree(root_element)
    doc.write(out_xml_path, xml_declaration=True, encoding='utf-8')


# create_esodreceipt_xml(main_esodreceipt_xsd_data, sub_esodreceipt_xsd_data, TEMP_DIRECTORY, 'test2')
