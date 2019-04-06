"""Tests for ui/graphviz, generating model diagrams."""

import xml.etree.ElementTree as ET

import ui.graphviz
from solution import solarpvutil

def test_render_model():
    xml = ui.graphviz.get_model_overview_svg(model=solarpvutil)
    tree = ET.fromstring(xml)
    # SolarPVUtil does not use S-Curve, verify that S-Curve node is empty now.
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="sc"]')
    assert node is not None
    assert len(node) == 0

def test_highlight_module():
    xml = ui.graphviz.get_model_overview_svg(model=solarpvutil, highlights=['ad', 'tm'])
    tree = ET.fromstring(xml)
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="ad"]/{http://www.w3.org/2000/svg}polygon')
    assert node.attrib['fill'] != 'none'
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="tm"]/{http://www.w3.org/2000/svg}polygon')
    assert node.attrib['fill'] != 'none'
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="oc"]/{http://www.w3.org/2000/svg}polygon')
    assert node.attrib['fill'] == 'none'
    # all text on edges should have been removed
    assert len(tree.findall(r'.//{http://www.w3.org/2000/svg}textPath')) == 0

def test_width():
    xml = ui.graphviz.get_model_overview_svg(model=solarpvutil, width=200)
    tree = ET.fromstring(xml)
    assert tree.attrib['width'] == '200px'
