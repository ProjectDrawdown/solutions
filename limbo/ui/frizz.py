"""Frizzle charts."""

import os.path

import ipyvolume as ipv
import numpy as np
import PIL
import PIL.ImageDraw
import PIL.ImageFont
import ui.color

def get_frizzle_chart(df, ylabel, size=None, key=None, color=None):
    """Returns a 3D Frizz chart, one frizzle strip per column in the dataframe.

       Arguments:
         df: the DataFrame to graph.
         ylabel: text label to place on the Y axis.
         size: in integer pixels
         key: string key to pass to ipyvolume, allows replacement of earlier charts
         color: base color to generate a gradient from (if None, a default color will be used)

       Returns:
         an ipywidget
    """
    (width, height) = (size, size) if size is not None else (500, 500)
    fig = ipv.figure(width=width, height=height, key=key, controls=True)
    if isinstance(color, str):
        color = ui.color.webcolor_to_rgb(color)
    if not color:
        color = (128, 128, 128)

    # Draw a strip of triangles for each region, tracing the dataframe values
    for (z, region) in enumerate(df.columns):
        years = list(df.index)
        nyears = len(years)
        year = years.pop(0)
        X = [year, year]
        y = df.loc[year, region]
        Y = [y, y]
        Z = [float(z), float(z) + 1.0]
        U = [0.0, 0.0]
        V = [0.0, 1.0]
        triangles = []
        offset = 2
        for (idx, year) in enumerate(years, 1):
            X.extend([year, year])
            y = df.loc[year, region]
            Y.extend([y, y * 0.97])
            Z.extend([float(z), float(z) + 0.95])
            u = float(idx) / nyears
            U.extend([u, u])
            V.extend([0.0, 1.0])
            triangles.extend([[offset-2, offset-1, offset+1], [offset-2, offset, offset+1]])
            offset += 2
        img = PIL.Image.new(mode='RGB', size=(1000, 100), color=color)
        draw = PIL.ImageDraw.Draw(img)
        font = PIL.ImageFont.truetype(os.path.join('data', 'fonts', 'Roboto-Medium.ttf'), 85)
        draw.text(xy=(40, 0), text=region, fill=(255,250,250), font=font)
        ipv.pylab.plot_trisurf(np.array(X), np.array(Y), np.array(Z), triangles=triangles,
                u=U, v=V, texture=img.transpose(PIL.Image.FLIP_TOP_BOTTOM))

    ipv.style.box_on()
    ipv.pylab.xlabel('Year')
    first_year = df.index[0]
    last_year = df.index[-1]
    ipv.pylab.xlim(first_year - 2, last_year + 2)
    ipv.pylab.ylabel(ylabel)
    ipv.pylab.zlabel('Region')
    nregions = len(df.columns)
    ipv.pylab.zlim(-0.5, nregions + 0.5)
    ipv.pylab.view(10.0, 10.0, 3.0)
    ipv.pylab.view(-24.46, 73.7, 2.32)
    return ipv.gcc()
