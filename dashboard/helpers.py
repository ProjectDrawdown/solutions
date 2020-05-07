import importlib
import os.path

import pandas as pd

import solution.factory as solution_loader


def get_py_solutions():
    data = []
    py_solutions = solution_loader.all_solutions_scenarios()
    for name in py_solutions:
        solution_module = importlib.import_module("solution." + name)
        for scenario in solution_module.scenarios.values():
            row = {"solution": name, "scenario": scenario.name}
            row["pds_adoption_basis"] = scenario.soln_pds_adoption_basis
            row["ref_adoption_basis"] = scenario.soln_ref_adoption_basis or "Default"
            data.append(row)
    return pd.json_normalize(data)


def get_excel_python_count(all_solutions, py_solutions):
    total_solutions_count = all_solutions.Solution.nunique()
    python_solutions_count = py_solutions.solution.nunique()

    excel_solutions_count = total_solutions_count - python_solutions_count
    return pd.DataFrame(
        {
            "type": ["Excel Only", "Python & Excel"],
            "count": [excel_solutions_count, python_solutions_count],
        }
    )


def get_scenarios_per_solution(py_solutions):
    return (
        py_solutions.groupby(["solution"])["scenario"]
        .count()
        .sort_values(ascending=False)
        .reset_index()
    )


def get_pds_adoption_basis_counts(py_solutions):
    keys = [
        "Linear",
        "Existing Adoption Prognostications",
        "Bass Diffusion S-Curve",
        "Logistic S-Curve",
        "Fully Customized PDS",
        "Customized S-Curve Adoption",
    ]
    pds_adoption_basis_counts = py_solutions.pds_adoption_basis.value_counts()
    pds_adoption_basis_counts.index.name = "type"
    pds_adoption_basis_counts.name = "count"
    for key in keys:
        if key not in pds_adoption_basis_counts.index:
            pds_adoption_basis_counts[key] = 0

    return pds_adoption_basis_counts.reset_index()


def get_ref_adoption_basis_counts(py_solutions):
    ref_adoption_basis_counts = py_solutions.ref_adoption_basis.value_counts()
    ref_adoption_basis_counts.index.name = "type"
    ref_adoption_basis_counts.name = "count"
    return ref_adoption_basis_counts.reset_index()


def get_regional_nonzero(survey_data, column):

    msk_isnull = survey_data[column].isnull()
    msk_zero = survey_data[column] == 0.0
    zero_count = (msk_zero | msk_isnull).sum()
    nonzero_count = survey_data.shape[0] - zero_count
    return pd.DataFrame(
        {"type": ["nonzero", "zero"], "count": [nonzero_count, zero_count]}
    )


def get_regional_as_percent(survey_data, column):
    msk_non_null = survey_data[column].notnull()
    msk_non_zero = survey_data[column] != 0.0
    return survey_data.loc[msk_non_null & msk_non_zero, column] * 100
