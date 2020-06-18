from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
from mock import patch

from dashboard.helpers import (
    get_excel_python_count,
    get_issues_with_regional_data,
    get_pds_adoption_basis_counts,
    get_py_solutions,
    get_ref_adoption_basis_counts,
    get_regional_as_percent,
    get_regional_nonzero,
    get_scenarios_per_solution,
)

mock_all_solutions = pd.DataFrame(
    {
        "Solution": {
            50: "Perennial Biomass",
            36: "Mass Transit",
            18: "Managed Grazing",
            66: "Farmland Irrigation",
            76: "Carpooling",
            19: "Nuclear",
            43: "LED Lighting (Commercial)",
            58: "Bike Infrastructure",
            55: "Industrial Recycling",
            57: "Landfill Methane",
        },
        "DirName": {
            50: "perennialbioenergy",
            36: "masstransit",
            18: "managedgrazing",
            66: "irrigationefficiency",
            76: "carpooling",
            19: "nuclear",
            43: "leds_commercial",
            58: "bikeinfrastructure",
            55: np.nan,
            57: "landfillmethane",
        },
        "Sector": {
            50: "Land Use",
            36: "Transport",
            18: "Food",
            66: "Food",
            76: "Transport",
            19: "Electricity Generation",
            43: "Buildings and Cities",
            58: "Buildings and Cities",
            55: "Materials",
            57: "Buildings and Cities",
        },
    }
)
mock_py_solutions = pd.DataFrame(
    [
        [
            "bamboo",
            "PDS-66p2050-Drawdown-CustomPDS-High-July2019",
            "Fully Customized PDS",
            "Default",
        ],
        [
            "bamboo",
            "PDS-38p2050-Plausible-PDScustom-high growth-BookVersion1",
            "Fully Customized PDS",
            "Default",
        ],
        [
            "bamboo",
            "PDS-41p2050-Plausible-CustomPDS-Avg-July2019",
            "Fully Customized PDS",
            "Default",
        ],
        [
            "bamboo",
            "PDS-69p2050-Optimum-PDScustom-high-BookVersion1",
            "Fully Customized PDS",
            "Default",
        ],
        [
            "bamboo",
            "PDS-47p2050-Drawdown-PDScustom-avg-BookVersion1",
            "Fully Customized PDS",
            "Default",
        ],
        [
            "bamboo",
            "PDS-85p2050-Optimum-PDSCustom-max-Nov2019",
            "Fully Customized PDS",
            "Custom",
        ],
        [
            "biochar",
            "PDS-16p2050-Drawdown-CustomPDS-High-Jan2020",
            "Fully Customized PDS",
            "Custom",
        ],
        [
            "biochar",
            "PDS-16p2050-Drawdown-PDScustom-high-Bookedition1",
            "Fully Customized PDS",
            "Default",
        ],
        [
            "nuclear",
            "PDS-10p2050-Drawdown (Book Ed. 1)",
            "Existing Adoption Prognostications",
            "Default",
        ],
        [
            "nuclear",
            "PDS-0p2050-Optimum2020",
            "Existing Adoption Prognostications",
            "Default",
        ],
    ],
    columns=["solution", "scenario", "pds_adoption_basis", "ref_adoption_basis"],
)


mock_survey_data = pd.DataFrame(
    [
        ["biochar:PDS-20p2050-Optimum-PDScustom-max-Bookedition1", 0.0, 0.0, 0.99],
        [
            "perennialbioenergy:PDS-72p2050-Plausible-PDScustom-avg-BookVersion1",
            np.nan,
            0.0,
            0.99,
        ],
        ["improvedcookstoves:PDS3-25p2050_Linear to 25% (Book Ed.1)", 1.10, 1.10, 1.0],
        ["biogas:PDS-1p2050-Optimum (Book Ed.1)", 0.71, 0.003, 0.97],
        [
            "tropicaltreestaples:PDS-42p2050-Drawdown-PDSCustom-avg-Nov2019",
            np.nan,
            0.0,
            0.99,
        ],
        ["solarpvutil:PDS-20p2050-Plausible2020", 1.09, np.nan, 0.94],
        [
            "trains:PDS1-4p2050-Doubled Historical Electrification Rate (Book Ed.1)",
            0.0,
            0.0,
            0.9861,
        ],
        [
            "multistrataagroforestry:PDS-12p2050-Plausible-CustomPDS-low-aug2019",
            np.nan,
            0.0,
            0.0,
        ],
        [
            "solarhotwater:PDS2-44p2050-Mean of Custom Scen. (Book Ed.1)",
            0.927,
            0.0,
            0.992,
        ],
        [
            "tropicaltreestaples:PDS-52p2050-Plausible-PDScustom-low-BookVersion1",
            np.nan,
            0.0,
            0.98,
        ],
    ],
    columns=["Solution", "RegionalFractionTAM", "RegionalFractionAdoption", "Rvalue"],
)


