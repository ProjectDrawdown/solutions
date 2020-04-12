"""Test advanced_controls.py."""

import json
import os
import pathlib
import tempfile

import numpy as np
import pandas as pd
import pytest
from numpy import nan
from model import advanced_controls, vma
from model.advanced_controls import fill_missing_regions_from_world
from model import emissionsfactors as ef


datadir = pathlib.Path(__file__).parents[0].joinpath('data')


def test_learning_rate():
    """Test efficiency versus learning rate."""
    ac = advanced_controls.AdvancedControls(
        pds_2014_cost=0, ref_2014_cost=0, conv_2014_cost=0,
        soln_first_cost_efficiency_rate=0.2,
        soln_first_cost_below_conv=True,
        conv_first_cost_efficiency_rate=0.4786,
        soln_fuel_efficiency_factor=0.1)
    assert ac.soln_first_cost_learning_rate == pytest.approx(0.8)
    assert ac.conv_first_cost_learning_rate == pytest.approx(0.5214)
    assert ac.soln_fuel_learning_rate == pytest.approx(0.9)
    ac = advanced_controls.AdvancedControls(
        pds_2014_cost=0, ref_2014_cost=0, conv_2014_cost=0,
        soln_first_cost_efficiency_rate=0.33333333,
        soln_first_cost_below_conv=True,
        conv_first_cost_efficiency_rate=1.0,
        soln_fuel_efficiency_factor=0.0)
    assert ac.soln_first_cost_learning_rate == pytest.approx(0.66666667)
    assert ac.conv_first_cost_learning_rate == pytest.approx(0.0)
    assert ac.soln_fuel_learning_rate == pytest.approx(1.0)


def test_electricity_factors():
    conv_annual_energy_used = 2.117

    class fakeVMA:
        df = pd.DataFrame()
        def avg_high_low(self, key):
            return (0.0, 0.0, 0.0)

    vmas = {'SOLUTION Energy Efficiency Factor': fakeVMA()}

    ac = advanced_controls.AdvancedControls(vmas=vmas,
        conv_annual_energy_used=conv_annual_energy_used)
    assert ac.soln_energy_efficiency_factor == 0
    assert ac.conv_annual_energy_used == pytest.approx(conv_annual_energy_used)
    assert ac.soln_annual_energy_used == 0


def test_lifetime_replacement():
    ac = advanced_controls.AdvancedControls(
        soln_lifetime_capacity=50000, soln_avg_annual_use=1000,
        conv_lifetime_capacity=10000, conv_avg_annual_use=3)
    assert ac.soln_lifetime_replacement == 50
    assert ac.conv_lifetime_replacement == pytest.approx(3333.333333333333)


def test_lifetime_replacement_rounded():
    ac = advanced_controls.AdvancedControls(
        soln_lifetime_capacity=63998.595, soln_avg_annual_use=2844.382,
        conv_lifetime_capacity=1.5, conv_avg_annual_use=1)
    assert ac.soln_lifetime_replacement_rounded == 23
    assert ac.conv_lifetime_replacement_rounded == 2
    ac = advanced_controls.AdvancedControls(
        conv_lifetime_capacity=63998.595, conv_avg_annual_use=2844.382,
        soln_lifetime_capacity=1.5, soln_avg_annual_use=1)
    assert ac.conv_lifetime_replacement_rounded == 23
    assert ac.soln_lifetime_replacement_rounded == 2
    # From Water Efficiency
    ac = advanced_controls.AdvancedControls(
        soln_lifetime_capacity=1086.6259087991305, soln_avg_annual_use=72.44172725327537,
        conv_lifetime_capacity=1629.9388631986958, conv_avg_annual_use=72.44172725327537)
    assert ac.conv_lifetime_replacement_rounded == 23
    assert ac.soln_lifetime_replacement_rounded == 15


