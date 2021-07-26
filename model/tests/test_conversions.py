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