def _mock_factory():
    return {
        "afforestation": (
            "afforestation",
            ["PDS-Drawdown-Nov2019", "PDS-Plausible-Nov2019",],
        ),
        "airplanes": (
            "airplanes",
            ["PDS1-Efficiency (Book Ed.1)", "PDS2-Manufacturer (Book Ed.1)",],
        ),
        "altcement": ("altcement", ["PDS1-Availability (Book Ed.1)"],),
        "bamboo": (
            "bamboo",
            ["PDS-Optimum-CustomPDS", "PDS-BookVersion1", "PDS-CustomPDS-July2019",],
        ),
    }


def _mock_importlib(name):
    @dataclass
    class Scenario:
        name: str
        soln_pds_adoption_basis: str
        soln_ref_adoption_basis: str

    @dataclass
    class Module:
        scenarios: dict

    return Module({"a": Scenario("a", "a", None), "b": Scenario("b", "b", "Custom")})


@patch("dashboard.helpers.solution_loader.all_solutions_scenarios", _mock_factory)
@patch("dashboard.helpers.importlib.import_module", _mock_importlib)
def test_get_py_solutions():
    df = get_py_solutions()
    pd.testing.assert_frame_equal(
        df,
        pd.DataFrame(
            {
                "solution": [
                    "afforestation",
                    "afforestation",
                    "airplanes",
                    "airplanes",
                    "altcement",
                    "altcement",
                    "bamboo",
                    "bamboo",
                ],
                "scenario": ["a", "b", "a", "b", "a", "b", "a", "b",],
                "pds_adoption_basis": ["a", "b", "a", "b", "a", "b", "a", "b",],
                "ref_adoption_basis": [
                    "Default",
                    "Custom",
                    "Default",
                    "Custom",
                    "Default",
                    "Custom",
                    "Default",
                    "Custom",
                ],
            }
        ),
    )


def test_get_scenarios_per_solution():
    result = get_scenarios_per_solution(mock_py_solutions)
    expected = pd.DataFrame(
        {"solution": ["bamboo", "nuclear", "biochar"], "scenario": [6, 2, 2]}
    )
    pd.testing.assert_frame_equal(result, expected)


def test_get_pds_adoption_basis_counts():
    result = get_pds_adoption_basis_counts(mock_py_solutions)
    expected = pd.DataFrame(
        {
            "type": [
                "Fully Customized PDS",
                "Existing Adoption Prognostications",
                "Linear",
                "Bass Diffusion S-Curve",
                "Logistic S-Curve",
                "Customized S-Curve Adoption",
            ],
            "count": [8, 2, 0, 0, 0, 0],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_get_ref_adoption_basis_counts():
    result = get_ref_adoption_basis_counts(mock_py_solutions)
    expected = pd.DataFrame({"type": ["Default", "Custom"], "count": [8, 2]})
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    "column,count",
    [("RegionalFractionTAM", [4, 6]), ("RegionalFractionAdoption", [2, 8])],
)
def test_get_regional_nonzero(column, count):
    result = get_regional_nonzero(mock_survey_data, column)
    expected = pd.DataFrame({"type": ["nonzero", "zero"], "count": count})
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    "column,count",
    [
        ("RegionalFractionTAM", [110.00000000000001, 71.0, 109.00000000000001, 92.7]),
        ("RegionalFractionAdoption", [110.00000000000001, 0.3]),
    ],
)
def test_get_regional_percent(column, count):
    result = get_regional_as_percent(mock_survey_data, column)
    expected = pd.Series(count)
    # Only check values
    np.testing.assert_array_equal(result.values, expected.values)


def test_get_issues_with_regional_data():
    land_survey = pd.DataFrame(
        {
            "has regional data": [True, True, True, True, True, False],
            "ca scen regions exceed world count": ["False", 2, 1, 0, "False", 0],
            "ca scen world exceeds regions count": ["True", "0", 1, 0, "0", 1],
            "ca scen exceeds alloc count": ["False", 1, 0, 0, 1, 1],
        }
    )
    result = get_issues_with_regional_data(land_survey)
    expected = pd.DataFrame(
        {
            "type": ["No Issues", "Exceed Limits", "Regions Mismatch", "Both Issues"],
            "count": [1, 1, 2, 1],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_get_excel_python_count():
    result = get_excel_python_count(mock_all_solutions, mock_py_solutions)
    expected = pd.DataFrame(
            {"type": {0: "Excel Only", 1: "Excel & Python 2020", 2: "Excel & Python 2019"},
                "count": {0: 7, 1: 3, 2: 0}}
    )

    pd.testing.assert_frame_equal(result, expected)
