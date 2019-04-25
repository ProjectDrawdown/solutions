"""Tests for emissionsfactors.py."""  # by Denton Gentry
# by Denton Gentry
from model import advanced_controls  # by Denton Gentry
from model import emissionsfactors as ef  # by Denton Gentry
import pandas as pd  # by Denton Gentry
import pytest  # by Denton Gentry


# by Denton Gentry

def test_CO2Equiv():  # by Denton Gentry
    c = ef.CO2Equiv(ef.CO2EQ_SOURCE.AR5_WITH_FEEDBACK)  # by Denton Gentry
    assert c.CH4multiplier == 34  # by Denton Gentry
    assert c.N2Omultiplier == 298  # by Denton Gentry
    c = ef.CO2Equiv(ef.CO2EQ_SOURCE.AR4)  # by Denton Gentry
    assert c.CH4multiplier == 25  # by Denton Gentry
    assert c.N2Omultiplier == 298  # by Denton Gentry
    c = ef.CO2Equiv(ef.CO2EQ_SOURCE.SAR)  # by Denton Gentry
    assert c.CH4multiplier == 21  # by Denton Gentry
    assert c.N2Omultiplier == 310  # by Denton Gentry
    # by Denton Gentry


def test_string_to_conversion_source():  # by Denton Gentry
    assert ef.string_to_conversion_source("AR5 with feedback") == ef.CO2EQ_SOURCE.AR5_WITH_FEEDBACK  # by Denton Gentry
    assert ef.string_to_conversion_source("AR4") == ef.CO2EQ_SOURCE.AR4  # by Denton Gentry
    assert ef.string_to_conversion_source("Ar4") == ef.CO2EQ_SOURCE.AR4  # by Denton Gentry
    assert ef.string_to_conversion_source("SAR") == ef.CO2EQ_SOURCE.SAR  # by Denton Gentry
    assert ef.string_to_conversion_source("sar") == ef.CO2EQ_SOURCE.SAR  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        ef.string_to_conversion_source("invalid")  # by Denton Gentry
    # by Denton Gentry


def test_string_to_emissions_grid_source():  # by Denton Gentry
    assert ef.string_to_emissions_grid_source("meta-analysis") == ef.GRID_SOURCE.META  # by Denton Gentry
    assert ef.string_to_emissions_grid_source("MeTa_AnAlYsIs") == ef.GRID_SOURCE.META  # by Denton Gentry
    assert ef.string_to_emissions_grid_source("META ANALYSIS") == ef.GRID_SOURCE.META  # by Denton Gentry
    assert ef.string_to_emissions_grid_source("IPCC_ONLY") == ef.GRID_SOURCE.IPCC  # by Denton Gentry
    assert ef.string_to_emissions_grid_source("ipcc only") == ef.GRID_SOURCE.IPCC  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        ef.string_to_conversion_source("invalid")  # by Denton Gentry
    # by Denton Gentry


def test_string_to_emissions_grid_range():  # by Denton Gentry
    assert ef.string_to_emissions_grid_range("MEAN") == ef.GRID_RANGE.MEAN  # by Denton Gentry
    assert ef.string_to_emissions_grid_range("MEan") == ef.GRID_RANGE.MEAN  # by Denton Gentry
    assert ef.string_to_emissions_grid_range("Median") == ef.GRID_RANGE.MEAN  # by Denton Gentry
    assert ef.string_to_emissions_grid_range("high") == ef.GRID_RANGE.HIGH  # by Denton Gentry
    assert ef.string_to_emissions_grid_range("LOW") == ef.GRID_RANGE.LOW  # by Denton Gentry
    with pytest.raises(ValueError):  # by Denton Gentry
        ef.string_to_conversion_source("invalid")  # by Denton Gentry
    # by Denton Gentry


