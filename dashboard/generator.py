from bokeh.resources import CDN
from jinja2 import Environment, PackageLoader, Template
from dashboard.charts import make_pie_chart, make_hist_chart
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


def get_all_charts_html():
    all_solutions = get_all_solutions()
    py_solutions = get_py_solutions()

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

    # Regional
    survey_data = get_survey_data()

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

    return charts


def generate_html():
    env = Environment(loader=PackageLoader("dashboard", "templates"),)
    template = env.get_template("index.html")

    charts = get_all_charts_html()
    cdn = CDN.render()

    html = template.render(cdn=cdn, charts=charts)
    return html
