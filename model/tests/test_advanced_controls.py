"""Test advanced_controls.py."""  # by Denton Gentry
# by Denton Gentry
import pytest  # by Denton Gentry
from unittest import mock
from model import advanced_controls, vma
from model import emissionsfactors as ef  # by Denton Gentry


# by Denton Gentry
# by Denton Gentry
def test_learning_rate():  # by Denton Gentry
    """Test efficiency versus learning rate."""  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        pds_2014_cost=0, ref_2014_cost=0, conv_2014_cost=0,  # by Denton Gentry
        soln_first_cost_efficiency_rate=0.2,  # by Denton Gentry
        soln_first_cost_below_conv=True,  # by Denton Gentry
        conv_first_cost_efficiency_rate=0.4786,  # by Denton Gentry
        soln_fuel_efficiency_factor=0.1)  # by Denton Gentry
    assert ac.soln_first_cost_learning_rate == pytest.approx(0.8)  # by Denton Gentry
    assert ac.conv_first_cost_learning_rate == pytest.approx(0.5214)  # by Denton Gentry
    assert ac.soln_fuel_learning_rate == pytest.approx(0.9)  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        pds_2014_cost=0, ref_2014_cost=0, conv_2014_cost=0,  # by Denton Gentry
        soln_first_cost_efficiency_rate=0.33333333,  # by Denton Gentry
        soln_first_cost_below_conv=True,  # by Denton Gentry
        conv_first_cost_efficiency_rate=1.0,  # by Denton Gentry
        soln_fuel_efficiency_factor=0.0)  # by Denton Gentry
    assert ac.soln_first_cost_learning_rate == pytest.approx(0.66666667)  # by Denton Gentry
    assert ac.conv_first_cost_learning_rate == pytest.approx(0.0)  # by Denton Gentry
    assert ac.soln_fuel_learning_rate == pytest.approx(1.0)  # by Denton Gentry


# by Denton Gentry
def test_electricity_factors():  # by Denton Gentry
    soln_energy_efficiency_factor = ""  # by Denton Gentry
    conv_annual_energy_used = 2.117  # by Denton Gentry
    soln_annual_energy_used = None  # by Denton Gentry
    # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        soln_energy_efficiency_factor=soln_energy_efficiency_factor,  # by Denton Gentry
        conv_annual_energy_used=conv_annual_energy_used,  # by Denton Gentry
        soln_annual_energy_used=soln_annual_energy_used)  # by Denton Gentry
    assert ac.soln_energy_efficiency_factor == 0  # by Denton Gentry
    assert ac.conv_annual_energy_used == pytest.approx(conv_annual_energy_used)  # by Denton Gentry
    assert ac.soln_annual_energy_used == 0  # by Denton Gentry
    # by Denton Gentry


def test_lifetime_replacement():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        soln_lifetime_capacity=50000, soln_avg_annual_use=1000,  # by Denton Gentry
        conv_lifetime_capacity=10000, conv_avg_annual_use=3)  # by Denton Gentry
    assert ac.soln_lifetime_replacement == 50  # by Denton Gentry
    assert ac.conv_lifetime_replacement == pytest.approx(3333.333333333333)  # by Denton Gentry
    # by Denton Gentry


def test_lifetime_replacement_rounded():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        soln_lifetime_capacity=63998.595, soln_avg_annual_use=2844.382,  # by Denton Gentry
        conv_lifetime_capacity=1.5, conv_avg_annual_use=1)  # by Denton Gentry
    assert ac.soln_lifetime_replacement_rounded == 23  # by Denton Gentry
    assert ac.conv_lifetime_replacement_rounded == 2  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        conv_lifetime_capacity=63998.595, conv_avg_annual_use=2844.382,  # by Denton Gentry
        soln_lifetime_capacity=1.5, soln_avg_annual_use=1)  # by Denton Gentry
    assert ac.conv_lifetime_replacement_rounded == 23  # by Denton Gentry
    assert ac.soln_lifetime_replacement_rounded == 2  # by Denton Gentry
    # From Water Efficiency  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        soln_lifetime_capacity=1086.6259087991305, soln_avg_annual_use=72.44172725327537,  # by Denton Gentry
        conv_lifetime_capacity=1629.9388631986958, conv_avg_annual_use=72.44172725327537)  # by Denton Gentry
    assert ac.conv_lifetime_replacement_rounded == 23  # by Denton Gentry
    assert ac.soln_lifetime_replacement_rounded == 15  # by Denton Gentry
    # by Denton Gentry


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


def test_co2eq_conversion_source():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(co2eq_conversion_source="ar5 with feedback")  # by Denton Gentry
    assert ac.co2eq_conversion_source == ef.CO2EQ_SOURCE.AR5_WITH_FEEDBACK  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(co2eq_conversion_source=ef.CO2EQ_SOURCE.AR4)  # by Denton Gentry
    assert ac.co2eq_conversion_source == ef.CO2EQ_SOURCE.AR4  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(co2eq_conversion_source="???")  # by Denton Gentry
    # by Denton Gentry


