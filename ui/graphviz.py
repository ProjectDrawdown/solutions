"""Manipulates SVG of the model operation as an overview for the researcher."""

import os.path
import re
import xml.etree.ElementTree as ET
from model import advanced_controls

# Suppress output of 'ns0' namespace
ET.register_namespace("", "http://www.w3.org/2000/svg")

def get_model_overview_svg(model, highlights=None, width=None):
    """Return an SVG containing only the modules used in this solution."""
    is_land = False
    has_default_pds_ad = has_custom_pds_ad = has_s_curve_pds_ad = False
    has_default_ref_ad = has_custom_ref_ad = False
    for s in model.scenarios.values():
        if s.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
            has_default_pds_ad = True
        if s.soln_pds_adoption_basis == 'Fully Customized PDS':
            has_custom_pds_ad = True
        if 'S-Curve' in s.soln_pds_adoption_basis:
            has_s_curve_pds_ad = True
        if s.soln_ref_adoption_basis == 'Default':
            has_default_ref_ad = True
        if s.soln_ref_adoption_basis == 'Custom':
            has_custom_ref_ad = True
        if s.solution_category == advanced_controls.SOLUTION_CATEGORY.LAND:
            is_land = True

    if is_land:
        tree = ET.parse(os.path.join('data', 'land_model_diagram.svg'))
    else:
        tree = ET.parse(os.path.join('data', 'rrs_model_diagram.svg'))

    if not has_default_pds_ad and not has_default_ref_ad:
        delete_module(tree, 'ad')
    if not has_custom_pds_ad:
        delete_module(tree, 'capds')
    if not has_custom_ref_ad:
        delete_module(tree, 'caref')
    if not has_s_curve_pds_ad:
        delete_module(tree, 'sc')

    if highlights:
        remove_edge_labels(tree)
        for name in highlights:
            node_color_fill(tree=tree, name=name)

    if width is not None:
        resize(tree, width)

    return ET.tostring(tree.getroot(), encoding='utf8', method='xml')


def delete_module(tree, name):
    """Remove a node and all edges which connect to it."""
    for node in tree.findall(r'.//{http://www.w3.org/2000/svg}g[@class="node"]'):
        if node.attrib['id'] == name:
            node.attrib['visibility'] = 'invisible'
            for child in list(node):
                node.remove(child)
    for edge in tree.findall(r'.//{http://www.w3.org/2000/svg}g[@class="edge"]'):
        (source, _, dest) = edge.attrib['id'].split('_')
        if source == name or dest == name:
            edge.attrib['visibility'] = 'invisible'
            for child in list(edge):
                edge.remove(child)

def remove_edge_labels(tree):
    """Remove text labels from edges."""
    for edge in tree.findall(r'.//{http://www.w3.org/2000/svg}textPath/...'):
        for child in list(edge):
            if 'textPath' in child.tag:
                edge.remove(child)

def node_color_fill(tree, name):
    """Color one node in the tree."""
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="' + name + '"]')
    polygon = node.find(r'.//{http://www.w3.org/2000/svg}polygon')
    polygon.attrib['fill'] = '#3D9970'

def resize(tree, width):
    """Adjust the viewPort to fit a new width."""
    svg = tree.getroot()
    (_, w, _) = re.split(r'(\d+)', svg.attrib['width'], maxsplit=1)
    old_width = float(w)
    (_, h, _) = re.split(r'(\d+)', svg.attrib['height'], maxsplit=1)
    old_height = float(h)
    ratio = float(width) / old_width
    new_height = old_height * ratio
    svg.attrib['width'] = str(width) + 'px'
    svg.attrib['height'] = str(new_height) + 'px'
