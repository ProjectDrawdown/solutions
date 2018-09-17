"""Tests for unitadoption.py."""

import unittest

import pandas as pd
from model import unitadoption


class TestUnitAdoption(unittest.TestCase):
    """Tests for unitadoption.py functionality."""


def test_na_funits():
    '''Test net adoption functional units calculation.'''

    columns = ["World", "OECD90", "Eastern Europe"]
    ref_sol_funits = pd.DataFrame.from_dict(
        dict([(2014, [112.63, 75.00,  0.33]),
              (2015, [117.07, 75.63,  0.34]),
              (2016, [121.51, 76.25,  0.34])]),
        orient='index', columns=columns)
    pds_sol_funits = pd.DataFrame.from_dict(
        dict([(2014, [112.63, 75.00, 0.33]),
              (2015, [176.24, 0, 0]),
              (2016, [272.03, 0, 0])]),
        orient='index', columns=columns)
    na_funits = pd.DataFrame.from_dict(
        dict([(2014, [0, 0, 0]),
              (2015, [59.17, -75.63, -0.34]),
              (2016, [150.52, -76.25, -0.34])]),
        orient='index', columns=columns)
    ua = unitadoption.UnitAdoption()
    result = ua.na_funits(ref_sol_funits, pds_sol_funits)
    # Confirm that values are equal across the entire array.
    pd.testing.assert_frame_equal(result, na_funits, check_exact=False,
                                  check_less_precise=2)


def test_life_rep_years(self):
    """Test Lifetime Replacement for solution/conventional in years calculation."""

    ua = unitadoption.UnitAdoption()
    result = ua.life_rep_years(48343.80, 1841.67)
    self.assertAlmostEqual(result, 26.00)


def test_sol_cum_iunits():
    '''Test cumulative solution implementation units installed'''

    columns = ["World", "OECD90", "Eastern Europe"]
    ref_sol_funits = pd.DataFrame.from_dict(
        dict([(2014, [112.63, 75.00,  0.33]),
              (2015, [117.07, 75.63,  0.34]),
              (2016, [121.51, 76.25,  0.34])]),
        orient='index', columns=columns)
    aau_sol_funits = 1841.67
    ref_sol_cum_iunits = pd.DataFrame.from_dict(
        dict([(2014, [0.06, 0.04, 0.00]),
              (2015, [0.06, 0.04, 0.00]),
              (2016, [0.07, 0.04, 0.00])]),
        orient='index', columns=columns)
    ua = unitadoption.UnitAdoption()
    result = ua.sol_cum_iunits(
        ref_sol_funits, aau_sol_funits).round(FLOAT_ROUND)
    # Confirm that values are equal across the entire array.
    pd.testing.assert_frame_equal(result, ref_sol_cum_iunits, check_exact=False,
                                  check_less_precise=2)


def test_sol_ann_iunits():
    '''Test new implementation units required (including replacement units)'''

    columns = ["World", "OECD90", "Eastern Europe"]
    ref_sol_cum_iunits = pd.DataFrame.from_dict(
        dict([(2014, [0.06116, 0.04073, 0.00018]),
              (2015, [0.06357, 0.04106, 0.00018]),
              (2016, [0.06598, 0.04140, 0.00015])]),
        orient='index', columns=columns)
    life_rep_sol_years = 26.00
    ref_sol_ann_funits = pd.DataFrame.from_dict(
        dict([(2015, [0.00241, 0.00033, 0]),
              (2016, [0.00241, 0.00034, 0])]),
        orient='index', columns=columns)
    ua = unitadoption.UnitAdoption()
    result = ua.sol_ann_iunits(
        ref_sol_cum_iunits, life_rep_sol_years)
    print(ref_sol_ann_funits.info())
    print(result.info())
    # Confirm that values are equal across the entire array.
    pd.testing.assert_frame_equal(result, ref_sol_ann_funits, check_exact=False,
                                  check_less_precise=2)
