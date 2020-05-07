from math import pi

import bqplot
from bokeh.embed import components, file_html, autoload_static
from bokeh.io import show
from bokeh.palettes import Colorblind
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import cumsum
import numpy as np
import pandas as pd

from dashboard.helpers import (
    get_excel_python_count,
    get_pds_adoption_basis_counts,
    get_py_solutions,
    get_ref_adoption_basis_counts,
    get_regional_as_percent,
    get_regional_nonzero,
    get_scenarios_per_solution,
)


def make_pie_chart(data, cat_column, val_column, title, as_html=True):
    data = data.copy()
    data["angle"] = data[val_column] / data[val_column].sum() * 2 * pi
    if data.shape[0] == 2:
        data["color"] = Colorblind[3][:2]
    else:
        data["color"] = Colorblind[data.shape[0]]

    fig = figure(
        plot_height=400,
        plot_width=650,
        title=title,
        toolbar_location=None,
        tools="hover",
        tooltips=f"@{cat_column}: @{val_column}",
        x_range=(-0.5, 1.0),
    )

    fig.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="grey",
        fill_color="color",
        legend_field=cat_column,
        alpha=0.6,
        source=data,
    )

    fig.axis.axis_label = None
    fig.axis.visible = False
    fig.grid.grid_line_color = None

    if as_html is True:
        script, body = components(fig)
        return {"script": script, "body": body}
    return fig


def make_hist_chart(data, title, xlabel, ylabel, bins=10, density=False, as_html=True):

    hist, edges = np.histogram(data, density=density, bins=bins)
    bars = pd.DataFrame({"top": hist, "left": edges[:-1], "right": edges[1:]})
    bars["bottom"] = 0

    fig = figure(
        title=title,
        tools="hover",
        plot_height=400,
        plot_width=650,
        tooltips="[@left{1.1f} - @right{1.1f}]: @{top}",
    )

    fig.quad(
        top="top",
        bottom="bottom",
        left="left",
        right="right",
        fill_color=Colorblind[3][0],
        line_color="white",
        alpha=0.6,
        source=bars,
    )
    fig.y_range.start = 0
    fig.xaxis.axis_label = xlabel
    fig.yaxis.axis_label = ylabel
    fig.grid.grid_line_color = "grey"

    if as_html is True:
        script, body = components(fig)
        return {"script": script, "body": body}
    return fig


def make_comparison_chart(data, x_col, y_col, title, as_html=True):
    data = data.copy().sort_values(ascending=False).to_frame().reset_index()

    fig = figure(
        title=title,
        y_range=data[y_col],
        tools="hover",
        plot_height=600,
        plot_width=600,
        tooltips=f"@{{{y_col}}}: @{{{x_col}}}",
    )
    fig.hbar(
        y=y_col,
        right=x_col,
        left=0,
        fill_color=Colorblind[3][0],
        source=data,
        height=0.5,
    )
    fig.xaxis.axis_label = x_col

    if as_html is True:
        script, body = components(fig)
        return {"script": script, "body": body}
    return fig
