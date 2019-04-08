import sys
import xml.etree.ElementTree as ET

# Suppress output of 'ns0' namespace
ET.register_namespace("", "http://www.w3.org/2000/svg")

tree = ET.parse(sys.stdin)

for node in tree.getroot().findall(r'.//{http://www.w3.org/2000/svg}g[@id]'):
    if 'Graphic_' in node.attrib['id']:
        title = node[0]
        assert title.tag == '{http://www.w3.org/2000/svg}title'
        node.attrib['id'] = title.text

for line in tree.findall(r'.//{http://www.w3.org/2000/svg}g[@id]'):
    if 'Line_' in line.attrib['id']:
        title = line[0]
        assert title.tag == '{http://www.w3.org/2000/svg}title'
        line.attrib['id'] = title.text

tree.write(sys.stdout, encoding='unicode')
