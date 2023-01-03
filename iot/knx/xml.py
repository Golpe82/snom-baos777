import csv
import logging

from iot import settings, helpers

SEPERATOR = '_'
XML_HTTP_ROOT = f'http://{settings.GATEWAY_IP}/knx_xml/'
KNX_ROOT = settings.KNX_ROOT
XML_PHYSICAL_ROOT = settings.XML_TARGET_DIRECTORY
MAIN_XML_FILE_NAME = "knx_multi.xml"
ENCODING = 'iso-8859-10'
DATAPOINT_TYPES = {
    "binary": 1,
    "step_code": 3,
    "unsigned_value": 5,
}
DATAPOINT_SUBTYPES = {
    "binary": {
        "on_off": 1,
        "up_down": 8,
        "open_close": 9,
        "state": 11,
    },
    "step_code": {},
    "unsigned_value": {}
}
DATAPOINT_VALUES = {
    1: {"on": "-an", "off": "-aus"},
    3: {"increase": "-plus", "decrease": "-minus"},
}

# TODO: check and handle file if it is too big for RTX compability
# RTX max. size: 16K?
class SnomXMLFactory:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.csv_data = self.get_csv_data()
        helpers.update_directory(XML_PHYSICAL_ROOT)

    def get_csv_data(self):
        csv_file_path = f"{ settings.MEDIA_ROOT }{self.csv_file}"

        with open(csv_file_path, encoding=ENCODING) as csv_data:
            data = list(csv.reader(csv_data))
            has_header = "Group name" in data[0]

            if has_header:
                data.pop(0)

            return data

    def create_multi_xml(self):
        main_xml_path = f'{XML_PHYSICAL_ROOT}{MAIN_XML_FILE_NAME}'
        helpers.remove_file_if_exists(main_xml_path)

        with open(main_xml_path, 'w', encoding=ENCODING) as main_xml:
            open_xml_phone_menu(main_xml)

            for groupaddress_info in self.csv_data:
                groupaddress_name = groupaddress_info[0]
                groupaddress = groupaddress_info[1]
                groupaddress_items = groupaddress.split("/")
                main_address = groupaddress_items[0]
                is_main_address = '/-/-' in groupaddress

                if is_main_address:
                    mid_xml_file_name = f"{groupaddress.replace('/',SEPERATOR)}.xml"
                    create_xml_menu_item(main_xml, groupaddress_name, mid_xml_file_name)
                    self.create_mid_xml(groupaddress_name, main_address, mid_xml_file_name)
            
            close_xml_phone_menu(main_xml)

    def create_mid_xml(self, main_address_name, main_address, mid_xml_file_name):
        mid_xml_path = f"{XML_PHYSICAL_ROOT}{mid_xml_file_name}"
        helpers.remove_file_if_exists(mid_xml_path)

        with open(mid_xml_path, 'w', encoding=ENCODING) as mid_xml:
            open_xml_phone_menu(mid_xml, title=main_address_name)

            for groupaddress_info in self.csv_data:
                groupaddress_name = groupaddress_info[0]
                groupaddress = groupaddress_info[1]
                groupaddress_items = groupaddress.split("/")
                mid_address = groupaddress_items[1]
                sub_address = groupaddress_items[2]
                belongs_to_main_address = groupaddress_items[0] == main_address
                is_mid_address = mid_address != '-' and sub_address == '-'

                if belongs_to_main_address and is_mid_address:
                    sub_xml_file_name = f"{groupaddress.replace('/',SEPERATOR)}.xml"
                    create_xml_menu_item(mid_xml, groupaddress_name, sub_xml_file_name)
                    self.create_sub_xml(groupaddress_name, main_address, mid_address, sub_xml_file_name)

            close_xml_phone_menu(mid_xml)

    def create_sub_xml(self, mid_address_name, main_address, mid_address, sub_xml_file_name):
        sub_xml_path = f"{XML_PHYSICAL_ROOT}{sub_xml_file_name}"
        helpers.remove_file_if_exists(sub_xml_path)

        with open(sub_xml_path, 'w', encoding=ENCODING) as sub_xml:
            open_xml_phone_menu(sub_xml, title=mid_address_name)

            for groupaddress_info in self.csv_data:
                groupaddress_name = groupaddress_info[0]
                groupaddress = groupaddress_info[1]
                groupaddress_items = groupaddress.split("/")
                sub_address = groupaddress_items[2]
                belongs_to_main_address = groupaddress_items[0] == main_address
                belongs_to_mid_address = groupaddress_items[1] == mid_address
                is_sub_address = sub_address != '-'

                if belongs_to_main_address and belongs_to_mid_address and is_sub_address:
                    values_xml_file_name = f"{groupaddress.replace('/',SEPERATOR)}.xml"
                    create_xml_menu_item(sub_xml, groupaddress_name, values_xml_file_name)
                    self.create_values_xml(groupaddress_name, groupaddress, values_xml_file_name)

            close_xml_phone_menu(sub_xml)

    def create_values_xml(self, sub_address_name, sub_address, values_xml_file_name):
        values_xml_path = f"{XML_PHYSICAL_ROOT}{values_xml_file_name}"
        helpers.remove_file_if_exists(values_xml_path)

        with open(values_xml_path, 'w', encoding=ENCODING) as values_xml:
            open_xml_phone_menu(values_xml, title=sub_address_name)

            for groupaddress_info in self.csv_data:
                groupaddress = groupaddress_info[1]
                is_groupaddress = groupaddress == sub_address
                datapointtype_string = groupaddress_info[5]
                datapointtype_items = datapointtype_string.split("-")

                if len(datapointtype_items) >= 2:
                    datapointtype = get_datapoint_type(datapointtype_items)
                    datapoint_subtype = get_datapoint_subtype(datapointtype_items)

                    if is_groupaddress and datapointtype in DATAPOINT_TYPES.values():
                        if datapointtype == DATAPOINT_TYPES.get("binary") and datapoint_subtype in (DATAPOINT_SUBTYPES["binary"]).values():
                            create_xml_menu_item_action(values_xml, groupaddress, datapointtype)
                        elif datapointtype == DATAPOINT_TYPES.get("step_code"):
                            create_xml_menu_item_action(values_xml, groupaddress, datapointtype)
                        elif datapointtype == DATAPOINT_TYPES.get("unsigned_value"):
                            create_xml_menu_item_read_value(values_xml, groupaddress)

            close_xml_phone_menu(values_xml)

    # TODO: Refactor
    def create_single_xml(self):
        xml_file = settings.XML_TARGET_PATH

        with open(xml_file, "w") as xml_data:
            xml_data.write(
            '''<?xml version="1.0"?>
            '''
            )
            # there must be only one top-level tag
            xml_data.write(
        """
        <SnomIPPhoneMenu document_id='control'>
        <Title>KNX Snom</Title>"""
            )

            tag1 = ''
            tag2 = ''

            for row in self.csv_data:
                if '/-/-' in row[1]:
                    if tag2 == 'open':
                        xml_data.write(
                """
                </Menu>"""
                        )
                        tag2 = ''

                    if tag1 == 'open':
                        xml_data.write(
            """
            </Menu>"""
                        )
                        tag1 = ''   

                    xml_data.write(
            f"""
            <Menu Name='{ row[0] }'>
            <Name>{ row[0] }</Name>"""
                        )
                    tag1 = 'open'
                    continue

                elif '/-' in row[1]:
                    if tag2 == 'open':
                        xml_data.write(
                """
                </Menu>"""
                        )
                    tag2 = ''

                    xml_data.write(
                f"""
                <Menu Name='{ row[0] }'>
                <Name>{ row[0] }</Name>"""
                    )
                    tag2 = 'open'
                    continue

                elif 'DPST-1-' in row[5] and row[5] != 'DPST-1-11':
                    xml_data.write(
                    f"""
                    <Menu Name='{ row[0] }'>
                    <Name>{ row[0] }</Name>
                        <MenuItem>
                        <Name>on</Name>
                            <URL>{ settings.KNX_ROOT }{ row[1] }-an</URL>
                        </MenuItem>
                        <MenuItem>
                        <Name>off</Name>
                            <URL>{ settings.KNX_ROOT }{ row[1] }-aus</URL>
                        </MenuItem>
                    </Menu>"""
                    )
                    continue
                elif 'DPST-3-' in row[5]:
                    xml_data.write(
                    f"""
                    <Menu Name='{ row[0] }'>
                    <Name>{ row[0] }</Name>
                        <MenuItem>
                        <Name>plus</Name>
                            <URL>{ settings.KNX_ROOT }{ row[1] }-plus</URL>
                        </MenuItem>
                        <MenuItem>
                        <Name>minus</Name>
                            <URL>{ settings.KNX_ROOT }{ row[1] }-minus</URL>
                        </MenuItem>
                    </Menu>"""
                    )
                    continue

                elif '-' not in row[1]:
                    continue

                if tag1 == 'open':
                        xml_data.write(
                """
                </Menu>"""
                        )
                        tag1 = ''

            if tag2 == 'open':
                    xml_data.write(
                """
                </Menu>"""
                    )
                    tag2 = ''
            if tag1 == 'open':

                xml_data.write(
            """
            </Menu>"""
                )

            xml_data.write(
            """
        </SnomIPPhoneMenu>"""
            )

