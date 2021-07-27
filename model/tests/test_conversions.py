import pytest
from math import isclose

from model import conversions


@pytest.mark.parametrize('in_mha,expected_in_ha',
                         [(32, 32_000_000),
                          (1, 1_000_000),
                          (0, 0),
                          (0.5, 5_00_000)])
def test_mha_to_ha(in_mha, expected_in_ha):
    converted_result = conversions.mha_to_ha(in_mha)
    assert converted_result == expected_in_ha


@pytest.mark.parametrize('in_tw,expected_in_kw',
                         [(32, 32_000_000_000),
                          (1, 1_000_000_000),
                          (0, 0),
                          (-3, -3_000_000_000)])
def test_terawatt_to_kilowatt(in_tw, expected_in_kw):
    converted_result = conversions.terawatt_to_kilowatt(in_tw)
    assert converted_result == expected_in_kw


def test_wrong_energy_unit():
    with pytest.raises(ValueError):
        conversions.EnergyConversion('made_up_unit', 'gcal')


@pytest.mark.parametrize('convert_from,convert_to,expected_result,quantity',
                         [('mbtu', 'twh', 2.93E-07, 1),
                          ('kwh', 'gcal', 0.000860, 1),
                          ('gwh', 'gwh', 10, 10)])
def test_energy_conversion(convert_from, convert_to, expected_result, quantity):
    converted_result = conversions.EnergyConversion(convert_from, convert_to)(quantity)
    assert isclose(converted_result, expected_result, rel_tol=1e-3)


@pytest.mark.parametrize('convert_from,convert_to,expected_result,quantity',
                         [('bbl', 'l', 158.98730, 1),
                          ('gal_uk', 'cubic_ft', 0.16054, 1),
                          ('l', 'l', 10, 10)])
def test_volume_conversion(convert_from, convert_to, expected_result, quantity):
    converted_result = conversions.VolumeConversion(convert_from, convert_to)(quantity)
    assert isclose(converted_result, expected_result, abs_tol=1e-4)


@pytest.mark.parametrize('convert_from,convert_to,expected_result,quantity',
                         [('g', 't', 1e-6, 1),
                          ('t', 'g', 1e6, 1),
                          ('t', 't', 10, 10)])
def test_mass_conversion(convert_from, convert_to, expected_result, quantity):
    converted_result = conversions.MassConversion(convert_from, convert_to)(quantity)
    assert isclose(converted_result, expected_result, abs_tol=1e-4)