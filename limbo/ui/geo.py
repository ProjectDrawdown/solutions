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


def get_globe(topofile, df, size=None, key=None):
    """Return an ipywidget with an interactive globe.

       Arguments:
         topofile: filename of a TopoJSON file to render. This file is expected to have its
            major regions arranged as a list in ['objects']['areas']['geometries'].
         df: dataframe where each row will be turned into an animation frame and columns
            are expected to match the major regions in the topofile.
         size: in integer pixels
         key: string key to pass to ipyvolume, allows replacement of earlier charts
    """
    with open(topofile, 'r') as fid:
        topo = json.loads(fid.read())
    (width, height) = (size, size) if size is not None else (500, 500)
    ipv.pylab.clear()
    fig = ipv.figure(width=width, height=height, key=key, controls=True)

    # Make a simple globe
    x, y, z = np.array([[0.], [0.], [0.]])
    ipv.scatter(x, y, z, size=100, color='blue', marker="sphere")

    # draw raised outlines for each area
    animate = []
    for area in topo['objects']['areas']['geometries']:
        name = area['id']
        if name not in df.columns:
            continue
        lines = _extract_lines(topo, name=name)
        x = []
        y = []
        z = []
        triangles = []
        data = df.loc[:, name].fillna(0.0)
        for (year, row) in df.iterrows():
            x_t = [0]
            y_t = [0]
            z_t = [0]
            tri_t = []
            offset = 1
            total = row.get('Total', row.get('World', 1.0))
            val = row.get(name, 0.0)
            radius = 1.01 + (((val / total) * 0.15) if total > 0.0 else 0.0)
            for line in lines:
                xyz = [_latlon2xyz(lat, lon, radius=radius) for (lon, lat) in line]
                x1, y1, z1 = [list(t) for t in zip(*xyz)]
                x_t.extend(x1 + [0])
                y_t.extend(y1 + [0])
                z_t.extend(z1 + [0])
                for _ in range(0, len(x1)):
                    tri_t.append([0, offset, offset+1])
                    offset += 1
                offset += 1
            x.append(x_t)
            y.append(y_t)
            z.append(z_t)
            triangles.append(tri_t)

        color = ui.color.webcolor_to_hex(ui.color.get_region_color(name))
        s = ipv.scatter(x=-np.array(x), y=np.array(z), z=np.array(y), color=color,
                size=0.5, connected=True, marker='sphere')
        s.material.visible = False
        animate.append(s)
        s = ipv.pylab.plot_trisurf(-np.array(x), np.array(z), np.array(y), color=color,
                triangles=triangles)
        animate.append(s)

    ipv.animation_control(animate, interval=100)
    ipv.xyzlim(-1, 1)
    ipv.style.box_on()
    ipv.style.axes_off()
    return ipv.gcc()
