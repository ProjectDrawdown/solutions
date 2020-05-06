from bokeh.resources import CDN
from jinja2 import Environment, PackageLoader, Template
from dashboard.charts import make_pie_chart
from dashboard.helpers import (
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


def get_all_charts_html():
    all_solutions = get_all_solutions()
    py_solutions = get_py_solutions()

    survey_data = get_survey_data()

    excel_python_count = get_excel_python_count(all_solutions, py_solutions)
    pds_adoption_basis_counts = get_pds_adoption_basis_counts(py_solutions)
    ref_adoption_basis_counts = get_ref_adoption_basis_counts(py_solutions)
    scenarios_per_solution = get_scenarios_per_solution(py_solutions)

    regional_non_zero_tam = get_regional_nonzero_tam(survey_data)
    regional_nonzero_adoption = get_regional_nonzero_adoption(survey_data)

    charts = {}
    charts["solution_implementation"] = make_pie_chart(
        excel_python_count, "type", "count", "Solution Implementation", as_html=True
    )
    charts["pds_adoption_basis"] = make_pie_chart(
        pds_adoption_basis_counts, "type", "count", "PDS Adoption Basis", as_html=True
    )
    charts["ref_adoption_basis_counts"] = make_pie_chart(
        ref_adoption_basis_counts, "type", "count", "REF Adoption Basis", as_html=True
    )
    return charts


def generate_html():
    env = Environment(loader=PackageLoader("dashboard", "templates"),)
    template = env.get_template("index.html")

    charts = get_all_charts_html()
    cdn = CDN.render()

    html = template.render(cdn=cdn, charts=charts)
    return html
