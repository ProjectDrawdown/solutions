"""Tests for unitadoption.py."""

import pandas as pd
import pytest
import io
from model import unitadoption


def test_na_funits():
    '''Test net adoption functional units calculation.'''

    ref_sol_funits = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2014, 112.63, 75.00, 0.33
2015, 117.07, 75.63, 0.34
2016, 121.51, 76.25, 0.34'''), index_col=0)

    pds_sol_funits = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2014, 112.63, 75.00, 0.33
2015, 176.24, 0, 0
2016, 272.03, 0, 0'''), index_col=0)

    na_funits = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2014, 0, 0, 0
2015, 59.17, -75.63, -0.34
2016, 150.52, -76.25, -0.34'''), index_col=0)

    ua = unitadoption.UnitAdoption()
    result = ua.na_funits(ref_sol_funits, pds_sol_funits)
    # Confirm that values are equal across the entire array.
    pd.testing.assert_frame_equal(result, na_funits, check_exact=False,
                                  check_less_precise=2)

def test_life_rep_years():
    """Test Lifetime Replacement for solution/conventional in years calculation."""

    ua = unitadoption.UnitAdoption()
    result = ua.life_rep_years(48343.80, 1841.67)
    assert result == pytest.approx(26.0)

def test_sol_cum_iunits():
    '''Test cumulative solution implementation units installed'''

    columns = ["World", "OECD90", "Eastern Europe"]
    ref_sol_funits = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2014, 112.63, 75.00, 0.33
2015, 117.07, 75.63, 0.34
2016, 121.51, 76.25, 0.34'''), index_col=0)

    aau_sol_funits = 1841.67
    ref_sol_cum_iunits = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2014, 0.0611, 0.0407, 0.000179
2015, 0.0635, 0.0410, 0.000184
2016, 0.0659, 0.0414, 0.000184'''), index_col=0)

    ua = unitadoption.UnitAdoption()
    result = ua.sol_cum_iunits(
        ref_sol_funits, aau_sol_funits)
    # Confirm that values are equal across the entire array.
    pd.testing.assert_frame_equal(result, ref_sol_cum_iunits, check_exact=False,
                                  check_less_precise=2)

def test_sol_ann_iunits():
    '''Test new implementation units required (including replacement units)'''

    # Test only the cumulative function - the lifetime should have no effect here.
    # For OEC90, this also tests that negative change in units is not counted.
    ref_sol_cum_iunits = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2014, 0.06116, 0.04073, 0.00018
2015, 0.06357, 0.04106, 0.00018
2016, 0.06598, 0.03, 0.00015'''), index_col=0)

    life_rep_sol_years = 26.00
    ref_sol_ann_funits_diff = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2015, 0.00241, 0.00033, 0.0
2016, 0.00241, 0.0, 0.0'''), index_col=0)

    ua = unitadoption.UnitAdoption()
    result = ua.sol_ann_iunits(
        ref_sol_cum_iunits, life_rep_sol_years)
    # Confirm that values are equal across the entire array.
    pd.testing.assert_frame_equal(result, ref_sol_ann_funits_diff, check_exact=False,
                                  check_less_precise=5)

    # Test a 2 year lifetime replacement - 2016 should now include
    # units from 2015, as those now need to be replaced.
    life_rep_sol_years = 1.00
    ref_sol_ann_funits_lifetime = pd.read_csv(io.StringIO('''
Year, World, OECD90, Eastern Europe
2015, 0.00241, 0.00033, 0.0
2016, 0.00482, 0.00033, 0.0'''), index_col=0)
    result = ua.sol_ann_iunits(
        ref_sol_cum_iunits, life_rep_sol_years)
    # Confirm that values are equal across the entire array.
    pd.testing.assert_frame_equal(result, ref_sol_ann_funits_lifetime, check_exact=False,
                                  check_less_precise=5)