def create_xml_menu_item(xml_file, groupaddress_name, xml_subfile):
    xml_file.write(f"""
        <MenuItem>
            <Name>{groupaddress_name}</Name>
            <URL>{XML_HTTP_ROOT}{xml_subfile}</URL>
        </MenuItem>
    """)

def get_datapoint_type(datapointtype_items):
    return int(datapointtype_items[1])

def get_datapoint_subtype(datapointtype_items):
    try:
        datapoint_subtype = int(datapointtype_items[2])
    except IndexError:
        datapoint_subtype = None
    except Exception:
        logging.exception("Uncaught exception:")

    return datapoint_subtype

def create_xml_menu_item_action(xml_file, groupaddress, datapointtype):
    for label, value in DATAPOINT_VALUES.get(datapointtype).items():
        xml_file.write(f"""
            <MenuItem>
                <Name>{label}</Name>
                <URL>{ KNX_ROOT }{groupaddress}{value}</URL>
            </MenuItem>"""
        )

def create_xml_menu_item_read_value(xml_file, groupaddress):
    xml_file.write(f"""
        <MenuItem>
            <Name>Show {groupaddress} value</Name>
            <URL>Fetch {groupaddress} value</URL>
        </MenuItem>"""
    )

def open_xml_phone_menu(xml_file, title="KNX"):
    xml_file.write(f"""<?xml version="1.0" encoding="{ENCODING}"?>
        <SnomIPPhoneMenu>
        <Title>{title}</Title>""")

def close_xml_phone_menu(xml_file):
    xml_file.write("</SnomIPPhoneMenu>")
