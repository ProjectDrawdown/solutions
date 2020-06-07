from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
from mock import patch

from dashboard.generator import (
    _get_summary_charts,
    _get_regional_charts,
    _get_land_solution_analytics,
    _get_scenarios_analytics,
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

mock_land_survey = pd.DataFrame(
    {
        "% tla": {
            "forestprotection": 92.82261256755086,
            "afforestation": 100.0,
            "peatlands": 99.03852328101631,
        },
        "% world alloc": {
            "forestprotection": 8.496675659518786,
            "afforestation": 5.756416521434398,
            "peatlands": 2.9570790808303613,
        },
        "avg abatement cost": {
            "forestprotection": -0.0,
            "afforestation": 2.3441063620721785,
            "peatlands": -0.0,
        },
        "model type": {
            "forestprotection": "protect",
            "afforestation": "core",
            "peatlands": "core",
        },
        "has regional data": {
            "forestprotection": False,
            "afforestation": True,
            "peatlands": False,
        },
        "ca exceeds alloc": {
            "forestprotection": False,
            "afforestation": "False",
            "peatlands": "False",
        },
        "ca exceeds max tla": {
            "forestprotection": False,
            "afforestation": False,
            "peatlands": False,
        },
        "ca scen exceeds alloc count": {
            "forestprotection": "0",
            "afforestation": "4",
            "peatlands": "0",
        },
        "ca scen exceeds max tla count": {
            "forestprotection": "0",
            "afforestation": "0",
            "peatlands": "0",
        },
        "ca scen regions exceed world count": {
            "forestprotection": 0,
            "afforestation": 0,
            "peatlands": 0,
        },
        "ca scen world exceeds regions count": {
            "forestprotection": 0,
            "afforestation": 1,
            "peatlands": 0,
        },
    }
)
mock_land_survey.index.name = "Solution"

mock_scenarios = pd.DataFrame(
    {
        "solution_category": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "vmas": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "pds_2014_cost": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "ref_2014_cost": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_2014_cost": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_first_cost_efficiency_rate": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "conv_first_cost_efficiency_rate": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "soln_first_cost_below_conv": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_energy_efficiency_factor": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "conv_annual_energy_used": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_annual_energy_used": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_fuel_consumed_per_funit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_fuel_efficiency_factor": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_fuel_emissions_factor": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_fuel_emissions_factor": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_emissions_per_funit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_emissions_per_funit": {"landfillmethane": 2.0, "walkablecities": 1.0},
        "ch4_is_co2eq": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "n2o_is_co2eq": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "co2eq_conversion_source": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "ch4_co2_per_twh": {"landfillmethane": 2.0, "walkablecities": 1.0},
        "n2o_co2_per_twh": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_indirect_co2_per_iunit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_indirect_co2_per_unit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_indirect_co2_is_iunits": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_lifetime_capacity": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_avg_annual_use": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_lifetime_capacity": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_avg_annual_use": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "report_start_year": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "report_end_year": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_var_oper_cost_per_funit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_fixed_oper_cost_per_iunit": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "soln_fuel_cost_per_funit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_var_oper_cost_per_funit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_fixed_oper_cost_per_iunit": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "conv_fuel_cost_per_funit": {"landfillmethane": 2.0, "walkablecities": 1.0},
        "npv_discount_rate": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "emissions_use_co2eq": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "emissions_grid_source": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "emissions_grid_range": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_ref_adoption_regional_data": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "soln_pds_adoption_regional_data": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "soln_ref_adoption_basis": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_ref_adoption_custom_name": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "soln_pds_adoption_basis": {"landfillmethane": 1.0, "walkablecities": 3.0},
        "soln_pds_adoption_custom_name": {
            "landfillmethane": 1.0,
            "walkablecities": 2.0,
        },
        "soln_pds_adoption_prognostication_source": {
            "landfillmethane": 3.0,
            "walkablecities": 2.0,
        },
        "soln_pds_adoption_prognostication_trend": {
            "landfillmethane": 2.0,
            "walkablecities": 2.0,
        },
        "soln_pds_adoption_prognostication_growth": {
            "landfillmethane": 1.0,
            "walkablecities": 2.0,
        },
        "pds_source_post_2014": {"landfillmethane": 3.0, "walkablecities": 1.0},
        "ref_source_post_2014": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "source_until_2014": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "ref_adoption_use_pds_years": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "pds_adoption_use_ref_years": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "pds_base_adoption": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "pds_adoption_final_percentage": {
            "landfillmethane": 1.0,
            "walkablecities": 2.0,
        },
        "pds_adoption_s_curve_innovation": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "pds_adoption_s_curve_imitation": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "tco2eq_reduced_per_land_unit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "tco2eq_rplu_rate": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "tco2_reduced_per_land_unit": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "tco2_rplu_rate": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "tn2o_co2_reduced_per_land_unit": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "tn2o_co2_rplu_rate": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "tch4_co2_reduced_per_land_unit": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "tch4_co2_rplu_rate": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "emissions_use_agg_co2eq": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "seq_rate_global": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "seq_rate_per_regime": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "degradation_rate": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "disturbance_rate": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "global_multi_for_regrowth": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "soln_expected_lifetime": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "conv_expected_lifetime": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "yield_from_conv_practice": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "yield_gain_from_conv_to_soln": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "use_custom_tla": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "harvest_frequency": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "carbon_not_emitted_after_harvesting": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "avoided_deforest_with_intensification": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "delay_protection_1yr": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "delay_regrowth_1yr": {"landfillmethane": 1.0, "walkablecities": 1.0},
        "include_unprotected_land_in_regrowth_calcs": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "land_annual_emissons_lifetime": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
        "tC_storage_in_protected_land_type": {
            "landfillmethane": 1.0,
            "walkablecities": 1.0,
        },
    }
)


@pytest.mark.slow
def test__get_summary_charts():
    result = _get_summary_charts(mock_all_solutions, mock_py_solutions)
    assert sorted(result.keys()) == [
        "custom_pds_data_basis_counts",
        "num_scenario_per_solution",
        "pds_adoption_basis",
        "ref_adoption_basis_counts",
        "solution_implementation",
    ]


def test_get_regional_charts():
    result = _get_regional_charts(mock_survey_data)
    assert sorted(result.keys()) == [
        "pds_adoption_r_squared",
        "regional_Adoption_percent",
        "regional_TAM_percent",
        "regional_nonzero_Adoption",
        "regional_nonzero_TAM",
    ]


def test_get_land_solution_analytics():
    result = _get_land_solution_analytics(mock_land_survey)

    assert sorted(result.keys()) == [
        "% tla",
        "% world alloc",
        "avg abatement cost",
        "has_regions",
        "issues_with_regional_data",
    ]


def test_get_scenarios_analytics():
    result = _get_scenarios_analytics(mock_scenarios)

    assert sorted(result.keys()) == ["scenarios_comparison"]
