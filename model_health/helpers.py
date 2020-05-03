import importlib
import os.path

import pandas as pd

import solution.factory as solution_loader

SOLUTIONS_PATH = os.path.join("data", "overview", "solutions.csv")
SURVEY_PATH = os.path.join("data", "health", "survey.csv")


def get_all_solutions():
    return pd.read_csv(
        SOLUTIONS_PATH,
        index_col=False,
        skipinitialspace=True,
        header=0,
        skip_blank_lines=True,
        comment="#",
    )


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
    return {
        "Excel Only": excel_solutions_count,
        "Python & Excel": python_solutions_count,
    }


def get_scenarios_per_solution(py_solutions):
    return (
        py_solutions.groupby(["solution"])["scenario"]
        .count()
        .sort_values(ascending=False)
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
    pds_adoption_basis_counts = py_solutions.pds_adoption_basis.value_counts().to_dict()
    for key in keys:
        if key not in pds_adoption_basis_counts:
            pds_adoption_basis_counts[key] = 0

    return pds_adoption_basis_counts


def get_ref_adoption_basis_count(py_solutions):
    return py_solutions.ref_adoption_basis.value_counts().to_dict()


def get_survey_data():
    return pd.read_csv(
        SURVEY_PATH,
        index_col=False,
        skipinitialspace=True,
        header=0,
        skip_blank_lines=True,
        comment="#",
    )


def get_regional_nonzero_tam(survey_data):

    msk_isnull = survey_data["RegionalFractionTAM"].isnull()
    msk_zero = survey_data["RegionalFractionTAM"] == 0.0
    zero_count = (msk_zero | msk_isnull).sum()
    nonzero_count = survey_data.shape[0] - zero_count
    return {
        "nonzero_count": nonzero_count,
        "zero_count": zero_count,
    }


def get_regional_nonzero_adoption(survey_data):

    msk_isnull = survey_data["RegionalFractionAdoption"].isnull()
    msk_zero = survey_data["RegionalFractionAdoption"] == 0.0
    zero_count = (msk_zero | msk_isnull).sum()
    nonzero_count = survey_data.shape[0] - zero_count
    return {
        "nonzero_count": nonzero_count,
        "zero_count": zero_count,
    }


def get_regional_as_percent(survey_data, column):
    msk_non_null = survey_data[column].notnull()
    msk_non_zero = survey_data[column] != 0.0
    return survey_data.loc[msk_non_null & msk_non_zero, column] * 100
