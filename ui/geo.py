"""Geographic views of data.

   Creates views of data projected onto a globe. This code uses techniques demonstrated in
   https://github.com/deeplook/spheromones for projecting geojson onto a sphere.
   That code is licensed under the GPL3; here it ends up being pulled into the Affero GPL3
   license used in the rest of the project.
"""

import json
import math

import numpy as np
import ipyvolume as ipv

import ui.color


def _extract_lines(gj, name=None):
    """Return lines from a TopoJSON file as a nested list of [lon, lat] coordinate pairs."""
    transform = gj.get('transform', {})
    scale = transform.get('scale', [1.0, 1.0])
    translate = transform.get('translate', [0.0, 0.0])

    expanded_arcs = gj.get('expanded_arcs', [])
    if not expanded_arcs:
        for arc in gj['arcs']:
            # https://github.com/topojson/topojson-specification#213-arcs
            line = []
            prev = [0, 0]
            for point in arc:
                prev[0] += point[0]
                prev[1] += point[1]
                line.append((prev[0] * scale[0] + translate[0], prev[1] * scale[1] + translate[1]))
            expanded_arcs.append(line)
        gj['expanded_arcs'] = expanded_arcs

    if name:
        # Extract the arcs for one particular area, like 'India'
        arcs = []
        for area in gj['objects']['areas']['geometries']:
            if area['id'] != name:
                continue
            for offset in area['arcs']:
                for n in offset[0]:
                    if n >= 0:
                        arcs.append(expanded_arcs[n])
                    else:
                        # https://github.com/topojson/topojson-specification#214-arc-indexes
                        arcs.append(expanded_arcs[~n])
    else:
        arcs = expanded_arcs
    return arcs


def _latlon2xyz(lat, lon, radius=1, unit='deg'):
    """Convert lat/lon pair to Cartesian x/y/z triple."""
    if unit == 'deg':
        pi_div_180 = math.pi / 180
        lat = lat * pi_div_180
        lon = lon * pi_div_180
    cos_lat = math.cos(lat)
    x = radius * cos_lat * math.cos(lon)
    y = radius * cos_lat * math.sin(lon)
    z = radius * math.sin(lat)
    return (x, y, z)


def get_globe(topofile, values=None, size=None, key=None):
    """Return an ipywidget with an interactive globe.

       Arguments:
         topofile: filename of a TopoJSON file to render. This file is expected to have its
            major regions arranged as a list in ['objects']['areas']['geometries'].
         values: dict-like structure of values for each region. Must also contain a 'Total' or
            'World' entry to use to compute relative heights.
         size: in integer pixels
         key: string key to pass to ipyvolume, allows replacement of earlier charts
    """
    data = json.load(open(topofile))
    (width, height) = (size, size) if size is not None else (500, 500)
    fig = ipv.figure(width=width, height=height, key=key, controls=True)
    if values is None:
        values = {}

    # Make a simple globe
    x, y, z = np.array([[0.], [0.], [0.]])
    ipv.scatter(x, y, z, size=100, color='blue', marker="sphere")

    # draw raised outlines for each area
    for area in data['objects']['areas']['geometries']:
        name = area['id']
        lines = _extract_lines(data, name=name)
        x = np.array([0])
        y = np.array([0])
        z = np.array([0])
        triangles = []
        total = values.get('Total', values.get('World', 1.0))
        val = values.get(name, 0.0)
        radius = 1.0 + ((val / total) * 0.2) if total != 0.0 else 1.0
        for line in lines:
            xyz = [_latlon2xyz(lat, lon, radius=radius) for (lon, lat) in line]
            x1, y1, z1 = np.array(xyz).T
            offset = x.size
            x = np.append(arr=x, values=np.append(x1, [0]))
            y = np.append(arr=y, values=np.append(y1, [0]))
            z = np.append(arr=z, values=np.append(z1, [0]))
            for idx in range(0, len(x1)-1):
                triangles.append([0, offset+idx, offset+idx+1])

        color = ui.color.webcolor_to_hex(ui.color.get_region_color(name))
        s = ipv.scatter(-x, z, y, color=color, size=0.5, connected=True, marker='sphere')
        s.material.visible = False
        ipv.pylab.plot_trisurf(-x, z, y, color=color, triangles=triangles)

    ipv.xyzlim(-1, 1)
    return ipv.gcc()
