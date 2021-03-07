import csv

from iot import settings

def create_xml(csv_file):
    xml_file = settings.XML_TARGET_PATH

    csv_data = csv.reader(open(f"{ settings.MEDIA_ROOT }{ csv_file }", encoding='latin-1'))
    data = [line for line in csv_data]
    xml_data = open(xml_file, 'w')
    xml_data.write(
    '''<?xml version="1.0"?>
    '''
    )
    # there must be only one top-level tag
    xml_data.write(
"""
<SnomIPPhoneMenu document_id="control">
    <Title>KNX Snom</Title>"""
    )

    tag1 = ''
    tag2 = ''

    for row in data:
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
    xml_data.close()

    return xml_data