def test_replacement_raises_error():
    """ Lifetime replacement values require different inputs for LAND and RRS """
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=None, soln_expected_lifetime=None)
    with pytest.raises(ValueError):
        ac.soln_lifetime_replacement
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=None, soln_expected_lifetime=None)
    with pytest.raises(ValueError):
        ac.soln_lifetime_replacement_rounded
    ac = advanced_controls.AdvancedControls(conv_lifetime_capacity=None, conv_expected_lifetime=None)
    with pytest.raises(ValueError):
        ac.conv_lifetime_replacement
    ac = advanced_controls.AdvancedControls(conv_lifetime_capacity=None, conv_expected_lifetime=None)
    with pytest.raises(ValueError):
        ac.conv_lifetime_replacement_rounded


def test_co2eq_conversion_source():
    ac = advanced_controls.AdvancedControls(co2eq_conversion_source="ar5 with feedback")
    assert ac.co2eq_conversion_source == ef.CO2EQ_SOURCE.AR5_WITH_FEEDBACK
    ac = advanced_controls.AdvancedControls(co2eq_conversion_source=ef.CO2EQ_SOURCE.AR4)
    assert ac.co2eq_conversion_source == ef.CO2EQ_SOURCE.AR4
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(co2eq_conversion_source="???")


def test_emissions_grid():
    ac = advanced_controls.AdvancedControls(
        emissions_grid_source="IPCC Only", emissions_grid_range="high")
    assert ac.emissions_grid_source == ef.GRID_SOURCE.IPCC
    assert ac.emissions_grid_range == ef.GRID_RANGE.HIGH
    ac = advanced_controls.AdvancedControls(
        emissions_grid_source=ef.GRID_SOURCE.META, emissions_grid_range=ef.GRID_RANGE.MEAN)
    assert ac.emissions_grid_source == ef.GRID_SOURCE.META
    assert ac.emissions_grid_range == ef.GRID_RANGE.MEAN
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(emissions_grid_source="???")
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(emissions_grid_range="???")


def test_soln_pds_adoption_args():
    ac = advanced_controls.AdvancedControls(
        soln_pds_adoption_basis="Existing Adoption Prognostications",
        soln_pds_adoption_prognostication_growth="Medium",
        soln_pds_adoption_prognostication_source="test1")
    assert ac.soln_pds_adoption_basis == "Existing Adoption Prognostications"
    assert ac.soln_pds_adoption_prognostication_growth == "Medium"
    assert ac.soln_pds_adoption_prognostication_source == "test1"
    ac = advanced_controls.AdvancedControls(
        soln_pds_adoption_basis="DEFAULT S-Curve",
        soln_pds_adoption_prognostication_growth="Low",
        soln_pds_adoption_prognostication_source="test2")
    assert ac.soln_pds_adoption_basis == "Logistic S-Curve"
    assert ac.soln_pds_adoption_prognostication_growth == "Low"
    assert ac.soln_pds_adoption_prognostication_source == "test2"
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(soln_pds_adoption_basis="???")
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_growth="???")


def test_soln_ref_adoption_args():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_basis="Default")
    assert ac.soln_ref_adoption_basis == "Default"
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_basis="Custom")
    assert ac.soln_ref_adoption_basis == "Custom"
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(soln_ref_adoption_basis="???")


def test_solution_category():
    ac = advanced_controls.AdvancedControls(solution_category="REPLACEMENT")
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.REPLACEMENT
    ac = advanced_controls.AdvancedControls(solution_category="reduction")
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.REDUCTION
    ac = advanced_controls.AdvancedControls(solution_category="LAND")
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.LAND
    ac = advanced_controls.AdvancedControls(solution_category="not applicable")
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.NOT_APPLICABLE
    ac = advanced_controls.AdvancedControls(solution_category="Not_ApPLICaBLe")
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.NOT_APPLICABLE
    ac = advanced_controls.AdvancedControls(solution_category="NA")
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.NOT_APPLICABLE
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(solution_category="invalid")


