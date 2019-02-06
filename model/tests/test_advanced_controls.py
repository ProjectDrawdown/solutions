"""Test advanced_controls.py."""

import pytest
from model import advanced_controls
from model import emissionsfactors as ef


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
  soln_energy_efficiency_factor = ""
  conv_annual_energy_used = 2.117
  soln_annual_energy_used = None

  ac = advanced_controls.AdvancedControls(
      soln_energy_efficiency_factor=soln_energy_efficiency_factor,
      conv_annual_energy_used=conv_annual_energy_used,
      soln_annual_energy_used=soln_annual_energy_used)
  assert ac.soln_energy_efficiency_factor == 0
  assert ac.conv_annual_energy_used == pytest.approx(conv_annual_energy_used)
  assert ac.soln_annual_energy_used == 0

def test_lifetimes():
  soln_lifetime_capacity = 50000
  soln_avg_annual_use = 1000
  conv_lifetime_capacity = 10000
  conv_avg_annual_use = 3
  ac = advanced_controls.AdvancedControls(
      soln_lifetime_capacity=soln_lifetime_capacity,
      soln_avg_annual_use=soln_avg_annual_use,
      conv_lifetime_capacity=conv_lifetime_capacity,
      conv_avg_annual_use=conv_avg_annual_use)
  assert ac.soln_lifetime_replacement == 50
  assert ac.conv_lifetime_replacement == pytest.approx(3333.333333333333)

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
  assert ac.soln_pds_adoption_basis == "S-Curve"
  assert ac.soln_pds_adoption_prognostication_growth == "Low"
  assert ac.soln_pds_adoption_prognostication_source == "test2"
  with pytest.raises(ValueError):
    _ = advanced_controls.AdvancedControls(soln_pds_adoption_basis="???")
  with pytest.raises(ValueError):
    _ = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_growth="???")

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
