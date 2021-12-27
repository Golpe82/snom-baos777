import os
import csv
import logging

import chardet


from iot import settings

SEPERATOR='_'
XML_HTTP_ROOT=f'http://{settings.GATEWAY_IP}/'
KNX_ROOT=settings.KNX_ROOT
XML_PHYSICAL_ROOT=settings.NGINX_HTML_ROOT
MAIN_FILE = "knx_dect.xml"
MAIN_FILE_PATH = f'{XML_PHYSICAL_ROOT}{MAIN_FILE}'
ENCODING = 'iso-8859-10'
DATAPOINT_TYPES = {
    "binary": 1,
    "step_code": 3,
    "unsigned_value": 5,
}
DATAPOINT_SUBTYPES = {
    "binary": {
        "on_off": 1,
        "state": 11,
    },
    "step_code": {},
    "unsigned_value": {}
}


class SnomXMLFactory:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.encoding = self.get_encoding()
        self.csv_data = self.get_csv_data()

    def get_encoding(self):
        characters_to_read = 10000

        with open(f"{ settings.MEDIA_ROOT }{self.csv_file}", 'rb') as raw_data:
            result = chardet.detect(raw_data.read(characters_to_read))

        return result.get("encoding")

    def get_csv_data(self):
        csv_file_path = f"{ settings.MEDIA_ROOT }{self.csv_file}"

        with open(csv_file_path, encoding=self.encoding) as csv_data:
            data = list(csv.reader(csv_data))
            has_header = "Group name" in data[0]

            if has_header:
                data.pop(0)

            return data

    def create_xml_menus(self):
        if os.path.exists(MAIN_FILE_PATH):
            os.remove(MAIN_FILE_PATH)
        else:
            print("The file does not exist")

        with open(MAIN_FILE_PATH, 'w', encoding=ENCODING) as main_menu_data:
            main_menu_data.write(f"""<?xml version="1.0" encoding="{ENCODING}"?>
            <SnomIPPhoneMenu>
            <Title>KNX</Title>""")

            for groupaddress_info in self.csv_data:
                groupaddress_name = groupaddress_info[0]
                groupaddress = groupaddress_info[1]
                groupaddress_items = groupaddress.split("/")
                main_address = groupaddress_items[0]

                if '/-/-' in groupaddress:
                    mid_menu_file = f"{groupaddress.replace('/',SEPERATOR)}.xml"
                    main_menu_data.write(f"""
                <MenuItem>
                    <Name>{groupaddress_name}</Name>
                    <URL>{XML_HTTP_ROOT}{mid_menu_file}</URL>
                </MenuItem>""")
                    self.create_mid_menu(groupaddress_name, main_address, mid_menu_file)
            main_menu_data.write(f"""
        </SnomIPPhoneMenu>""")

    def create_mid_menu(self, main_address_name, main_address, mid_menu_file):
        mid_file_path = f"{XML_PHYSICAL_ROOT}{mid_menu_file}"

        if os.path.exists(mid_file_path):
            os.remove(mid_file_path)
        else:
            print("The file does not exist")

        with open(mid_file_path, 'w', encoding=ENCODING) as mid_menu_data:
            mid_menu_data.write(f"""<?xml version="1.0" encoding="{ENCODING}"?>
            <SnomIPPhoneMenu>
            <Title>{main_address_name}</Title>""")

            for groupaddress_info in self.csv_data:
                groupaddress_name = groupaddress_info[0]
                groupaddress = groupaddress_info[1]
                groupaddress_items = groupaddress.split("/")
                mid_address = groupaddress_items[1]
                sub_address = groupaddress_items[2]
                belongs_to_main_address = groupaddress_items[0] == main_address
                is_mid_address = mid_address != '-' and sub_address == '-'

                if belongs_to_main_address and is_mid_address:
                    sub_menu_file = f"{groupaddress.replace('/',SEPERATOR)}.xml"
                    mid_menu_data.write(f"""
                    <MenuItem>
                        <Name>{groupaddress_name}</Name>
                        <URL>{XML_HTTP_ROOT}{sub_menu_file}</URL>
                    </MenuItem>""")
                    self.create_sub_menu(groupaddress_name, main_address, mid_address, sub_menu_file)

            mid_menu_data.write(f"""
            </SnomIPPhoneMenu>""")

    def create_sub_menu(self, mid_address_name, main_address, mid_address, sub_menu_file):
        sub_file_path = f"{XML_PHYSICAL_ROOT}{sub_menu_file}"

        if os.path.exists(sub_file_path):
            os.remove(sub_file_path)
        else:
            print("The file does not exist")

        with open(sub_file_path, 'w', encoding=ENCODING) as sub_menu_data:
            sub_menu_data.write(f"""<?xml version="1.0" encoding="{ENCODING}"?>
            <SnomIPPhoneMenu>
            <Title>{mid_address_name}</Title>""")

            for groupaddress_info in self.csv_data:
                groupaddress_name = groupaddress_info[0]
                groupaddress = groupaddress_info[1]
                groupaddress_items = groupaddress.split("/")
                sub_address = groupaddress_items[2]
                belongs_to_main_address = groupaddress_items[0] == main_address
                belongs_to_mid_address = groupaddress_items[1] == mid_address
                is_sub_address = sub_address != '-'

                if belongs_to_main_address and belongs_to_mid_address and is_sub_address:
                    action_menu_file = f"{groupaddress.replace('/',SEPERATOR)}.xml"
                    sub_menu_data.write(f"""
                    <MenuItem>
                        <Name>{groupaddress_name}</Name>
                        <URL>{XML_HTTP_ROOT}{action_menu_file}</URL>
                    </MenuItem>""")
                    self.create_action_menu(groupaddress_name, groupaddress)

            sub_menu_data.write(f"""
            </SnomIPPhoneMenu>""")

    def create_action_menu(self, sub_address_name, sub_address):
        groupaddress_file_path = f"{XML_PHYSICAL_ROOT}/{sub_address.replace('/',SEPERATOR)}.xml"

        if os.path.exists(groupaddress_file_path):
            os.remove(groupaddress_file_path)
        else:
            print("The file does not exist")

        with open(groupaddress_file_path, 'w', encoding=ENCODING) as groupaddress_menu_data:
            groupaddress_menu_data.write(f"""<?xml version="1.0" encoding="{ENCODING}"?>
            <SnomIPPhoneMenu>
            <Title>{sub_address_name}</Title>""")

            for groupaddress_info in self.csv_data:
                groupaddress = groupaddress_info[1]
                datapointtype_string = groupaddress_info[5]
                datapointtype_items = datapointtype_string.split("-")

                if len(datapointtype_items) >= 2:
                    datapointtype = int(datapointtype_items[1])
                    try: 
                        datapoint_subtype = int(datapointtype_items[2])
                    except IndexError:
                        datapoint_subtype = None

                is_groupaddress = groupaddress == sub_address

                if is_groupaddress and datapointtype in DATAPOINT_TYPES.values():
                    if datapointtype == DATAPOINT_TYPES.get("binary") and datapoint_subtype == DATAPOINT_SUBTYPES["binary"]["on_off"]:
                        groupaddress_menu_data.write(f"""
                <MenuItem>
                    <Name>on</Name>
                    <URL>{ KNX_ROOT }{groupaddress}-an</URL>
                </MenuItem>
                <MenuItem>
                    <Name>off</Name>
                    <URL>{ KNX_ROOT}{groupaddress}-aus</URL>
                </MenuItem>""")

                    elif datapointtype == DATAPOINT_TYPES.get("step_code"):
                        groupaddress_menu_data.write(f"""
                <MenuItem>
                    <Name>increase</Name>
                    <URL>{ KNX_ROOT }{groupaddress}-plus</URL>
                </MenuItem>
                <MenuItem>
                    <Name>decrease</Name>
                    <URL>{ KNX_ROOT}{groupaddress}-minus</URL>
                </MenuItem>""")

                    elif datapointtype == DATAPOINT_TYPES.get("unsigned_value"):
                        groupaddress_menu_data.write(f"""
                <MenuItem>
                    <Name>Show {groupaddress} value</Name>
                    <URL>Fetch {groupaddress} value</URL>
                </MenuItem>""")
        
            groupaddress_menu_data.write(f"""
        </SnomIPPhoneMenu>""")

    def create_deskphone_xml(self):
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