def test_pds_ref_use_years():
    ac = advanced_controls.AdvancedControls(ref_adoption_use_pds_years=[2014],
                                            pds_adoption_use_ref_years=[2015])
    with pytest.raises(ValueError):
        _ = advanced_controls.AdvancedControls(ref_adoption_use_pds_years=[2014],
                                               pds_adoption_use_ref_years=[2014])

def test_has_var_costs():
    ac = advanced_controls.AdvancedControls(soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
                                            conv_var_oper_cost_per_funit=0.0,
                                            conv_fuel_cost_per_funit=0.0)
    assert ac.has_var_costs
    ac = advanced_controls.AdvancedControls(soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
                                            conv_var_oper_cost_per_funit=0.0)
    assert not ac.has_var_costs


def test_substitute_vma():
    class fakeVMA:
        df = pd.DataFrame(0, index=[0, 1], columns=vma.VMA_columns)
        def avg_high_low(self, key):
            if key == 'mean': return 'mean value'
            if key == 'high': return 'high value'
            if key == 'low': return 'low value'
            return ('mean value', 'high value', 'low value')

    seq_vma = {'Sequestration Rates': fakeVMA()}
    ac = advanced_controls.AdvancedControls(vmas=seq_vma, seq_rate_global='mean')
    assert ac.seq_rate_global == 'mean value'


def test_substitute_vma_passthru_value():
    ac = advanced_controls.AdvancedControls(seq_rate_global=4.3)
    assert ac.seq_rate_global == 4.3

    class fakeVMA:
        df = pd.DataFrame()
        def avg_high_low(self, key):
            return (0.0, 0.0, 0.0)

    vmas = {'Sequestration Rates': fakeVMA()}
    ac = advanced_controls.AdvancedControls(vmas=vmas, seq_rate_global={'value': 4.3})
    assert ac.seq_rate_global == 4.3


def test_substitute_vma_raises():
    ac = advanced_controls.AdvancedControls(vmas={}, seq_rate_global=1)
    assert ac.seq_rate_global == 1
    with pytest.raises(KeyError):
        advanced_controls.AdvancedControls(vmas={}, seq_rate_global='mean')


def test_substitute_vma_handles_raw_value_discrepancy():
    class fakeVMA:
        df = pd.DataFrame(0, index=[0, 1], columns=vma.VMA_columns)
        def avg_high_low(self, key):
            if key == 'mean': return 1.2
            if key == 'high': return 1.4
            if key == 'low': return 1.0
            return (1.2, 1.4, 1.0)

    vmas = {'Sequestration Rates': fakeVMA()}
    ac = advanced_controls.AdvancedControls(vmas=vmas,
            seq_rate_global={'value': 1.1, 'statistic': 'mean'})
    assert ac.seq_rate_global == pytest.approx(1.1)


def test_lookup_vma():
    class fakeVMA:
        def avg_high_low(self, key):
            return (1.2, 1.4, 1.0)

    vmas = {'VMA1': fakeVMA(), 'VMA2': fakeVMA()}
    ac = advanced_controls.AdvancedControls(vmas=vmas,
            vma_values={'VMA1': 2.0, 'statistic': 'mean'})
    assert ac.lookup_vma('VMA1') == 2.0


def test_substitute_vma_regional_statistics():
    vals = {'World': 0, 'OECD90': 1, 'Eastern Europe': 2, 'Asia (Sans Japan)': 3,
            'Middle East and Africa': 4, 'Latin America': 5, 'China': 0, 'India': 0,
            'EU': 0, 'USA': 0}

    class fakeVMA:
        df = pd.DataFrame(0, index=[0, 1], columns=vma.VMA_columns)
        def avg_high_low(self, key, region=None):
            if region and key == 'mean': return vals[region]
            return (None, None, None)

    vmas = {'SOLUTION First Cost per Implementation Unit': fakeVMA()}

    ac = advanced_controls.AdvancedControls(vmas=vmas, pds_2014_cost='mean per region')
    expected = pd.Series(data=vals, name='regional values')
    pd.testing.assert_series_equal(expected, ac.pds_2014_cost)


