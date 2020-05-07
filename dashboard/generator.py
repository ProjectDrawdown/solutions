import os

import pandas as pd
from bokeh.resources import CDN
from jinja2 import Environment, PackageLoader, Template

from dashboard.charts import make_hist_chart, make_pie_chart, make_comparison_chart
from dashboard.helpers import (
    get_excel_python_count,
    get_pds_adoption_basis_counts,
    get_py_solutions,
    get_ref_adoption_basis_counts,
    get_regional_as_percent,
    get_regional_nonzero,
    get_scenarios_per_solution,
)

SOLUTIONS_PATH = os.path.join("data", "overview", "solutions.csv")
SURVEY_PATH = os.path.join("data", "health", "survey.csv")
LAND_SURVEY_PATH = os.path.join("data", "health", "landsurvey.csv")


def _get_summary_charts(all_solutions, py_solutions):
    excel_python_count = get_excel_python_count(all_solutions, py_solutions)
    pds_adoption_basis_counts = get_pds_adoption_basis_counts(py_solutions)
    ref_adoption_basis_counts = get_ref_adoption_basis_counts(py_solutions)
    scenarios_per_solution = get_scenarios_per_solution(py_solutions)

    charts = {}
    charts["solution_implementation"] = make_pie_chart(
        excel_python_count, "type", "count", "Solution Implementation"
    )
    charts["pds_adoption_basis"] = make_pie_chart(
        pds_adoption_basis_counts, "type", "count", "PDS Adoption Basis"
    )
    charts["ref_adoption_basis_counts"] = make_pie_chart(
        ref_adoption_basis_counts, "type", "count", "REF Adoption Basis"
    )
    charts["num_scenario_per_solution"] = make_hist_chart(
        scenarios_per_solution.scenario,
        "Num scenarios per solution",
        "scenario",
        "solution",
        bins=15,
    )

    return charts


def _get_regional_charts(survey_data):
    charts = {}
    for type_ in ["TAM", "Adoption"]:
        col = f"RegionalFraction{type_}"
        regional_non_zero = get_regional_nonzero(survey_data, col)
        regional_percent = get_regional_as_percent(survey_data, col)

        charts[f"regional_nonzero_{type_}"] = make_pie_chart(
            regional_non_zero, "type", "count", f"Has Regional {type_} Data?"
        )

        charts[f"regional_{type_}_percent"] = make_hist_chart(
            regional_percent,
            f"Regional {type_} as % of the World",
            "percentage",
            "number of scenarios",
            bins=20,
        )

    charts[f"pds_adoption_r_squared"] = make_hist_chart(
        survey_data["Rvalue"].dropna() ** 2,
        f"Linearity of PDS Adoption",
        "R squared value",
        "number of scenarios",
        bins=30,
    )
    return charts


def _get_land_solution_analytics(land_survey):
    charts = {}
    for col, title in [
        ("% tla", "% of land allocation reached"),
        ("% world alloc", "% of World land allocated to solution"),
        ("avg abatement cost", "Average abatement cost ($/tCO2)"),
    ]:
        charts[col] = make_comparison_chart(land_survey[col], col, "Solution", title)

    has_regions = (
        land_survey["has regional data"]
        .map({True: "Yes", False: "No"})
        .value_counts()
        .reset_index()
    )
    has_regions.columns = ["has_region", "count"]

    charts["has_regions"] = make_pie_chart(
        has_regions,
        "has_region",
        "count",
        "Has regional adoption data? (Land solutions)",
    )

    return charts


def get_all_charts():
    all_solutions = pd.read_csv(
        SOLUTIONS_PATH,
        index_col=False,
        skipinitialspace=True,
        header=0,
        skip_blank_lines=True,
        comment="#",
    )
    py_solutions = get_py_solutions()

    summary_charts = _get_summary_charts(all_solutions, py_solutions)

    survey_data = pd.read_csv(
        SURVEY_PATH,
        index_col=False,
        skipinitialspace=True,
        header=0,
        skip_blank_lines=True,
        comment="#",
    )
    regional_charts = _get_regional_charts(survey_data)

    land_survey = pd.read_csv(LAND_SURVEY_PATH, index_col=0)
    land_survey_charts = _get_land_solution_analytics(land_survey)

    charts = dict(summary_charts, **regional_charts)
    charts.update(land_survey_charts)
    return charts


def generate_html():
    env = Environment(loader=PackageLoader("dashboard", "templates"),)
    template = env.get_template("index.html")

    charts = get_all_charts()
    cdn = CDN.render()

    html = template.render(cdn=cdn, charts=charts)
    return html
