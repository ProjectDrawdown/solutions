import pytest

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
