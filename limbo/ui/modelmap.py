"""Manipulates SVG of the model operation as an overview for the researcher."""

import os.path
import xml.etree.ElementTree as ET
from model import advanced_controls

def get_model_overview_svg(model, highlights=None, width=None, prefix=None):
    """Return an SVG containing only the modules used in this solution."""
    is_land = is_ocean = False
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
        if s.solution_category == advanced_controls.SOLUTION_CATEGORY.OCEAN:
            is_ocean = True

    if is_land:
        tree = ET.parse(os.path.join('data', 'land_model_diagram.svg'))
    elif is_ocean:
        tree = ET.parse(os.path.join('data', 'ocean_model_diagram.svg'))
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
        for name in highlights:
            node_color_fill(tree=tree, name=name)

    if width is not None:
        resize(tree, width)

    if prefix is not None:
        randomize_ids(tree, prefix)

    # Jupyter Notebook display(SVG()) does not tolerate explicit namespaces on the SVG tags.
    # Jupyterlab does, but we support use of the Notebook for https://github.com/QuantStack/voila
    # Remove the ns0: namespace prefixes and emit a default namespace.
    # We do this for Lab as well because it doesn't hurt and looks cleaner as XML.
    tree.getroot().attrib['xmlns'] = 'http://www.w3.org/2000/svg'
    s = ET.tostring(tree.getroot(), encoding='utf8', method='xml')
    return s.replace(b'ns0:', b'')


def delete_module(tree, name):
    """Remove a node and all edges which connect to it."""
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="' + name + '"]')
    for child in list(node):
        node.remove(child)
    for edge in tree.findall(r'.//{http://www.w3.org/2000/svg}g'):
        if 'id' not in edge.attrib:
            continue
        try:
            (source, _, dest) = edge.attrib['id'].split('_')
        except ValueError:
            continue
        if source == name or dest == name:
            for child in list(edge):
                edge.remove(child)


def node_color_fill(tree, name):
    """Color one node in the tree.

       Note that a list of modules is passed in, some of which may not exist in
       this specific solution because the code passing in the highlights is generic.
       It is not an error for name to not exist.
    """
    node = tree.find(r'.//{http://www.w3.org/2000/svg}g[@id="' + name + '"]')
    if node is not None and len(node) >= 1:
        rect = node[1]
        rect.attrib['fill'] = '#3D9970'


def resize(tree, width):
    """Adjust the viewPort to fit a new width."""
    svg = tree.getroot()
    old_width = float(svg.attrib['width'])
    old_height = float(svg.attrib['height'])
    ratio = float(width) / old_width
    new_height = old_height * ratio
    svg.attrib['width'] = str(width)
    svg.attrib['height'] = str(new_height)


def randomize_ids(tree, prefix):
    """Attach random text to id fields.

       Work around https://github.com/ipython/ipython/issues/1866 in Jupyter Notebook
       by prepending a random slug to the id fields within the SVG.
    """
    for elem in tree.getroot().iter():
        if 'id' in elem.attrib:
            orig = elem.attrib['id']
            elem.attrib['id'] = prefix + '_' + orig
        for tag in ['filter', 'marker-end', 'marker-start']:
            if tag not in elem.attrib:
                continue
            orig = elem.attrib[tag]
            if 'url(#' in orig:
                elem.attrib[tag] = orig.replace('url(#', f'url(#{prefix}_')
