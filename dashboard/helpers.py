import importlib

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
    python_2019_count = 0
    python_2020_count = 0

    for name in py_solutions['solution'].unique():
        solution_module = importlib.import_module("solution." + name)
        obj = solution_module.Scenario()
        if obj.ac.ref_base_adoption is not None:
            python_2020_count += 1
        else:
            python_2019_count += 1

    excel_solutions_count = total_solutions_count - python_2019_count - python_2020_count
    return pd.DataFrame(
        {
            "type": ["Excel Only", "Excel & Python 2020", "Excel & Python 2019"],
            "count": [excel_solutions_count, python_2020_count, python_2019_count],
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


def get_custom_pds_data_basis_counts():
    # data sources in model/customadoption.py. If we add new ones they will be discovered
    # by the code below and added to the dataframe, the ones here will just always be present
    # with a count of zero if no scenario uses them.
    sources = ['tabular', 'linear', 'algorithmic', 'polyfit', 'growth', 'dataframe']
    data = pd.Series(0, index=sources)
    all_solutions = solution_loader.all_solutions()
    for name in all_solutions:
        solution_module = importlib.import_module("solution." + name)
        obj = solution_module.Scenario()
        if hasattr(obj, 'pds_ca'):
            for val in obj.pds_ca.scenarios.values():
                keylist = val.get('data_basis', ['unknown'])
                for key in keylist:
                    if key in data.index:
                        data[key] += 1
                    else:
                        data[key] = 1
    data.index.name = "type"
    data.name = "count"
    return data.reset_index()


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


def get_issues_with_regional_data(land_survey):
    msk_regions = land_survey["has regional data"]
    land_survey = land_survey.loc[msk_regions]

    def check_exceed(val):
        # Values have different types
        # need conversion
        try:
            return int(val) > 0
        except ValueError as e:
            if val == "False":
                return False
            elif val == "True":
                return True

    n = land_survey.shape[0]
    msk_exceeds_world_count = land_survey["ca scen regions exceed world count"].apply(
        check_exceed
    )
    msk_exceeds_regions_count = land_survey[
        "ca scen world exceeds regions count"
    ].apply(check_exceed)
    msk_mismatch = msk_exceeds_world_count | msk_exceeds_regions_count

    msk_exceeds_alloc_count = land_survey["ca scen exceeds alloc count"].apply(
        check_exceed
    )

    no_issues = ((-msk_mismatch) & (-msk_exceeds_alloc_count)).sum()
    exceeds_limits = (msk_exceeds_alloc_count & (-msk_mismatch)).sum()
    regions_mismatch = (msk_mismatch & (-msk_exceeds_alloc_count)).sum()
    both_issues = (msk_mismatch & msk_exceeds_alloc_count).sum()
    return pd.DataFrame(
        {
            "type": ["No Issues", "Exceed Limits", "Regions Mismatch", "Both Issues"],
            "count": [no_issues, exceeds_limits, regions_mismatch, both_issues],
        }
    )
