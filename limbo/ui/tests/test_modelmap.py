"""Tests for ui/modelmap, generating model diagrams."""

import xml.etree.ElementTree as ET

import ui.modelmap
from solution import bottomtrawling
from solution import solarpvutil

def test_render_model():
    xml = ui.modelmap.get_model_overview_svg(model=solarpvutil)
    tree = ET.fromstring(xml)
    # SolarPVUtil does not use S-Curve, verify that S-Curve node is empty now.
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="sc"]')
    assert node is not None
    assert len(node) == 0

def test_highlight_module():
    xml = ui.modelmap.get_model_overview_svg(model=solarpvutil, highlights=['ad', 'tm'])
    tree = ET.fromstring(xml)
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="ad"]/{http://www.w3.org/2000/svg}rect')
    assert node.attrib['fill'] != 'white'
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="tm"]/{http://www.w3.org/2000/svg}rect')
    assert node.attrib['fill'] != 'white'
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="oc"]/{http://www.w3.org/2000/svg}rect')
    assert node.attrib['fill'] == 'white'

def test_width():
    xml = ui.modelmap.get_model_overview_svg(model=solarpvutil, width=200)
    tree = ET.fromstring(xml)
    assert int(tree.attrib['width']) == 200

def test_ocean():
    xml = ui.modelmap.get_model_overview_svg(model=bottomtrawling)
    tree = ET.fromstring(xml)
    # Limited Bottom Trawling does not use S-Curve, verify that S-Curve node is empty now.
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="sc"]')
    assert node is not None
    assert len(node) == 0

def test_randomize_ids():
    xml = ui.modelmap.get_model_overview_svg(model=solarpvutil, prefix='test')
    tree = ET.fromstring(xml)
    # The node id should have been randomized now, not "sc"
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="sc"]')
    assert node is None