def test_ElectricityGenOnGrid_conv_ref_grid_CO2eq_per_KWh():  # by Denton Gentry
    ac = advanced_controls.AdvancedControls(emissions_grid_source="ipcc_only",
                                            emissions_grid_range="mean")  # by Denton Gentry
    eg = ef.ElectricityGenOnGrid(ac=ac)  # by Denton Gentry
    table = eg.conv_ref_grid_CO2eq_per_KWh()  # by Denton Gentry
    assert table.loc[2025, "OECD90"] == pytest.approx(0.454068989)  # by Denton Gentry
    assert table.loc[2020, 'World'] == pytest.approx(0.483415642)  # by Denton Gentry
    ac.emissions_grid_range = ef.GRID_RANGE.LOW  # by Denton Gentry
    eg = ef.ElectricityGenOnGrid(ac=ac)  # by Denton Gentry
    table = eg.conv_ref_grid_CO2eq_per_KWh()  # by Denton Gentry
    assert table.loc[2020, 'World'] == pytest.approx(0.416520905)  # by Denton Gentry
    ac.emissions_grid_range = ef.GRID_RANGE.HIGH  # by Denton Gentry
    eg = ef.ElectricityGenOnGrid(ac=ac)  # by Denton Gentry
    table = eg.conv_ref_grid_CO2eq_per_KWh()  # by Denton Gentry
    assert table.loc[2020, 'World'] == pytest.approx(0.952177536)  # by Denton Gentry
    ac.emissions_grid_source = ef.GRID_SOURCE.META  # by Denton Gentry
    ac.emissions_grid_range = ef.GRID_RANGE.MEAN  # by Denton Gentry
    eg = ef.ElectricityGenOnGrid(ac=ac)  # by Denton Gentry
    table = eg.conv_ref_grid_CO2eq_per_KWh()  # by Denton Gentry
    assert table.loc[2020, 'World'] == pytest.approx(0.581083120)  # by Denton Gentry
    ac.emissions_grid_range = ef.GRID_RANGE.LOW  # by Denton Gentry
    eg = ef.ElectricityGenOnGrid(ac=ac)  # by Denton Gentry
    table = eg.conv_ref_grid_CO2eq_per_KWh()  # by Denton Gentry
    assert table.loc[2020, 'World'] == pytest.approx(0.446005409)  # by Denton Gentry
    ac.emissions_grid_range = ef.GRID_RANGE.HIGH  # by Denton Gentry
    eg = ef.ElectricityGenOnGrid(ac=ac)  # by Denton Gentry
    table = eg.conv_ref_grid_CO2eq_per_KWh()  # by Denton Gentry
    assert table.loc[2020, 'World'] == pytest.approx(0.726403172)  # by Denton Gentry
    # by Denton Gentry


def test_conv_ref_grid_CO2_per_KWh():  # by Denton Gentry
    eg = ef.ElectricityGenOnGrid(ac=None)  # by Denton Gentry
    table = eg.conv_ref_grid_CO2_per_KWh()  # by Denton Gentry
    assert table.loc[2025, "World"] == pytest.approx(0.484512031)  # by Denton Gentry
    assert table.loc[2032, "OECD90"] == pytest.approx(0.392126590)  # by Denton Gentry
    assert table.loc[2046, "Eastern Europe"] == pytest.approx(0.659977317)  # by Denton Gentry
    assert table.loc[2060, "Asia (Sans Japan)"] == pytest.approx(0.385555834)  # by Denton Gentry
    assert table.loc[2016, "Middle East and Africa"] == pytest.approx(0.185499981)  # by Denton Gentry
    assert table.loc[2027, "Latin America"] == pytest.approx(0.491537631)  # by Denton Gentry
    assert table.loc[2034, "China"] == pytest.approx(0.474730313)  # by Denton Gentry
    assert table.loc[2041, "India"] == pytest.approx(0.725081980)  # by Denton Gentry
    assert table.loc[2020, "EU"] == pytest.approx(0.297016531)  # by Denton Gentry
    assert table.loc[2039, "USA"] == pytest.approx(0.594563067)  # by Denton Gentry