def test_emissions_grid():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        emissions_grid_source="IPCC Only", emissions_grid_range="high")  # by Denton Gentry
    assert ac.emissions_grid_source == ef.GRID_SOURCE.IPCC  # by Denton Gentry
    assert ac.emissions_grid_range == ef.GRID_RANGE.HIGH  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        emissions_grid_source=ef.GRID_SOURCE.META, emissions_grid_range=ef.GRID_RANGE.MEAN)  # by Denton Gentry
    assert ac.emissions_grid_source == ef.GRID_SOURCE.META  # by Denton Gentry
    assert ac.emissions_grid_range == ef.GRID_RANGE.MEAN  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(emissions_grid_source="???")  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(emissions_grid_range="???")  # by Denton Gentry
    # by Denton Gentry


def test_soln_pds_adoption_args():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        soln_pds_adoption_basis="Existing Adoption Prognostications",  # by Denton Gentry
        soln_pds_adoption_prognostication_growth="Medium",  # by Denton Gentry
        soln_pds_adoption_prognostication_source="test1")  # by Denton Gentry
    assert ac.soln_pds_adoption_basis == "Existing Adoption Prognostications"  # by Denton Gentry
    assert ac.soln_pds_adoption_prognostication_growth == "Medium"  # by Denton Gentry
    assert ac.soln_pds_adoption_prognostication_source == "test1"  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(  # by Denton Gentry
        soln_pds_adoption_basis="DEFAULT S-Curve",  # by Denton Gentry
        soln_pds_adoption_prognostication_growth="Low",  # by Denton Gentry
        soln_pds_adoption_prognostication_source="test2")  # by Denton Gentry
    assert ac.soln_pds_adoption_basis == "Logistic S-Curve"  # by Denton Gentry
    assert ac.soln_pds_adoption_prognostication_growth == "Low"  # by Denton Gentry
    assert ac.soln_pds_adoption_prognostication_source == "test2"  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(soln_pds_adoption_basis="???")  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_growth="???")  # by Denton Gentry
    # by Denton Gentry


def test_soln_ref_adoption_args():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_basis="Default")  # by Denton Gentry
    assert ac.soln_ref_adoption_basis == "Default"  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_basis="Custom")  # by Denton Gentry
    assert ac.soln_ref_adoption_basis == "Custom"  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(soln_ref_adoption_basis="???")  # by Denton Gentry
    # by Denton Gentry


def test_solution_category():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(solution_category="REPLACEMENT")  # by Denton Gentry
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.REPLACEMENT  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(solution_category="reduction")  # by Denton Gentry
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.REDUCTION  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(solution_category="LAND")
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.LAND
    ac = advanced_controls.AdvancedControls(solution_category="not applicable")  # by Denton Gentry
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.NOT_APPLICABLE  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(solution_category="Not_ApPLICaBLe")  # by Denton Gentry
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.NOT_APPLICABLE  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(solution_category="NA")  # by Denton Gentry
    assert ac.solution_category == advanced_controls.SOLUTION_CATEGORY.NOT_APPLICABLE  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(solution_category="invalid")  # by Denton Gentry
    # by Denton Gentry


def test_pds_ref_use_years():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(ref_adoption_use_pds_years=[2014],  # by Denton Gentry
                                            pds_adoption_use_ref_years=[2015])  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        _ = advanced_controls.AdvancedControls(ref_adoption_use_pds_years=[2014],  # by Denton Gentry
                                               pds_adoption_use_ref_years=[2014])  # by Denton Gentry


def test_has_var_costs():
    ac = advanced_controls.AdvancedControls(soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,

                                            conv_var_oper_cost_per_funit=0.0,
                                            conv_fuel_cost_per_funit=0.0)
    assert ac.has_var_costs
    ac = advanced_controls.AdvancedControls(soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,

                                            conv_var_oper_cost_per_funit=0.0)
    assert not ac.has_var_costs


def test_substitute_vma():
    with mock.patch('model.vma.VMA') as MockVMA:
        MockVMA.return_value.avg_high_low.return_value = 'expected return'
        seq_vma = vma.VMA()
        ac = advanced_controls.AdvancedControls(vmas={'Sequestration Rates': seq_vma},
                                                seq_rate_global='mean')
        assert ac.seq_rate_global == 'expected return'


def test_substitute_vma_passthru_value():
    ac = advanced_controls.AdvancedControls(seq_rate_global=4.3)
    assert ac.seq_rate_global == 4.3
    ac = advanced_controls.AdvancedControls(seq_rate_global={'value': 4.3})
    assert ac.seq_rate_global == 4.3


def test_substitute_vma_raises():
    ac = advanced_controls.AdvancedControls(vmas={}, seq_rate_global=1)
    assert ac.seq_rate_global == 1
    with pytest.raises(KeyError):
        advanced_controls.AdvancedControls(vmas={}, seq_rate_global='mean')


def test_substitute_vma_handles_raw_value_discrepancy():
    with mock.patch('model.vma.VMA') as MockVMA:
        MockVMA.return_value.avg_high_low.return_value = 1.2
        seq_vma = vma.VMA()
        ac = advanced_controls.AdvancedControls(vmas={'Sequestration Rates': seq_vma},
                                                seq_rate_global={'value': 1.1, 'statistic': 'mean'})
        assert ac.seq_rate_global == 1.1


def test_yield_coeff():
    ac = advanced_controls.AdvancedControls(yield_from_conv_practice=2, yield_gain_from_conv_to_soln=4,
                                            disturbance_rate=0.25)
    assert ac.yield_coeff == 6