def test_substitute_vma_not_has_data():
    class fakeVMA:
        def __init__(self):
            self.v = (np.nan, np.nan, np.nan)

        def avg_high_low(self, key):
            if key == 'mean': return self.v[0]
            if key == 'high': return self.v[1]
            if key == 'low': return self.v[2]
            return v

    v = fakeVMA()
    v.df = pd.DataFrame(0, index=[0, 1], columns=vma.VMA_columns)
    vmas = {'Sequestration Rates': v}
    with pytest.raises(KeyError):
        _ = advanced_controls.AdvancedControls(vmas=vmas, seq_rate_global='mean')

    v.v = (1, 2, 3)
    ac = advanced_controls.AdvancedControls(vmas=vmas, seq_rate_global='mean')
    assert ac.seq_rate_global == 1


def test_yield_coeff():
    ac = advanced_controls.AdvancedControls(yield_from_conv_practice=2,
            yield_gain_from_conv_to_soln=4, disturbance_rate=0.25)
    assert ac.yield_coeff == 6


def test_fill_missing_regions_from_world():
    vals = {'World': 2, 'OECD90': 1, 'Eastern Europe': nan, 'Asia (Sans Japan)': 3,
            'Middle East and Africa': 4, 'Latin America': 5, 'China': 0, 'India': nan,
            'EU': 0, 'USA': 0}
    data = pd.Series(data=vals, name='regional values')
    exp_vals = {'World': 2, 'OECD90': 1, 'Eastern Europe': 2, 'Asia (Sans Japan)': 3,
            'Middle East and Africa': 4, 'Latin America': 5, 'China': 0, 'India': nan,
            'EU': 0, 'USA': 0}
    expected = pd.Series(data=exp_vals, name='regional values')
    pd.testing.assert_series_equal(expected, fill_missing_regions_from_world(data))


def test_fill_missing_regions_from_world_passthru():
    assert fill_missing_regions_from_world(1) == 1


def test_from_json():
    l = advanced_controls.load_scenarios_from_json(directory=datadir.joinpath('ac'), vmas=None)
    assert len(l) == 1
    ac = l['ac_dataclass']
    assert ac.pds_2014_cost == pytest.approx(1.0)
    assert ac.ref_2014_cost == pytest.approx(2.0)
    assert ac.conv_2014_cost == pytest.approx(3.0)
    assert ac.soln_first_cost_efficiency_rate == pytest.approx(4.0)
    assert ac.conv_first_cost_efficiency_rate == pytest.approx(5.0)


def test_to_json():
    (f, jsfile) = tempfile.mkstemp()
    ac = advanced_controls.AdvancedControls(
        soln_lifetime_capacity=1.0, soln_avg_annual_use=2.0,
        conv_lifetime_capacity=3.0, conv_avg_annual_use=4.0,
        jsfile=jsfile)
    ac.write_to_json_file()
    with open(jsfile, 'r') as fid:
        js = json.loads(fid.read())
    os.unlink(jsfile)
    assert js['soln_lifetime_capacity'] == 1.0
    assert js['soln_avg_annual_use'] == 2.0
    assert js['conv_lifetime_capacity'] == 3.0
    assert js['conv_avg_annual_use'] == 4.0


def test_vma_to_param_names():
    result = advanced_controls.get_vma_for_param('yield_gain_from_conv_to_soln')
    assert 'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)' in result
    result = advanced_controls.get_vma_for_param('conv_fixed_oper_cost_per_iunit')
    assert 'CONVENTIONAL Operating Cost per Functional Unit per Annum' in result
    assert 'CONVENTIONAL Fixed Operating Cost (FOM)' in result
    result = advanced_controls.get_param_for_vma_name('t C storage in Protected Landtype')
    assert result == 'tC_storage_in_protected_land_type'
    result = advanced_controls.get_param_for_vma_name('CONVENTIONAL Fixed Operating Cost (FOM)')
    assert result == 'conv_fixed_oper_cost_per_iunit'
