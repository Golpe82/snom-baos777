import os
import csv

from iot import settings

SEPERATOR='_'
XML_HTTP_ROOT=f'http://{settings.GATEWAY_IP}/'
KNX_ROOT=settings.KNX_ROOT
XML_PHYSICAL_ROOT=settings.NGINX_HTML_ROOT
MAIN_FILE = "knx_dect.xml"
MAIN_FILE_PATH = f'{XML_PHYSICAL_ROOT}{MAIN_FILE}'
ENCODING = 'iso-8859-10'

class SnomXMLFactory:
    def __init__(self):
        self.csv_data = []

    def create_handset_xml(self, csv_file):
        self.set_csv_data(csv_file)
        create_xml_files(self.csv_data)

    def set_csv_data(self, csv_file):
        with open(f"{ settings.MEDIA_ROOT }{ csv_file }", encoding=ENCODING) as csv_data:
            data = csv.reader(csv_data)
            self.csv_data = list(data)

    def create_deskphone_xml(self, csv_file):
        self.set_csv_data(csv_file)
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


def create_xml_files(csv_data):
    if os.path.exists(MAIN_FILE_PATH):
        os.remove(MAIN_FILE_PATH)
    else:
        print("The file does not exist")

    with open(MAIN_FILE_PATH, 'w', encoding=ENCODING) as main_menu_data:
        main_menu_data.write(f"""<SnomIPPhoneMenu>
        <Title>Main</Title>""")

        for row in csv_data:
            menu_name = row[0]
            main_menu = row[1]
            is_main_menu = '/-/-' in main_menu

            if is_main_menu:
                mid_menu_file = f"{main_menu.replace('/',SEPERATOR)}.xml"
                main_menu_data.write(f"""
            <MenuItem>
                <Name>{menu_name}</Name>
                <URL>{XML_HTTP_ROOT}{mid_menu_file}</URL>
            </MenuItem>""")
                make_mid_menu(csv_data, menu_name, main_menu, mid_menu_file)
        main_menu_data.write(f"""
    </SnomIPPhoneMenu>""")

def make_mid_menu(csv_data, main_menu_name, main_menu, mid_menu_file):
    mid_file_path = f"{XML_PHYSICAL_ROOT}{mid_menu_file}"
    main_menu_split = main_menu.split("/")

    if os.path.exists(mid_file_path):
        os.remove(mid_file_path)
    else:
        print("The file does not exist")

    with open(mid_file_path, 'w', encoding=ENCODING) as mid_menu_data:
        mid_menu_data.write(f"""<SnomIPPhoneMenu>
        <Title>{main_menu_name}</Title>""")

        for row_mid_menu in csv_data:
            row_split = row_mid_menu[1].split("/")
            if row_split[0] == main_menu_split[0] and row_split[1] != '-' and row_split[2] == '-':
                new_file_name = row_mid_menu[1].replace('/',SEPERATOR)

                mid_menu_data.write(f"""
                <MenuItem>
                    <Name>{ row_mid_menu[0] }</Name>
                    <URL>{XML_HTTP_ROOT}{new_file_name}.xml</URL>
                </MenuItem>""")
                make_action_menu(csv_data, row_mid_menu[0], row_mid_menu[1])

        mid_menu_data.write(f"""
        </SnomIPPhoneMenu>""")

def make_action_menu(data, menu_name, top_menu):
    xml_file=f"{XML_PHYSICAL_ROOT}/{top_menu.replace('/',SEPERATOR)}.xml"

    if os.path.exists(xml_file):
        os.remove(xml_file)
    else:
        print("The file does not exist")

    with open(xml_file, 'w', encoding=ENCODING) as xml_data:
        top_menu_split = top_menu.split("/")
        xml_data.write(f"""<SnomIPPhoneMenu>
        <Title>{menu_name}</Title>""")

        for row_action_menu in data:
            row_split = row_action_menu[1].split("/")
            if row_split[0] == top_menu_split[0] and row_split[1] == top_menu_split[1] and row_split[2] != '-': 
                action_split = row_action_menu[5].split("-")
                if action_split[0] == 'DPST' and action_split[1] == '1' and action_split[2] != '11':
                    xml_data.write(f"""
            <MenuItem>
                <Name>{ row_action_menu[0] }</Name>
            </MenuItem>
            <MenuItem>
                <Name>AN</Name>
                <URL>{ KNX_ROOT }{ row_action_menu[1] }-an</URL>
            </MenuItem>
            <MenuItem>
                <Name>AUS</Name>
                <URL>{ KNX_ROOT}{ row_action_menu[1] }-aus</URL>
            </MenuItem>""")
        
        xml_data.write(f"""
    </SnomIPPhoneMenu>""")
