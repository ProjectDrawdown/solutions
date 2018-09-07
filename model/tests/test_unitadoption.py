import pytest
import pandas as pd
from model import unitadoption

FLOAT_ROUND = 2


def test_na_funits():
    """Test net adoption functional units calculation."""

    columns = ["World", "OECD90", "Eastern Europe"]
    ref = pd.DataFrame.from_dict(dict([(2014, [112.63, 75.00,  0.33]),
                                       (2015, [117.07, 75.63,  0.34]),
                                       (2016, [121.51, 76.25,  0.34])]), orient='index', columns=columns)
    pds = pd.DataFrame.from_dict(dict([(2014, [112.63, 75.00, 0.33]),
                                       (2015, [176.24, 0, 0]),
                                       (2016, [272.03, 0, 0])]), orient='index', columns=columns)
    na_funits = pd.DataFrame.from_dict(dict([(2014, [0, 0, 0]),
                                             (2015, [59.17, -75.63, -0.34]),
                                             (2016, [150.52, -76.25, -0.34])]), orient='index', columns=columns)
    ua = unitadoption.UnitAdoption()
    result = ua.na_funits(ref, pds).round(FLOAT_ROUND)
    # Confirm that values are equal across the entire array.
    assert (result == na_funits).all(axis=None)


def test_life_rep_years():
    """Test Lifetime Replacement for solution/conventional in years calculation."""

    ua = unitadoption.UnitAdoption()
    result = ua.life_rep_years(48343.80, 1841.67)
    assert result == 26.00
