import re
import sys
import xml.etree.ElementTree as ET

# Suppress output of 'ns0' namespace
ET.register_namespace("", "http://www.w3.org/2000/svg")

tree = ET.parse(sys.stdin)

# Graphviz adds a <title> of %3.
# I'm sure there is a way to handle this in dot, but I'm not smart enough.
title = tree.getroot()[0][0]
title.text = 'Model Overview'

# graphviz generates its labels on paths as rectangular blocks of text. There isn't a way
# to make text follow a curved path. We instead pull the tooltips from edges and turn them
# into SVG textPath to follow the curve between nodes.
for edge in tree.findall(r'.//{http://www.w3.org/2000/svg}g[@class="edge"]'):
    group = edge[1]
    link = group[0]
    path = link[0]

    # add an ID attrib to identify this path from future elements.
    path_id = 'p_' + edge.attrib['id']
    path.attrib['id'] = path_id

    # the tooltip is a title attribute on the enclosing <a> group element.
    label = link.attrib['{http://www.w3.org/1999/xlink}title']
    textPath = ET.Element('textPath')
    textPath.attrib['ns1:href'] = '#' + path_id
    textPath.attrib['visibility'] = 'inherit'
    textPath.attrib['startOffset'] = '10%'
    textPath.text = label

    text = ET.Element('text')
    text.append(textPath)
    text.attrib['font-family'] = 'Times,serif'
    text.attrib['font-size'] = '9.00'
    text.attrib['fill'] = '#000000'

    link.append(text)

    for child in edge.findall('.//'):
        child.attrib['visibility'] = 'inherit'
    edge.attrib['visibility'] = 'visible'

# Put visibility attributes on all of the nodes, to make it easier to toggle from Jupyter.
for node in tree.findall(r'.//{http://www.w3.org/2000/svg}g[@class="node"]'):
    node.attrib['visibility'] = 'visible'
    for child in node:
        child.attrib['visibility'] = 'inherit'


tree.write(sys.stdout, encoding='unicode')
