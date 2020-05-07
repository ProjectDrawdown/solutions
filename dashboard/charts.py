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
    get_all_solutions,
    get_excel_python_count,
    get_pds_adoption_basis_counts,
    get_py_solutions,
    get_ref_adoption_basis_counts,
    get_regional_as_percent,
    get_regional_nonzero,
    get_scenarios_per_solution,
    get_survey_data,
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
        legend_field="type",
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
        tooltips="From @left{1.1f} to @right{1.1f}: @{top} solutions",
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


# def get_pds_adoption_hist():
#     y_scale = bqplot.LinearScale()
#     y_axis = bqplot.Axis(scale=y_scale, orientation="vertical", label="# scenarios")
#     x_scale = bqplot.LinearScale()
#     x_axis = bqplot.Axis(scale=x_scale, tick_format=".1f", label="R\u00B2 value")
#     hist_data = surveydata["Rvalue"].dropna() ** 2
#     hist = bqplot.Hist(sample=hist_data, scales={"sample": x_scale, "count": y_scale})
#     hist.bins = 200
#     r2_value_chart = bqplot.Figure(
#         marks=[hist],
#         axes=[x_axis, y_axis],
#         padding_y=0,
#         title="Linearity of PDS Adoption",
#     )
#     r2_value_chart.layout.width = "100%"

#     ipywidgets.VBox(
#         [
#             ipywidgets.HBox([soln_count_fig, pds_adoption_fig, ref_adoption_fig]),
#             scenarios_per_solution_chart,
#             ipywidgets.HBox([tam_regional_nonzero_fig, tam_regional_chart]),
#             ipywidgets.HBox([ad_regional_nonzero_fig, ad_regional_chart]),
#             r2_value_chart,
#         ]
#     )
