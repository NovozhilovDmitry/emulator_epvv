import random
import xml.etree.ElementTree as Et


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
xsd_data = 'XMLSchema/igr/envelope.xsd'


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
        for key, value in element.items():
            if key == 'targetNamespace':
                namespace_igr = value
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



