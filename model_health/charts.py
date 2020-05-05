from math import pi

import bqplot
from bokeh.embed import components, file_html, autoload_static
from bokeh.io import show
from bokeh.palettes import Colorblind
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import cumsum

from model_health.helpers import (
    get_all_solutions,
    get_excel_python_count,
    get_pds_adoption_basis_counts,
    get_py_solutions,
    get_ref_adoption_basis_counts,
    get_regional_as_percent,
    get_regional_nonzero_adoption,
    get_regional_nonzero_tam,
    get_scenarios_per_solution,
    get_survey_data,
)


def make_pie_chart(data, cat_column, val_column, title, as_html):
    data = data.copy()
    data["angle"] = data[val_column] / data[val_column].sum() * 2 * pi
    if data.shape[0] == 2:
        data["color"] = Colorblind[3][:2]
    else:
        data["color"] = Colorblind[data.shape[0]]

    fig = figure(
        plot_height=400,
        plot_width=700,
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
        source=data,
    )

    fig.axis.axis_label = None
    fig.axis.visible = False
    fig.grid.grid_line_color = None

    if as_html is True:
        script, body = components(fig)
        return {"script": script, "body": body}
    return fig


def make_scenarios_per_solution_chart(scenarios_per_solution):
    # TODO
    # scenarios_per_solution.scenario.plot.hist()

    y_scale = bqplot.LinearScale()
    y_axis = bqplot.Axis(scale=y_scale, orientation="vertical", label="solutions")
    x_scale = bqplot.LinearScale()
    x_axis = bqplot.Axis(scale=x_scale, tick_format="d", label="num scenarios")
    hist = bqplot.Hist(
        sample=scenarios_per_solution, scales={"sample": x_scale, "count": y_scale}
    )
    scenarios_per_solution_chart = bqplot.Figure(
        marks=[hist],
        axes=[x_axis, y_axis],
        padding_y=0,
        title="Num scenarios per solution",
    )
    scenarios_per_solution_chart.layout.width = "50%"
    scenarios_per_solution_chart.layout.height = "300px"


# # ------------------- Regional Data -------------------


# def get_nonzero_regional_tam_chart():
#     nonzero_chart = bqplot.Pie(
#         sizes=[nonzero_count, zero_count],
#         labels=["YES", "NO"],
#         colors=["Green", "Red"],
#         display_values=True,
#         values_format="d",
#         display_labels="inside",
#         radius=110,
#     )
#     tam_regional_nonzero_fig = bqplot.Figure(
#         marks=[nonzero_chart], title="Has Regional TAM Data?"
#     )
#     tam_regional_nonzero_fig.layout.width = "320px"
#     tam_regional_nonzero_fig.fig_margin = {"left": 1, "right": 1, "top": 1, "bottom": 1}


# def get_tam_regional_chart():
#     y_scale = bqplot.LinearScale()
#     y_axis = bqplot.Axis(scale=y_scale, orientation="vertical", label="# scenarios")
#     x_scale = bqplot.LinearScale()
#     x_axis = bqplot.Axis(scale=x_scale, tick_format=".1f", label="percentage")
#     hist_data = regional_nonzero_tam["RegionalFractionTAM"] * 100.0
#     hist = bqplot.Hist(sample=hist_data, scales={"sample": x_scale, "count": y_scale})
#     hist.bins = 50
#     tam_regional_chart = bqplot.Figure(
#         marks=[hist],
#         axes=[x_axis, y_axis],
#         padding_y=0,
#         title="Regional TAM as a % of World",
#     )
#     tam_regional_chart.layout.width = "100%"


# def get_non_zero_adoption_chart():
#     nonzero_chart = bqplot.Pie(
#         sizes=[nonzero_count, zero_count],
#         labels=["YES", "NO"],
#         colors=["Green", "Red"],
#         display_values=True,
#         values_format="d",
#         display_labels="inside",
#         radius=110,
#     )
#     ad_regional_nonzero_fig = bqplot.Figure(
#         marks=[nonzero_chart], title="Has Regional Adoption Data?"
#     )
#     ad_regional_nonzero_fig.layout.width = "320px"
#     ad_regional_nonzero_fig.fig_margin = {"left": 1, "right": 1, "top": 1, "bottom": 1}


# def get_ad_regional_chart():
#     y_scale = bqplot.LinearScale()
#     y_axis = bqplot.Axis(scale=y_scale, orientation="vertical", label="# scenarios")
#     x_scale = bqplot.LinearScale()
#     x_axis = bqplot.Axis(scale=x_scale, tick_format=".1f", label="percentage")
#     hist_data = regional_nonzero_adoption["RegionalFractionAdoption"] * 100.0
#     hist = bqplot.Hist(sample=hist_data, scales={"sample": x_scale, "count": y_scale})
#     hist.bins = 100
#     ad_regional_chart = bqplot.Figure(
#         marks=[hist],
#         axes=[x_axis, y_axis],
#         padding_y=0,
#         title="Regional Adoption as a % of World",
#     )
#     ad_regional_chart.layout.width = "100%"


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
