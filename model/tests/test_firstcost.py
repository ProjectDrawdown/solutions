"""Tests for firstcost.py."""

import numpy as np
import pandas as pd
import pathlib
from unittest import mock
from model import advanced_controls
from model import firstcost
from model.dd import REGIONS

datadir = pathlib.Path(__file__).parents[0].joinpath('data')
pd.set_option('display.expand_frame_repr', False)


def test_soln_pds_install_cost_per_iunit():
    """Test PDS install cost per unit
       Values taken from SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    soln_pds_tot_iunits_reqd = pd.DataFrame(
            soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2,
            conv_learning_increase_mult=2, soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=None, conv_ref_tot_iunits=None, soln_pds_new_iunits_reqd=None,
            soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(
            soln_pds_install_cost_per_iunit_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "soln_pds_install_cost_per_iunit"
    result = fc.soln_pds_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_pds_install_cost_per_iunit_with_nan():
    """Test PDS install cost per unit

       Values taken from
       Drawdown-Alternative (High Vol. Fly Ash) Cement_RRS_v1.1_16Nov2018_PUBLIC.xlsm
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=32130000.0,
            ref_2014_cost=32130000.0,
            conv_2014_cost=45900000.0,
            soln_first_cost_efficiency_rate=0.0,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.0)
    soln_pds_tot_iunits_reqd = pd.DataFrame(
            soln_pds_tot_iunits_reqd_altcement_list[1:],
            columns=soln_pds_tot_iunits_reqd_altcement_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2,
            conv_learning_increase_mult=2, soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=None, conv_ref_tot_iunits=None, soln_pds_new_iunits_reqd=None,
            soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None, fc_convert_iunit_factor=1.0)
    expected = pd.Series(
            soln_pds_install_cost_per_iunit_altcement_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_altcement_nparray[:, 0],
            dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "soln_pds_install_cost_per_iunit"
    result = fc.soln_pds_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_pds_install_cost_per_iunit_with_zero():
    """Test PDS install cost per unit

       Values taken from
       Drawdown-Alternative (High Vol. Fly Ash) Cement_RRS_v1.1_16Nov2018_PUBLIC.xlsm
       then filled with zero. This approximates the behavior of the Nuclear solution.
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=32130000.0,
            ref_2014_cost=32130000.0,
            conv_2014_cost=45900000.0,
            soln_first_cost_efficiency_rate=0.0,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.0)
    soln_pds_tot_iunits_reqd = pd.DataFrame(
            soln_pds_tot_iunits_reqd_altcement_list[1:],
            columns=soln_pds_tot_iunits_reqd_altcement_list[0]).set_index('Year').fillna(0.0)
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2,
            conv_learning_increase_mult=2, soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=None, conv_ref_tot_iunits=None, soln_pds_new_iunits_reqd=None,
            soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None, fc_convert_iunit_factor=1.0)
    expected = pd.Series(
            soln_pds_install_cost_per_iunit_altcement_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_altcement_nparray[:, 0],
            dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "soln_pds_install_cost_per_iunit"
    result = fc.soln_pds_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_pds_install_cost_per_iunit_start_2018():
    """Test PDS install cost per unit
       Values taken from SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    soln_pds_tot_iunits_reqd = pd.DataFrame(
            soln_pds_tot_iunits_reqd_list[4:],  # only 2018 and beyond
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2,
            conv_learning_increase_mult=2, soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=None, conv_ref_tot_iunits=None, soln_pds_new_iunits_reqd=None,
            soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    result = fc.soln_pds_install_cost_per_iunit()
    assert 2015 not in result.index
    assert 2018 in result.index


def test_conv_ref_install_cost_per_iunit():
    """Test conventional install cost per unit

       Values taken from SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(conv_ref_install_cost_per_iunit_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "conv_ref_install_cost_per_iunit"
    result = fc.conv_ref_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_conv_ref_install_cost_per_iunit_no_conversion_factor():
    """Test conventional install cost per unit

       Values taken from Drawdown-Improved Cook Stoves (ICS)_RRS_v1.1_28Nov2018_PUBLIC.xlsm
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=39.0, ref_2014_cost=39.0, conv_2014_cost=2.0487610390567785,
            soln_first_cost_efficiency_rate=0.0, soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.0)
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_cookstoves_list[1:],
            columns=conv_ref_tot_iunits_cookstoves_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2,
            conv_learning_increase_mult=2, soln_pds_tot_iunits_reqd=None,
            soln_ref_tot_iunits_reqd=None, conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1.0)
    expected = pd.Series(conv_ref_install_cost_per_iunit_cookstoves_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_cookstoves_nparray[:, 0],
            dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "conv_ref_install_cost_per_iunit"
    result = fc.conv_ref_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_pds_install_cost_per_iunit_not_less_conv():
    """Test PDS install cost per unit
       Values taken from SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=False,  # result == conv_ref_install_cost_per_iunit
            conv_first_cost_efficiency_rate=0.02)
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2,
            conv_learning_increase_mult=2, soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=None, conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    # Not a typo, soln_first_cost_below_conv=False so expected=conv_pds_install_cost_per_iunit.
    expected = pd.Series(conv_ref_install_cost_per_iunit_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "soln_pds_install_cost_per_iunit"
    result = fc.soln_pds_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_ref_install_cost_per_iunit():
    """Test PDS install cost per unit

       Values taken from SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(soln_ref_install_cost_per_iunit_nparray[:, 1],
            index=soln_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "soln_ref_install_cost_per_iunit"
    result = fc.soln_ref_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_install_cost_per_iunit_param_b_is_zero():
    """Test install cost per unit with contrived values to make parameter_b be zero."""
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1000.0, ref_2014_cost=2000.0, conv_2014_cost=3000.0,
            soln_first_cost_below_conv=True,
            soln_first_cost_efficiency_rate=0.0,
            conv_first_cost_efficiency_rate=0.0)
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2,
            conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(ac.ref_2014_cost * 1000000000.0,
            index=soln_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "soln_ref_install_cost_per_iunit"
    result = fc.soln_ref_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)
    expected = pd.Series(ac.conv_2014_cost * 1000000000.0,
            index=conv_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "conv_ref_install_cost_per_iunit"
    result = fc.conv_ref_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_ref_install_cost_per_iunit_not_less_conv():
    """Test PDS install cost per unit

       Values taken from SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18
    """
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=False,  # result = conv
            conv_first_cost_efficiency_rate=0.02)
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    # Not a typo, soln_first_cost_below_conv=False so expected=conv_pds_install_cost_per_iunit.
    expected = pd.Series(conv_ref_install_cost_per_iunit_nparray[:, 1],
                         index=conv_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "soln_ref_install_cost_per_iunit"
    result = fc.soln_ref_install_cost_per_iunit()
    pd.testing.assert_series_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_pds_annual_world_first_cost():
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_pds_new_iunits_reqd = pd.DataFrame(soln_pds_new_iunits_reqd_list[1:],
            columns=soln_pds_new_iunits_reqd_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac,
            pds_learning_increase_mult=2, ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd, soln_ref_tot_iunits_reqd=None,
            conv_ref_tot_iunits=None,
            soln_pds_new_iunits_reqd=soln_pds_new_iunits_reqd, soln_ref_new_iunits_reqd=None,
            conv_ref_new_iunits=None, fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(soln_pds_annual_world_first_cost_nparray[:, 1],
            index=soln_pds_annual_world_first_cost_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    expected.name = "soln_pds_annual_world_first_cost"
    result = fc.soln_pds_annual_world_first_cost()
    pd.testing.assert_series_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)


def test_soln_pds_cumulative_install():
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_pds_new_iunits_reqd = pd.DataFrame(soln_pds_new_iunits_reqd_list[1:],
            columns=soln_pds_new_iunits_reqd_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=None, conv_ref_tot_iunits=None,
            soln_pds_new_iunits_reqd=soln_pds_new_iunits_reqd,
            soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0)
    result = fc.soln_pds_cumulative_install()
    expected = pd.Series(pds_cumulative_install_nparray[:, 1],
            index=pds_cumulative_install_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    expected.name = "soln_pds_cumulative_install"
    pd.testing.assert_series_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)


def test_soln_ref_annual_world_first_cost():
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    soln_ref_new_iunits_reqd = pd.DataFrame(soln_ref_new_iunits_reqd_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=None, soln_pds_new_iunits_reqd=None,
            soln_ref_new_iunits_reqd=soln_ref_new_iunits_reqd,
            conv_ref_new_iunits=None, fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(soln_ref_annual_world_first_cost_nparray[:, 1],
            index=soln_ref_annual_world_first_cost_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    expected.name = "soln_ref_annual_world_first_cost"
    result = fc.soln_ref_annual_world_first_cost()
    pd.testing.assert_series_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)


def test_conv_ref_annual_world_first_cost():
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    conv_ref_new_iunits = pd.DataFrame(conv_ref_new_iunits_list[1:],
            columns=conv_ref_new_iunits_list[0]).set_index('Year').drop(['Lifetime'])
    fc = firstcost.FirstCost(ac=ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None,
            conv_ref_new_iunits=conv_ref_new_iunits,
            fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(conv_ref_annual_world_first_cost_nparray[:, 1],
            index=conv_ref_annual_world_first_cost_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "conv_ref_annual_world_first_cost"
    result = fc.conv_ref_annual_world_first_cost()
    pd.testing.assert_series_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)


def test_conv_ref_annual_world_first_cost_tot_iunits():
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_for_fc_list[1:],
            columns=conv_ref_tot_iunits_for_fc_list[0]).set_index('Year')
    fc = firstcost.FirstCost(ac=ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
            fc_convert_iunit_factor=1000000000.0, conv_ref_first_cost_uses_tot_units=True)
    expected = pd.Series(conv_ref_annual_world_first_cost_tot_iunits_nparray[:, 1],
            index=conv_ref_annual_world_first_cost_tot_iunits_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = "Year"
    expected.name = "conv_ref_annual_world_first_cost"
    result = fc.conv_ref_annual_world_first_cost()
    pd.testing.assert_series_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)


def test_ref_cumulative_install():
    ac = advanced_controls.AdvancedControls(
            pds_2014_cost=1444.93954421485,
            ref_2014_cost=1444.93954421485,
            conv_2014_cost=2010.03170851964,
            soln_first_cost_efficiency_rate=0.196222222222222,
            soln_first_cost_below_conv=True,
            conv_first_cost_efficiency_rate=0.02)
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    conv_ref_tot_iunits = pd.DataFrame(conv_ref_tot_iunits_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    soln_ref_new_iunits_reqd = pd.DataFrame(soln_ref_new_iunits_reqd_list[1:],
            columns=conv_ref_tot_iunits_list[0]).set_index('Year')
    conv_ref_new_iunits = pd.DataFrame(conv_ref_new_iunits_list[1:],
            columns=conv_ref_new_iunits_list[0]).set_index('Year').drop(['Lifetime'])
    fc = firstcost.FirstCost(ac=ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=soln_ref_new_iunits_reqd,
            conv_ref_new_iunits=conv_ref_new_iunits,
            fc_convert_iunit_factor=1000000000.0)
    expected = pd.Series(ref_cumulative_install_nparray[:, 1],
            index=ref_cumulative_install_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    expected.name = "ref_cumulative_install"
    result = fc.ref_cumulative_install()
    pd.testing.assert_series_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)


# SolarPVUtil 'Unit Adoption Calculations'!AX135:BH182
soln_pds_tot_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 0.06115814489, 0.04072624506, 0.00018047945, 0.01144207203, 0.00085524497,
     0.00795507895, 0.00812970502, 0.00149228865, 0.03001194422, 0.00712649942],
    [2015, 0.09569632876, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 0.14770917868, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 0.20813155943, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 0.27658585364, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 0.35269444391, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 0.35511275489, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 0.52636404313, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 0.62316981729, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 0.72611941799, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 0.83483522783, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 0.86627964703, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 1.06805500539, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 1.19180373834, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 1.31980821089, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 1.45169080567, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 1.65078562298, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 1.72557989233, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 1.86683114944, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 2.01045005923, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 2.15605900432, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 2.30328036731, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 2.45173653082, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 2.60104987747, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 2.75084278988, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 2.90073765065, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 3.07612351532, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 3.19932274775, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 3.34725774931, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 3.49378422970, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 3.63852457153, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 3.78110115742, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 3.92113636998, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 4.05825259183, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 4.19207220558, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 4.32221759385, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 4.43499993794, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 4.56997522439, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 4.68683223190, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 4.79850454439, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 4.90461454447, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 5.00478461475, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 5.09863713786, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 5.18579449640, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 5.26587907300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 5.33851325027, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 5.40331941081, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil 'Unit Adoption Calculations'!AX197:BH244
soln_ref_tot_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.06115814489, 0.04072624506, 0.00018047945, 0.01144207203, 0.00085524497, 0.00795507895, 0.00812970502,
     0.00149228865, 0.03001194422, 0.00712649942],
    [2015, 0.06356811321, 0.04106406734, 0.00018335632, 0.01203213720, 0.00092855523, 0.00837129114, 0.00837997582,
     0.00166702867, 0.03027672478, 0.00717613125],
    [2016, 0.06597808152, 0.04140188962, 0.00018623318, 0.01262220236, 0.00100186550, 0.00878750333, 0.00863024663,
     0.00184176869, 0.03054150533, 0.00722576309],
    [2017, 0.06838804984, 0.04173971190, 0.00018911004, 0.01321226753, 0.00107517577, 0.00920371553, 0.00888051744,
     0.00201650870, 0.03080628588, 0.00727539492],
    [2018, 0.07079801816, 0.04207753419, 0.00019198691, 0.01380233270, 0.00114848604, 0.00961992772, 0.00913078824,
     0.00219124872, 0.03107106643, 0.00732502676],
    [2019, 0.07320798648, 0.04241535647, 0.00019486377, 0.01439239787, 0.00122179630, 0.01003613991, 0.00938105905,
     0.00236598874, 0.03133584698, 0.00737465859],
    [2020, 0.07561795479, 0.04275317875, 0.00019774064, 0.01498246304, 0.00129510657, 0.01045235210, 0.00963132986,
     0.00254072876, 0.03160062754, 0.00742429043],
    [2021, 0.07802792311, 0.04309100103, 0.00020061750, 0.01557252821, 0.00136841684, 0.01086856429, 0.00988160066,
     0.00271546877, 0.03186540809, 0.00747392226],
    [2022, 0.08043789143, 0.04342882332, 0.00020349436, 0.01616259338, 0.00144172710, 0.01128477648, 0.01013187147,
     0.00289020879, 0.03213018864, 0.00752355410],
    [2023, 0.08284785974, 0.04376664560, 0.00020637123, 0.01675265855, 0.00151503737, 0.01170098867, 0.01038214228,
     0.00306494881, 0.03239496919, 0.00757318593],
    [2024, 0.08525782806, 0.04410446788, 0.00020924809, 0.01734272372, 0.00158834764, 0.01211720086, 0.01063241308,
     0.00323968882, 0.03265974974, 0.00762281777],
    [2025, 0.08766779638, 0.04444229016, 0.00021212496, 0.01793278889, 0.00166165791, 0.01253341305, 0.01088268389,
     0.00341442884, 0.03292453030, 0.00767244960],
    [2026, 0.09007776469, 0.04478011245, 0.00021500182, 0.01852285405, 0.00173496817, 0.01294962525, 0.01113295470,
     0.00358916886, 0.03318931085, 0.00772208144],
    [2027, 0.09248773301, 0.04511793473, 0.00021787869, 0.01911291922, 0.00180827844, 0.01336583744, 0.01138322550,
     0.00376390887, 0.03345409140, 0.00777171327],
    [2028, 0.09489770133, 0.04545575701, 0.00022075555, 0.01970298439, 0.00188158871, 0.01378204963, 0.01163349631,
     0.00393864889, 0.03371887195, 0.00782134511],
    [2029, 0.09730766964, 0.04579357929, 0.00022363241, 0.02029304956, 0.00195489897, 0.01419826182, 0.01188376712,
     0.00411338891, 0.03398365250, 0.00787097694],
    [2030, 0.09971763796, 0.04613140157, 0.00022650928, 0.02088311473, 0.00202820924, 0.01461447401, 0.01213403792,
     0.00428812893, 0.03424843305, 0.00792060878],
    [2031, 0.10212760628, 0.04646922386, 0.00022938614, 0.02147317990, 0.00210151951, 0.01503068620, 0.01238430873,
     0.00446286894, 0.03451321361, 0.00797024061],
    [2032, 0.10453757459, 0.04680704614, 0.00023226301, 0.02206324507, 0.00217482978, 0.01544689839, 0.01263457954,
     0.00463760896, 0.03477799416, 0.00801987244],
    [2033, 0.10694754291, 0.04714486842, 0.00023513987, 0.02265331024, 0.00224814004, 0.01586311058, 0.01288485034,
     0.00481234898, 0.03504277471, 0.00806950428],
    [2034, 0.10935751123, 0.04748269070, 0.00023801673, 0.02324337541, 0.00232145031, 0.01627932278, 0.01313512115,
     0.00498708899, 0.03530755526, 0.00811913611],
    [2035, 0.11176747954, 0.04782051299, 0.00024089360, 0.02383344057, 0.00239476058, 0.01669553497, 0.01338539196,
     0.00516182901, 0.03557233581, 0.00816876795],
    [2036, 0.11417744786, 0.04815833527, 0.00024377046, 0.02442350574, 0.00246807084, 0.01711174716, 0.01363566276,
     0.00533656903, 0.03583711637, 0.00821839978],
    [2037, 0.11658741618, 0.04849615755, 0.00024664733, 0.02501357091, 0.00254138111, 0.01752795935, 0.01388593357,
     0.00551130905, 0.03610189692, 0.00826803162],
    [2038, 0.11899738449, 0.04883397983, 0.00024952419, 0.02560363608, 0.00261469138, 0.01794417154, 0.01413620438,
     0.00568604906, 0.03636667747, 0.00831766345],
    [2039, 0.12140735281, 0.04917180212, 0.00025240106, 0.02619370125, 0.00268800165, 0.01836038373, 0.01438647518,
     0.00586078908, 0.03663145802, 0.00836729529],
    [2040, 0.12381732113, 0.04950962440, 0.00025527792, 0.02678376642, 0.00276131191, 0.01877659592, 0.01463674599,
     0.00603552910, 0.03689623857, 0.00841692712],
    [2041, 0.12622728944, 0.04984744668, 0.00025815478, 0.02737383159, 0.00283462218, 0.01919280811, 0.01488701680,
     0.00621026911, 0.03716101913, 0.00846655896],
    [2042, 0.12863725776, 0.05018526896, 0.00026103165, 0.02796389676, 0.00290793245, 0.01960902030, 0.01513728760,
     0.00638500913, 0.03742579968, 0.00851619079],
    [2043, 0.13104722608, 0.05052309124, 0.00026390851, 0.02855396193, 0.00298124271, 0.02002523250, 0.01538755841,
     0.00655974915, 0.03769058023, 0.00856582263],
    [2044, 0.13345719439, 0.05086091353, 0.00026678538, 0.02914402709, 0.00305455298, 0.02044144469, 0.01563782922,
     0.00673448917, 0.03795536078, 0.00861545446],
    [2045, 0.13586716271, 0.05119873581, 0.00026966224, 0.02973409226, 0.00312786325, 0.02085765688, 0.01588810002,
     0.00690922918, 0.03822014133, 0.00866508630],
    [2046, 0.13827713103, 0.05153655809, 0.00027253911, 0.03032415743, 0.00320117352, 0.02127386907, 0.01613837083,
     0.00708396920, 0.03848492189, 0.00871471813],
    [2047, 0.14068709935, 0.05187438037, 0.00027541597, 0.03091422260, 0.00327448378, 0.02169008126, 0.01638864163,
     0.00725870922, 0.03874970244, 0.00876434997],
    [2048, 0.14309706766, 0.05221220266, 0.00027829283, 0.03150428777, 0.00334779405, 0.02210629345, 0.01663891244,
     0.00743344923, 0.03901448299, 0.00881398180],
    [2049, 0.14550703598, 0.05255002494, 0.00028116970, 0.03209435294, 0.00342110432, 0.02252250564, 0.01688918325,
     0.00760818925, 0.03927926354, 0.00886361364],
    [2050, 0.14791700430, 0.05288784722, 0.00028404656, 0.03268441811, 0.00349441458, 0.02293871783, 0.01713945405,
     0.00778292927, 0.03954404409, 0.00891324547],
    [2051, 0.15032697261, 0.05322566950, 0.00028692343, 0.03327448328, 0.00356772485, 0.02335493002, 0.01738972486,
     0.00795766928, 0.03980882465, 0.00896287731],
    [2052, 0.15273694093, 0.05356349178, 0.00028980029, 0.03386454845, 0.00364103512, 0.02377114222, 0.01763999567,
     0.00813240930, 0.04007360520, 0.00901250914],
    [2053, 0.15514690925, 0.05390131407, 0.00029267715, 0.03445461361, 0.00371434539, 0.02418735441, 0.01789026647,
     0.00830714932, 0.04033838575, 0.00906214098],
    [2054, 0.15755687756, 0.05423913635, 0.00029555402, 0.03504467878, 0.00378765565, 0.02460356660, 0.01814053728,
     0.00848188934, 0.04060316630, 0.00911177281],
    [2055, 0.15996684588, 0.05457695863, 0.00029843088, 0.03563474395, 0.00386096592, 0.02501977879, 0.01839080809,
     0.00865662935, 0.04086794685, 0.00916140465],
    [2056, 0.16237681420, 0.05491478091, 0.00030130775, 0.03622480912, 0.00393427619, 0.02543599098, 0.01864107889,
     0.00883136937, 0.04113272741, 0.00921103648],
    [2057, 0.16478678251, 0.05525260320, 0.00030418461, 0.03681487429, 0.00400758645, 0.02585220317, 0.01889134970,
     0.00900610939, 0.04139750796, 0.00926066832],
    [2058, 0.16719675083, 0.05559042548, 0.00030706148, 0.03740493946, 0.00408089672, 0.02626841536, 0.01914162051,
     0.00918084940, 0.04166228851, 0.00931030015],
    [2059, 0.16960671915, 0.05592824776, 0.00030993834, 0.03799500463, 0.00415420699, 0.02668462755, 0.01939189131,
     0.00935558942, 0.04192706906, 0.00935993199],
    [2060, 0.17201668746, 0.05626607004, 0.00031281520, 0.03858506980, 0.00422751726, 0.02710083975, 0.01964216212,
     0.00953032944, 0.04219184961, 0.00940956382]]

# SolarPVUtil 'Unit Adoption Calculations'!Q251:AA298
conv_ref_tot_iunits_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 4.53535289538, 1.93172544646, 0.40864109200, 1.62670021570, 0.35349784059, 0.33696728156, 1.06083899586,
     0.26726785668, 0.67200041390, 0.85164625801],
    [2015, 4.87963781659, 1.94274331751, 0.41354556337, 1.71747727285, 0.36623971961, 0.34647499389, 1.12436082360,
     0.28395661580, 0.67661778152, 0.85406909967],
    [2016, 5.05302431141, 1.95081104871, 0.41846626996, 1.80887913162, 0.38117035177, 0.35703644903, 1.18305384727,
     0.30426884337, 0.68059242533, 0.85404423296],
    [2017, 5.22637504321, 1.95963749723, 0.42358977955, 1.89897464489, 0.39677819112, 0.36812109492, 1.23953812870,
     0.32534664195, 0.68456148855, 0.85458743518],
    [2018, 5.39969647678, 1.96919699819, 0.42890642054, 1.98784134090, 0.41308655225, 0.37972041074, 1.29387052033,
     0.34718138172, 0.68853612852, 0.85567945042],
    [2019, 5.57299507691, 1.97946388670, 0.43440652133, 2.07555674785, 0.43011874973, 0.39182587567, 1.34610787462,
     0.36976443287, 0.69252750258, 0.85730102277],
    [2020, 5.74627730839, 1.99041249786, 0.44008041032, 2.16219839398, 0.44789809816, 0.40442896888, 1.39630704399,
     0.39308716559, 0.69654676805, 0.85943289630],
    [2021, 5.91954963603, 2.00201716680, 0.44591841591, 2.24784380750, 0.46644791211, 0.41752116955, 1.44452488090,
     0.41714095005, 0.70060508226, 0.86205581512],
    [2022, 6.09281852461, 2.01425222862, 0.45191086651, 2.33257051665, 0.48579150618, 0.43109395687, 1.49081823780,
     0.44191715646, 0.70471360255, 0.86515052330],
    [2023, 6.26609043893, 2.02709201843, 0.45804809052, 2.41645604963, 0.50595219495, 0.44513881001, 1.53524396711,
     0.46740715499, 0.70888348625, 0.86869776493],
    [2024, 6.43937184379, 2.04051087134, 0.46432041634, 2.49957793469, 0.52695329301, 0.45964720815, 1.57785892129,
     0.49360231583, 0.71312589069, 0.87267828410],
    [2025, 6.61266920398, 2.05448312247, 0.47071817236, 2.58201370003, 0.54881811493, 0.47461063047, 1.61871995279,
     0.52049400918, 0.71745197321, 0.87707282490],
    [2026, 6.78598898429, 2.06898310692, 0.47723168701, 2.66384087388, 0.57156997532, 0.49002055616, 1.65788391403,
     0.54807360521, 0.72187289113, 0.88186213141],
    [2027, 6.95933764951, 2.08398515980, 0.48385128866, 2.74513698447, 0.59523218875, 0.50586846439, 1.69540765748,
     0.57633247411, 0.72639980178, 0.88702694773],
    [2028, 7.13272166445, 2.09946361624, 0.49056730573, 2.82597956001, 0.61982806980, 0.52214583433, 1.73134803557,
     0.60526198608, 0.73104386251, 0.89254801792],
    [2029, 7.30614749389, 2.11539281133, 0.49737006663, 2.90644612874, 0.64538093307, 0.53884414518, 1.76576190074,
     0.63485351130, 0.73581623064, 0.89840608610],
    [2030, 7.47962160264, 2.13174708019, 0.50424989974, 2.98661421886, 0.67191409314, 0.55595487611, 1.79870610544,
     0.66509841995, 0.74072806349, 0.90458189633],
    [2031, 7.65315045548, 2.14850075794, 0.51119713347, 3.06656135861, 0.69945086460, 0.57346950629, 1.83023750212,
     0.69598808222, 0.74579051842, 0.91105619271],
    [2032, 7.82674051720, 2.16562817967, 0.51820209622, 3.14636507621, 0.72801456202, 0.59137951492, 1.86041294321,
     0.72751386830, 0.75101475274, 0.91780971932],
    [2033, 8.00039825262, 2.18310368051, 0.52525511641, 3.22610289989, 0.75762850001, 0.60967638116, 1.88928928116,
     0.75966714838, 0.75641192379, 0.92482322026],
    [2034, 8.17413012651, 2.20090159556, 0.53234652241, 3.30585235785, 0.78831599313, 0.62835158419, 1.91692336842,
     0.79243929265, 0.76199318889, 0.93207743960],
    [2035, 8.34794260367, 2.21899625993, 0.53946664265, 3.38569097833, 0.82010035599, 0.64739660321, 1.94337205743,
     0.82582167128, 0.76776970539, 0.93955312144],
    [2036, 8.52184214889, 2.23736200874, 0.54660580552, 3.46569628955, 0.85300490315, 0.66680291738, 1.96869220062,
     0.85980565447, 0.77375263062, 0.94723100986],
    [2037, 8.69583522698, 2.25597317710, 0.55375433942, 3.54594581973, 0.88705294922, 0.68656200588, 1.99294065045,
     0.89438261241, 0.77995312190, 0.95509184895],
    [2038, 8.86992830273, 2.27480410011, 0.56090257275, 3.62651709710, 0.92226780877, 0.70666534791, 2.01617425936,
     0.92954391528, 0.78638233657, 0.96311638279],
    [2039, 9.04412784092, 2.29382911289, 0.56804083392, 3.70748764988, 0.95867279639, 0.72710442262, 2.03844987980,
     0.96528093327, 0.79305143195, 0.97128535548],
    [2040, 9.21844030636, 2.31302255056, 0.57515945133, 3.78893500629, 0.99629122667, 0.74787070921, 2.05982436420,
     1.00158503656, 0.79997156539, 0.97957951109],
    [2041, 9.39287216384, 2.33235874821, 0.58224875337, 3.87093669455, 1.03514641418, 0.76895568685, 2.08035456501,
     1.03844759535, 0.80715389422, 0.98797959372],
    [2042, 9.56742987814, 2.35181204096, 0.58929906846, 3.95357024288, 1.07526167353, 0.79035083473, 2.10009733467,
     1.07585997982, 0.81460957575, 0.99646634746],
    [2043, 9.74211991408, 2.37135676393, 0.59630072499, 4.03691317952, 1.11666031929, 0.81204763201, 2.11910952563,
     1.11381356015, 0.82234976734, 1.00502051638],
    [2044, 9.91694873644, 2.39096725222, 0.60324405137, 4.12104303268, 1.15936566604, 0.83403755789, 2.13744799034,
     1.15229970654, 0.83038562630, 1.01362284458],
    [2045, 10.09192281001, 2.41061784094, 0.61011937599, 4.20603733058, 1.20340102838, 0.85631209154, 2.15516958122,
     1.19130978917, 0.83872830998, 1.02225407615],
    [2046, 10.26704859959, 2.43028286521, 0.61691702726, 4.29197360145, 1.24878972090, 0.87886271214, 2.17233115074,
     1.23083517822, 0.84738897570, 1.03089495516],
    [2047, 10.44233256998, 2.44993666014, 0.62362733358, 4.37892937351, 1.29555505816, 0.90168089887, 2.18898955133,
     1.27086724390, 0.85637878079, 1.03952622571],
    [2048, 10.61778118597, 2.46955356084, 0.63024062335, 4.46698217499, 1.34372035477, 0.92475813091, 2.20520163543,
     1.31139735637, 0.86570888259, 1.04812863188],
    [2049, 10.79340091235, 2.48910790241, 0.63674722497, 4.55620953410, 1.39330892530, 0.94808588744, 2.22102425550,
     1.35241688584, 0.87539043843, 1.05668291777],
    [2050, 10.96919821391, 2.50857401997, 0.64313746685, 4.64668897907, 1.44434408435, 0.97165564763, 2.23651426397,
     1.39391720248, 0.88543460564, 1.06516982745],
    [2051, 11.14517955546, 2.52792624864, 0.64940167739, 4.73849803812, 1.49684914649, 0.99545889068, 2.25172851328,
     1.43588967648, 0.89585254155, 1.07357010502],
    [2052, 11.32135140178, 2.54713892352, 0.65553018499, 4.83171423947, 1.55084742632, 1.01948709575, 2.26672385589,
     1.47832567803, 0.90665540350, 1.08186449456],
    [2053, 11.49772021768, 2.56618637972, 0.66151331804, 4.92641511136, 1.60636223842, 1.04373174203, 2.28155714423,
     1.52121657733, 0.91785434881, 1.09003374016],
    [2054, 11.67429246794, 2.58504295235, 0.66734140496, 5.02267818199, 1.66341689737, 1.06818430869, 2.29628523075,
     1.56455374454, 0.92946053482, 1.09805858590],
    [2055, 11.85107461736, 2.60368297653, 0.67300477414, 5.12058097960, 1.72203471776, 1.09283627492, 2.31096496789,
     1.60832854987, 0.94148511886, 1.10591977588],
    [2056, 12.02807313073, 2.62208078736, 0.67849375399, 5.22020103240, 1.78223901418, 1.11767911990, 2.32565320810,
     1.65253236350, 0.95393925826, 1.11359805417],
    [2057, 12.20529447285, 2.64021071997, 0.68379867291, 5.32161586862, 1.84405310120, 1.14270432280, 2.34040680381,
     1.69715655561, 0.96683411036, 1.12107416487],
    [2058, 12.38274510851, 2.65804710945, 0.68890985929, 5.42490301648, 1.90750029343, 1.16790336280, 2.35528260748,
     1.74219249640, 0.98018083248, 1.12832885206],
    [2059, 12.56043150251, 2.67556429092, 0.69381764155, 5.53014000421, 1.97260390544, 1.19326771908, 2.37033747155,
     1.78763155604, 0.99399058196, 1.13534285983],
    [2060, 12.73836011964, 2.69273659948, 0.69851234808, 5.63740436002, 2.03938725182, 1.21878887083, 2.38562824845,
     1.83346510474, 1.00827451613, 1.14209693227]]

soln_pds_new_iunits_reqd_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
     'China', 'India', 'EU', 'USA'],
    [2014, None, None, None, None, None, None, None, None, None, None],
    [2015, 0.0345381838652173, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2016, 0.0520128499184754, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2017, 0.0604223807557696, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2018, 0.0684542942080606, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2019, 0.0761085902753482, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2020, 0.00241831097882528, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2021, 0.17125128823372, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2022, 0.0968057741671903, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2023, 0.102949600694464, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2024, 0.108715809836735, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2025, 0.0314444192029726, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2026, 0.201775358357296, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2027, 0.123748732953527, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2028, 0.128004472555784, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2029, 0.131882594773037, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2030, 0.199094817307635, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2031, 0.0747942693501868, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2032, 0.141251257114778, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2033, 0.143618909792018, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2034, 0.145608945084255, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2035, 0.147221362991488, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2036, 0.148456163513718, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2037, 0.149313346650944, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2038, 0.149792912403169, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2039, 0.149894860770387, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2040, 0.175385864675128, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2041, 0.123199232427293, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2042, 0.182473185427243, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2043, 0.198539330307708, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2044, 0.205162722587205, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2045, 0.211030880096696, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2046, 0.216143802836179, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2047, 0.139534532826849, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2048, 0.305070901983933, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2049, 0.22695116243459, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2050, 0.215731944792336, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2051, 0.243691096285204, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2052, 0.148301426711909, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2053, 0.313447670843405, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2054, 0.229858733031804, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2055, 0.228174542841226, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2056, 0.225735117880642, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2057, 0.286252175852399, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2058, 0.154878845947108, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2059, 0.213885434378849, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2060, 0.208425070338238, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

soln_ref_new_iunits_reqd_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
     'China', 'India', 'EU', 'USA'],
    [2014, None, None, None, None, None, None, None, None, None, None],
    [2015, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2016, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2017, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2018, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2019, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2020, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2021, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2022, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2023, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2024, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2025, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2026, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2027, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2028, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2029, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2030, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2031, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2032, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2033, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2034, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2035, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2036, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2037, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2038, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2039, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2040, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2041, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2042, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2043, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2044, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2045, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2046, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2047, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2048, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2049, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2050, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2051, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2052, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2053, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2054, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2055, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2056, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2057, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2058, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2059, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2060, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367]]

# Note that the 'Lifetime', 37.00, ... values are what appears in the spreadsheet at that location. It
# differs from the soln_pds and soln_ref tables in that row.
conv_ref_new_iunits_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
     'China', 'India', 'EU', 'USA'],
    ['Lifetime', 37.00, 37.00, 37.00, 37.00, 37.00, 37.00, 37.00, 37.00, 37.00, 37.00],
    [2015, 0.01196107466, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 0.01846675143, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 0.02159755171, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 0.02458776809, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 0.02743740058, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 0.00000310591, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 0.06285825712, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 0.03514279466, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 0.03743009156, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 0.03957680456, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 0.01080929112, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 0.07422212143, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 0.04517344019, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 0.04675781761, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 0.04820161112, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 0.07322417769, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 0.02694808953, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 0.05168948830, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 0.05257094623, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 0.05331182027, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 0.05391211041, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 0.05437181665, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 0.05469093900, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 0.05486947745, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 0.05490743200, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 0.06439752648, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 0.04496886559, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 0.05417779227, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 0.05365341124, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 0.05298844631, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 0.05218289748, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 0.05123676476, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 0.05015004813, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 0.04892274762, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 0.04755486320, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 0.04109074236, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 0.04935299521, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 0.04260770657, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 0.05263856124, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 0.05707343410, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 0.05799284659, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 0.05863109128, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 0.05898816818, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 0.02892073402, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 0.08900216185, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 0.05837239211, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil "First Cost"!C37:C82
soln_pds_install_cost_per_iunit_nparray = np.array([
    [2015, 1444939544214.85], [2016, 1260211854559.48], [2017, 1131125771261.71],
    [2018, 1034176540754.27], [2019, 957914360042.17], [2020, 955853826404.52],
    [2021, 844363092072.89], [2022, 800615041745.80], [2023, 762954261503.24],
    [2024, 730136123170.93], [2025, 721678325520.19], [2026, 675595934758.92],
    [2027, 652654395751.15], [2028, 632005749879.43], [2029, 613318626692.05],
    [2030, 588974654797.70], [2031, 580807336513.56], [2032, 566583683816.19],
    [2033, 553503708701.86], [2034, 541440613073.64], [2035, 530286923303.66],
    [2036, 519950919467.44], [2037, 510353842407.28], [2038, 501427686348.92],
    [2039, 493113437720.23], [2040, 484074786193.61], [2041, 478121333143.78],
    [2042, 471358936327.06], [2043, 465037653845.78], [2044, 459126747449.31],
    [2045, 453599023283.05], [2046, 448430388622.18], [2047, 443599480377.26],
    [2048, 439087352857.46], [2049, 434877214846.06], [2050, 431361401332.87],
    [2051, 427305220575.04], [2052, 423918730328.15], [2053, 420784674297.91],
    [2054, 417894340462.60], [2055, 415240279798.58], [2056, 412816236436.15],
    [2057, 410617094526.91], [2058, 408638840847.23], [2059, 406878542591.41],
    [2060, 405334340227.07]])

# SolarPVUtil "First Cost"!L37:L82
soln_ref_install_cost_per_iunit_nparray = np.array([
    [2015, 1444939544214.85], [2016, 1428094804476.75], [2017, 1412040401146.06],
    [2018, 1396713300701.40], [2019, 1382057429062.82], [2020, 1368022703608.46],
    [2021, 1354564225858.61], [2022, 1341641604099.87], [2023, 1329218381829.52],
    [2024, 1317261552938.44], [2025, 1305741148426.15], [2026, 1294629882446.35],
    [2027, 1283902847828.80], [2028, 1273537253070.74], [2029, 1263512194254.57],
    [2030, 1253808456515.32], [2031, 1244408340617.21], [2032, 1235295510953.90],
    [2033, 1226454861899.16], [2034, 1217872399934.28], [2035, 1209535139387.41],
    [2036, 1201431009956.79], [2037, 1193548774468.46], [2038, 1185877955550.05],
    [2039, 1178408770095.10], [2040, 1171132070553.72], [2041, 1164039292221.12],
    [2042, 1157122405809.40], [2043, 1150373874685.44], [2044, 1143786616238.99],
    [2045, 1137353966915.75], [2046, 1131069650509.32], [2047, 1124927749357.55],
    [2048, 1118922678132.44], [2049, 1113049159950.79], [2050, 1107302204565.43],
    [2051, 1101677088425.20], [2052, 1096169336416.45], [2053, 1090774705120.23],
    [2054, 1085489167437.89], [2055, 1080308898454.35], [2056, 1075230262422.28],
    [2057, 1070249800763.29], [2058, 1065364220992.90], [2059, 1060570386486.19],
    [2060, 1055865307009.24]])

# SolarPVUtil "First Cost"!O37:O82
conv_ref_install_cost_per_iunit_nparray = np.array([
    [2015, 2005749716919.21], [2016, 2003709559856.43], [2017, 2001740610594.36],
    [2018, 1999838071911.36], [2019, 1997997609222.97], [2020, 1996215293069.34],
    [2021, 1994487550260.54], [2022, 1992811122162.61], [2023, 1991183028908.37],
    [2024, 1989600538551.80], [2025, 1988061140369.17], [2026, 1986562521656.05],
    [2027, 1985102547485.31], [2028, 1983679242984.24], [2029, 1982290777764.18],
    [2030, 1980935452196.45], [2031, 1979611685278.25], [2032, 1978318003872.66],
    [2033, 1977053033140.28], [2034, 1975815488007.72], [2035, 1974604165541.04],
    [2036, 1973417938111.51], [2037, 1972255747256.95], [2038, 1971116598155.42],
    [2039, 1969999554639.64], [2040, 1968903734689.63], [2041, 1967828306349.86],
    [2042, 1966772484023.75], [2043, 1965735525104.47], [2044, 1964716726906.07],
    [2045, 1963715423863.49], [2046, 1962730984973.61], [2047, 1961762811452.90],
    [2048, 1960810334590.08], [2049, 1959873013774.63], [2050, 1958950334684.14],
    [2051, 1958041807615.42], [2052, 1957146965945.90], [2053, 1956265364713.38],
    [2054, 1955396579303.22], [2055, 1954540204233.54], [2056, 1953695852029.72],
    [2057, 1952863152180.40], [2058, 1952041750168.08], [2059, 1951231306567.92],
    [2060, 1950431496209.24]])

# SolarPVUtil "First Cost"!E37:E82
soln_pds_annual_world_first_cost_nparray = np.array([
    [2015, 49905587652.22], [2016, 65547210056.69], [2017, 68345312033.84],
    [2018, 70793825183.87], [2019, 72905511547.32], [2020, 2311551802.55],
    [2021, 144598267254.49], [2022, 77504158926.10], [2023, 78545836569.90],
    [2024, 79377339921.58], [2025, 22692755797.36], [2026, 136318611840.71],
    [2027, 80765154530.75], [2028, 80899562665.54], [2029, 80886051910.78],
    [2030, 117261801295.78], [2031, 43441060367.76], [2032, 80030657599.76],
    [2033, 79493599209.60], [2034, 78838596495.43], [2035, 78069563625.33],
    [2036, 77189918719.57], [2037, 76202640186.00], [2038, 75110313497.79],
    [2039, 73915170091.08], [2040, 84899874943.99], [2041, 58904181250.43],
    [2042, 86010366591.19], [2043, 92328264362.41], [2044, 94195693519.31],
    [2045, 95723401094.42], [2046, 96925449504.10], [2047, 61897446256.67],
    [2048, 133952774785.96], [2049, 98695889425.63], [2050, 93058434017.89],
    [2051, 104130477650.32], [2052, 62867752517.57], [2053, 131893976085.28],
    [2054, 96056663639.89], [2055, 94747261012.30], [2056, 93187121794.96],
    [2057, 117540036750.52], [2058, 63289512079.58], [2059, 87025393821.60],
    [2060, 84481838372.33]])

# SolarPVUtil "First Cost"!N37:N82
soln_ref_annual_world_first_cost_nparray = np.array([
    [2015, 3482258521.23], [2016, 3441663232.15], [2017, 3402972628.78],
    [2018, 3366034802.32], [2019, 3330714616.02], [2020, 3296891372.34],
    [2021, 3264456867.37], [2022, 3233313758.36], [2023, 3203374186.30],
    [2024, 3174558607.50], [2025, 3146794797.63], [2026, 3120016998.66],
    [2027, 3094165185.10], [2028, 3069184430.14], [2029, 3045024356.02],
    [2030, 3021638655.52], [2031, 2998984674.03], [2032, 2977023043.26],
    [2033, 2955717359.14], [2034, 2935033897.73], [2035, 2914941363.96],
    [2036, 2895410668.80], [2037, 2876414731.01], [2038, 2857928300.45],
    [2039, 2839927800.15], [2040, 2822391184.80], [2041, 2805297813.74],
    [2042, 5577256673.28], [2043, 5544729180.90], [2044, 5512979012.60],
    [2045, 5481974050.47], [2046, 5451684043.61], [2047, 5422080469.25],
    [2048, 5393136406.46], [2049, 5364826421.01], [2050, 5337126460.22],
    [2051, 5310013756.86], [2052, 5283466741.19], [2053, 5257464960.18],
    [2054, 5231989003.48], [2055, 5207020435.23], [2056, 5182541731.37],
    [2057, 5158536221.77], [2058, 5134988036.86], [2059, 5111882058.30],
    [2060, 5089203873.37]])

# SolarPVUtil "First Cost"!Q37:Q82
conv_ref_annual_world_first_cost_nparray = np.array([
    [2015, 23990922121.35], [2016, 37002006377.58], [2017, 43232696345.06],
    [2018, 49171554733.95], [2019, 54819860759.44], [2020, 6200056.19],
    [2021, 125370011265.80], [2022, 70032952058.20], [2023, 74530163079.95],
    [2024, 78742031667.77], [2025, 21489531621.24], [2026, 147446884706.03],
    [2027, 89673911197.87], [2028, 92752512230.40], [2029, 95549609205.27],
    [2030, 145052369536.31], [2031, 53346752937.10], [2032, 102258245318.98],
    [2033, 103935548708.06], [2034, 105334320183.91], [2035, 106455077787.31],
    [2036, 107298318307.97], [2037, 107864518760.06], [2038, 108154137726.00],
    [2039, 108167616582.81], [2040, 126792530383.75], [2041, 88491006611.85],
    [2042, 106555391090.20], [2043, 105468416516.60], [2044, 104107286794.25],
    [2045, 102472360643.17], [2046, 100563985754.45], [2047, 98382499420.65],
    [2048, 95928229120.13], [2049, 93201493059.41], [2050, 80494723496.87],
    [2051, 96635227949.86], [2052, 83389543648.21], [2053, 102974994195.43],
    [2054, 111601197813.73], [2055, 113349350213.04], [2056, 114547319830.92],
    [2057, 115195820046.09], [2058, 56454480248.00], [2059, 173663804562.34],
    [2060, 113851352078.09]])

# SolarPVUtil "Unit Adoption Calculations"!R252:R298
conv_ref_tot_iunits_for_fc_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
     'Latin America', 'China', 'India', 'EU', 'USA'],
    [2014, 4.51635400373752, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2015, 4.85919669275670, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2016, 5.03185686014748, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2017, 5.20448141432579, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2018, 5.37707679300453, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2019, 5.54964943389661, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2020, 5.72220577471493, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2021, 5.89475225317238, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2022, 6.06729530698188, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2023, 6.23984137385633, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2024, 6.41239689150862, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2025, 6.58496829765166, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2026, 6.75756202999835, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2027, 6.93018452626160, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2028, 7.10284222415430, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2029, 7.27554156138937, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2030, 7.44828897567969, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2031, 7.62109090473818, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2032, 7.79395378627773, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2033, 7.96688405801125, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2034, 8.13988815765164, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2035, 8.31297252291180, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2036, 8.48614359150463, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2037, 8.65940780114305, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2038, 8.83277158953994, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2039, 9.00624139440822, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2040, 9.17982365346077, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2041, 9.35352480441052, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2042, 9.52735128497035, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2043, 9.70130953285318, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2044, 9.87540598577190, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2045, 10.04964708143940, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2046, 10.22403925756860, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2047, 10.39858895187240, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2048, 10.57330260206370, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2049, 10.74818664585550, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2050, 10.92324752096050, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2051, 11.09849166509170, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2052, 11.27392551596210, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2053, 11.44955551128440, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2054, 11.62538808877170, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2055, 11.80142968613680, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2056, 11.97768674109260, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2057, 12.15416569135210, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2058, 12.33087297462800, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2059, 12.50781502863340, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2060, 12.68499829108110, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# SolarPVUtil "First Cost"!Q37:Q82 with R37:R82 changed to
# ='Unit Adoption Calculations'!R253-'Unit Adoption Calculations'!R252  (etc)
conv_ref_annual_world_first_cost_tot_iunits_nparray = np.array([
    [2015, 687656626448.04], [2016, 345960828007.32], [2017, 345549580484.47],
    [2018, 345162809317.71], [2019, 344799723919.67], [2020, 344459606457.61],
    [2021, 344141803124.70], [2022, 343845716683.47], [2023, 343570800065.28],
    [2024, 343316550851.08], [2025, 343082506491.85], [2026, 342868240152.67],
    [2027, 342673357085.45], [2028, 342497491451.20], [2029, 342340303527.05],
    [2030, 342201477242.97], [2031, 342080718002.81], [2032, 341977750751.00],
    [2033, 341892318252.53], [2034, 341824179558.32], [2035, 341773108632.75],
    [2036, 341738893123.04], [2037, 341721333253.30], [2038, 341720240828.22],
    [2039, 341735438333.93], [2040, 341766758124.45], [2041, 341814041684.46],
    [2042, 341877138959.77], [2043, 341955907748.20], [2044, 342050213144.42],
    [2045, 342159927033.17], [2046, 342284927625.78], [2047, 342425099035.69],
    [2048, 342580330889.08], [2049, 342750517967.17], [2050, 342935559877.08],
    [2051, 343135360748.74], [2052, 343349828955.11], [2053, 343578876853.90],
    [2054, 343822420548.69], [2055, 344080379667.57], [2056, 344352677158.15],
    [2057, 344639239097.14], [2058, 344939994513.46], [2059, 345254875223.75],
    [2060, 345583815679.15]])

# SolarPVUtil "First Cost"!F37:F82
pds_cumulative_install_nparray = np.array([
    [2015, 49905587652.22], [2016, 115452797708.90], [2017, 183798109742.74],
    [2018, 254591934926.61], [2019, 327497446473.93], [2020, 329808998276.48],
    [2021, 474407265530.97], [2022, 551911424457.07], [2023, 630457261026.96],
    [2024, 709834600948.55], [2025, 732527356745.90], [2026, 868845968586.61],
    [2027, 949611123117.37], [2028, 1030510685782.91], [2029, 1111396737693.69],
    [2030, 1228658538989.46], [2031, 1272099599357.22], [2032, 1352130256956.98],
    [2033, 1431623856166.58], [2034, 1510462452662.01], [2035, 1588532016287.33],
    [2036, 1665721935006.90], [2037, 1741924575192.90], [2038, 1817034888690.69],
    [2039, 1890950058781.77], [2040, 1975849933725.76], [2041, 2034754114976.19],
    [2042, 2120764481567.39], [2043, 2213092745929.79], [2044, 2307288439449.10],
    [2045, 2403011840543.53], [2046, 2499937290047.63], [2047, 2561834736304.30],
    [2048, 2695787511090.27], [2049, 2794483400515.90], [2050, 2887541834533.78],
    [2051, 2991672312184.11], [2052, 3054540064701.67], [2053, 3186434040786.95],
    [2054, 3282490704426.85], [2055, 3377237965439.15], [2056, 3470425087234.11],
    [2057, 3587965123984.63], [2058, 3651254636064.21], [2059, 3738280029885.81],
    [2060, 3822761868258.14]])

# SolarPVUtil "First Cost"!R37:R82
ref_cumulative_install_nparray = np.array([
    [2015, 27473180642.58], [2016, 67916850252.30], [2017, 114552519226.14],
    [2018, 167090108762.41], [2019, 225240684137.87], [2020, 228543775566.41],
    [2021, 357178243699.58], [2022, 430444509516.14], [2023, 508178046782.39],
    [2024, 590094637057.66], [2025, 614730963476.53], [2026, 765297865181.21],
    [2027, 858065941564.18], [2028, 953887638224.72], [2029, 1052482271786.01],
    [2030, 1200556279977.84], [2031, 1256902017588.96], [2032, 1362137285951.21],
    [2033, 1469028552018.41], [2034, 1577297906100.04], [2035, 1686667925251.31],
    [2036, 1796861654228.08], [2037, 1907602587719.15], [2038, 2018614653745.60],
    [2039, 2129622198128.56], [2040, 2259237119697.11], [2041, 2350533424122.71],
    [2042, 2462666071886.19], [2043, 2573679217583.69], [2044, 2683299483390.53],
    [2045, 2791253818084.18], [2046, 2897269487882.23], [2047, 3001074067772.13],
    [2048, 3102395433298.72], [2049, 3200961752779.14], [2050, 3286793602736.23],
    [2051, 3388738844442.95], [2052, 3477411854832.34], [2053, 3585644313987.95],
    [2054, 3702477500805.16], [2055, 3821033871453.43], [2056, 3940763733015.72],
    [2057, 4061118089283.58], [2058, 4122707557568.43], [2059, 4301483244189.08],
    [2060, 4420423800140.54]])

# ImprovedCookStoves 'Unit Adoption Calculations'!Q251:AA298
conv_ref_tot_iunits_cookstoves_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
     'China', 'India', 'EU', 'USA'],
    [2014, 3459768305.219460, 0.0, 0.0, 2400036400.868050, 1059583372.984360, 81224840.734370, 647332299.811139,
     966608684.629265, 0.0, 0.0],
    [2015, 3082774868.067660, 0.0, 0.0, 2406093206.523950, 1077370808.498250, 81190653.766277, 645351616.515017,
     970761686.381095, 0.0, 0.0],
    [2016, 3061616339.888600, 0.0, 0.0, 2411615646.508290, 1096785024.058630, 81255779.730429, 643042231.440560,
     977569891.850606, 0.0, 0.0],
    [2017, 3045544944.672860, 0.0, 0.0, 2416771630.000820, 1116277796.490000, 81304461.351923, 640280552.988342,
     984210184.803298, 0.0, 0.0],
    [2018, 3034328506.270050, 0.0, 0.0, 2421561065.366360, 1135846727.299340, 81336802.227080, 637089856.576712,
     990682052.067734, 0.0, 0.0],
    [2019, 3027734848.529750, 0.0, 0.0, 2425983860.969720, 1155489417.993660, 81352905.952223, 633493417.624019,
     996984980.472479, 0.0, 0.0],
    [2020, 3025531795.301560, 0.0, 0.0, 2430039925.175720, 1175203470.079970, 81352876.123673, 629514511.548611,
     1003118456.846100, 0.0, 0.0],
    [2021, 3027487170.435070, 0.0, 0.0, 2433729166.349180, 1194986485.065250, 81336816.337753, 625176413.768837,
     1009081968.017150, 0.0, 0.0],
    [2022, 3033368797.779890, 0.0, 0.0, 2437051492.854910, 1214836064.456510, 81304830.190783, 620502399.703045,
     1014875000.814200, 0.0, 0.0],
    [2023, 3042944501.185600, 0.0, 0.0, 2440006813.057720, 1234749809.760760, 81257021.279086, 615515744.769584,
     1020497042.065820, 0.0, 0.0],
    [2024, 3055982104.501810, 0.0, 0.0, 2442595035.322440, 1254725322.484980, 81193493.198983, 610239724.386803,
     1025947578.600570, 0.0, 0.0],
    [2025, 3072249431.578100, 0.0, 0.0, 2444816068.013890, 1274760204.136190, 81114349.546797, 604697613.973050,
     1031226097.247010, 0.0, 0.0],
    [2026, 3091514306.264080, 0.0, 0.0, 2446669819.496870, 1294852056.221390, 81019693.918850, 598912688.946673,
     1036332084.833710, 0.0, 0.0],
    [2027, 3113544552.409330, 0.0, 0.0, 2448156198.136200, 1314998480.247560, 80909629.911462, 592908224.726022,
     1041265028.189230, 0.0, 0.0],
    [2028, 3138107993.863460, 0.0, 0.0, 2449275112.296710, 1335197077.721730, 80784261.120956, 586707496.729445,
     1046024414.142130, 0.0, 0.0],
    [2029, 3164972454.476060, 0.0, 0.0, 2450026470.343200, 1355445450.150870, 80643691.143654, 580333780.375291,
     1050609729.520980, 0.0, 0.0],
    [2030, 3193905758.096730, 0.0, 0.0, 2450410180.640490, 1375741199.042000, 80488023.575878, 573810351.081908,
     1055020461.154340, 0.0, 0.0],
    [2031, 3224675728.575050, 0.0, 0.0, 2450426151.553410, 1396081925.902120, 80317362.013948, 567160484.267645,
     1059256095.870780, 0.0, 0.0],
    [2032, 3257050189.760640, 0.0, 0.0, 2450074291.446760, 1416465232.238230, 80131810.054188, 560407455.350850,
     1063316120.498870, 0.0, 0.0],
    [2033, 3290796965.503070, 0.0, 0.0, 2449354508.685370, 1436888719.557320, 79931471.292919, 553574539.749872,
     1067200021.867150, 0.0, 0.0],
    [2034, 3325683879.651950, 0.0, 0.0, 2448266711.634040, 1457349989.366400, 79716449.326463, 546685012.883060,
     1070907286.804210, 0.0, 0.0],
    [2035, 3361478756.056880, 0.0, 0.0, 2446810808.657600, 1477846643.172470, 79486847.751141, 539762150.168762,
     1074437402.138590, 0.0, 0.0],
    [2036, 3397949418.567440, 0.0, 0.0, 2444986708.120860, 1498376282.482530, 79242770.163276, 532829227.025327,
     1077789854.698880, 0.0, 0.0],
    [2037, 3434863691.033240, 0.0, 0.0, 2442794318.388640, 1518936508.803580, 78984320.159189, 525909518.871104,
     1080964131.313620, 0.0, 0.0],
    [2038, 3471989397.303860, 0.0, 0.0, 2440233547.825760, 1539524923.642620, 78711601.335203, 519026301.124440,
     1083959718.811390, 0.0, 0.0],
    [2039, 3509094361.228910, 0.0, 0.0, 2437304304.797030, 1560139128.506650, 78424717.287638, 512202849.203685,
     1086776104.020750, 0.0, 0.0],
    [2040, 3545946406.657990, 0.0, 0.0, 2434006497.667270, 1580776724.902670, 78123771.612817, 505462438.527188,
     1089412773.770260, 0.0, 0.0],
    [2041, 3582313357.440670, 0.0, 0.0, 2430340034.801290, 1601435314.337680, 77808867.907061, 498828344.513296,
     1091869214.888490, 0.0, 0.0],
    [2042, 3617963037.426570, 0.0, 0.0, 2426304824.563910, 1622112498.318690, 77480109.766693, 492323842.580359,
     1094144914.204000, 0.0, 0.0],
    [2043, 3652663270.465280, 0.0, 0.0, 2421900775.319950, 1642805878.352690, 77137600.788034, 485972208.146725,
     1096239358.545360, 0.0, 0.0],
    [2044, 3686181880.406390, 0.0, 0.0, 2417127795.434220, 1663513055.946680, 76781444.567406, 479796716.630743,
     1098152034.741120, 0.0, 0.0],
    [2045, 3718286691.099490, 0.0, 0.0, 2411985793.271550, 1684231632.607670, 76411744.701131, 473820643.450761,
     1099882429.619860, 0.0, 0.0],
    [2046, 3748745526.394190, 0.0, 0.0, 2406474677.196740, 1704959209.842660, 76028604.785531, 468067264.025129,
     1101430030.010130, 0.0, 0.0],
    [2047, 3777326210.140080, 0.0, 0.0, 2400594355.574610, 1725693389.158640, 75632128.416927, 462559853.772193,
     1102794322.740500, 0.0, 0.0],
    [2048, 3803796566.186750, 0.0, 0.0, 2394344736.769990, 1746431772.062610, 75222419.191642, 457321688.110304,
     1103974794.639540, 0.0, 0.0],
    [2049, 3827924418.383810, 0.0, 0.0, 2387725729.147680, 1767171960.061580, 74799580.705996, 452376042.457809,
     1104970932.535810, 0.0, 0.0],
    [2050, 3849477590.580840, 0.0, 0.0, 2380737241.072500, 1787911554.662550, 74363716.556313, 447746192.233058,
     1105782223.257870, 0.0, 0.0],
    [2051, 3868223906.627430, 0.0, 0.0, 2373379180.909270, 1808648157.372520, 73914930.338913, 443455412.854399,
     1106408153.634290, 0.0, 0.0],
    [2052, 3883931190.373200, 0.0, 0.0, 2365651457.022810, 1829379369.698490, 73453325.650120, 439526979.740181,
     1106848210.493630, 0.0, 0.0],
    [2053, 3896367265.667730, 0.0, 0.0, 2357553977.777930, 1850102793.147460, 72979006.086253, 435984168.308751,
     1107101880.664450, 0.0, 0.0],
    [2054, 3905299956.360610, 0.0, 0.0, 2349086651.539450, 1870816029.226420, 72492075.243636, 432850253.978460,
     1107168650.975320, 0.0, 0.0],
    [2055, 3910497086.301450, 0.0, 0.0, 2340249386.672180, 1891516679.442390, 71992636.718590, 430148512.167655,
     1107048008.254810, 0.0, 0.0],
    [2056, 3911726479.339840, 0.0, 0.0, 2331042091.540950, 1912202345.302360, 71480794.107436, 427902218.294684,
     1106739439.331470, 0.0, 0.0],
    [2057, 3908755959.325370, 0.0, 0.0, 2321464674.510560, 1932870628.313330, 70956651.006498, 426134647.777898,
     1106242431.033870, 0.0, 0.0],
    [2058, 3901353350.107640, 0.0, 0.0, 2311517043.945840, 1953519129.982300, 70420311.012096, 424869076.035644,
     1105556470.190580, 0.0, 0.0],
    [2059, 3889286475.536250, 0.0, 0.0, 2301199108.211590, 1974145451.816270, 69871877.720552, 424128778.486270,
     1104681043.630160, 0.0, 0.0],
    [2060, 3872323159.460780, 0.0, 0.0, 2290510775.672650, 1994747195.322250, 69311454.728189, 423937030.548126,
     1103615638.181170, 0.0, 0.0]]

# SolarPVUtil "First Cost"!O37:O82
conv_ref_install_cost_per_iunit_cookstoves_nparray = np.array([
    [2015, 2.048761039057], [2016, 2.048761039057], [2017, 2.048761039057], [2018, 2.048761039057],
    [2019, 2.048761039057], [2020, 2.048761039057], [2021, 2.048761039057], [2022, 2.048761039057],
    [2023, 2.048761039057], [2024, 2.048761039057], [2025, 2.048761039057], [2026, 2.048761039057],
    [2027, 2.048761039057], [2028, 2.048761039057], [2029, 2.048761039057], [2030, 2.048761039057],
    [2031, 2.048761039057], [2032, 2.048761039057], [2033, 2.048761039057], [2034, 2.048761039057],
    [2035, 2.048761039057], [2036, 2.048761039057], [2037, 2.048761039057], [2038, 2.048761039057],
    [2039, 2.048761039057], [2040, 2.048761039057], [2041, 2.048761039057], [2042, 2.048761039057],
    [2043, 2.048761039057], [2044, 2.048761039057], [2045, 2.048761039057], [2046, 2.048761039057],
    [2047, 2.048761039057], [2048, 2.048761039057], [2049, 2.048761039057], [2050, 2.048761039057],
    [2051, 2.048761039057], [2052, 2.048761039057], [2053, 2.048761039057], [2054, 2.048761039057],
    [2055, 2.048761039057], [2056, 2.048761039057], [2057, 2.048761039057], [2058, 2.048761039057],
    [2059, 2.048761039057], [2060, 2.048761039057]])

# Alternative Cement 'Unit Adoption Calculations'!AX135:BH182
soln_pds_tot_iunits_reqd_altcement_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 222.222222, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 222.703192, 42.116996, 12.424431, 163.800714, 3.206397, 1.154654, 170.811140, 41.665041, 13.602438,
     16.646779],
    [2016, 609.148337, 117.977901, 27.112990, 412.849266, 33.775844, 17.432336, 325.612968, 65.175302, 13.669529,
     31.277073],
    [2017, 934.565664, 194.599717, 42.254483, 633.389025, 46.440035, 17.882404, 330.589587, 92.201734, 13.878352,
     46.823306],
    [2018, 975.119605, 242.609222, 57.753094, 609.424282, 46.986309, 18.346698, 340.504586, 93.047453, 14.209510,
     63.164601],
    [2019, 973.006043, 237.419406, 73.534464, 595.533069, 47.693902, 18.825203, 354.236377, 91.604222, 14.646482,
     63.119003],
    [2020, 981.751223, 234.366686, 89.540626, 589.967696, 48.558311, 19.317904, 370.886844, 91.658279, 15.175174,
     63.964271],
    [2021, 999.595665, 233.157862, 105.726194, 591.311421, 49.575399, 19.824789, 389.733827, 93.041111, 15.783532,
     65.667799],
    [2022, 1014.465706, 233.544814, 111.422252, 598.411428, 50.741368, 20.345845, 410.194305, 95.613202, 16.461227,
     68.098278],
    [2023, 1030.233806, 235.317091, 111.656705, 610.326224, 52.052729, 20.881058, 431.795728, 99.258692, 17.199388,
     71.149521],
    [2024, 1052.387957, 238.295807, 112.871265, 626.284184, 53.506284, 21.430418, 454.153629, 103.881081, 17.990386,
     74.735321],
    [2025, 1079.978053, 242.328605, 114.905658, 645.650774, 55.099103, 21.993913, 476.954050, 109.399770, 18.827644,
     78.785427],
    [2026, 1050.177794, 235.240633, 110.903042, 627.052313, 54.876971, 22.104835, 463.082817, 108.710778, 18.496449,
     77.519524],
    [2027, 1024.285761, 228.969865, 107.470799, 610.925810, 54.705410, 22.213877, 450.302625, 108.368217, 18.199765,
     76.501339],
    [2028, 1001.775069, 223.424048, 104.523646, 596.924133, 54.582215, 22.321027, 438.456091, 108.327800, 17.934090,
     75.694575],
    [2029, 982.205642, 218.524180, 101.991340, 584.758465, 54.505379, 22.426278, 427.412820, 108.552179, 17.696392,
     75.069237],
    [2030, 965.209294, 214.202593, 99.815894, 574.188102, 54.473085, 22.529619, 417.064573, 109.009827, 17.484047,
     74.600485],
    [2031, 949.210997, 210.388857, 97.549362, 563.837209, 54.754525, 22.681044, 402.321376, 109.589118, 17.311451,
     74.067716],
    [2032, 935.219104, 207.045937, 95.552062, 554.713167, 55.077392, 22.830545, 388.108403, 110.352578, 17.159980,
     73.653835],
    [2033, 923.017422, 204.131586, 93.791163, 546.676188, 55.440368, 22.978116, 374.363452, 111.281265, 17.027947,
     73.344656],
    [2034, 912.425429, 201.609910, 92.239540, 539.609942, 55.842287, 23.123750, 361.034921, 112.359261, 16.913910,
     73.128433],
    [2035, 903.293046, 199.450591, 90.874864, 533.418024, 56.282125, 23.267442, 348.080162, 113.573258, 16.816640,
     72.995475],
    [2036, 895.496395, 197.628251, 89.678868, 528.021095, 56.758994, 23.409187, 335.464166, 114.912214, 16.735104,
     72.937838],
    [2037, 888.934378, 196.121914, 88.636765, 523.354579, 57.272138, 23.548981, 323.158501, 116.367078, 16.668440,
     72.949079],
    [2038, 883.525934, 194.914581, 87.736781, 519.366823, 57.820929, 23.686820, 311.140469, 117.930564, 16.615949,
     73.024061],
    [2039, 879.207875, 193.992878, 86.969792, 516.017643, 58.404859, 23.822702, 299.392442, 119.596974, 16.577076,
     73.158798],
    [2040, 875.933203, 193.346783, 86.329048, 513.277204, 59.023543, 23.956625, 287.901349, 121.362061, 16.551405,
     73.350337],
    [2041, 873.969055, 193.234283, 85.809960, 511.125182, 59.711043, 24.088587, 285.901349, 123.317061, 16.538651,
     73.650337],
    [2042, 872.699055, 193.121783, 85.409960, 509.550182, 60.398543, 24.218587, 283.901349, 125.272061, 16.538651,
     73.950337],
    [2043, 872.119747, 193.009283, 85.128413, 508.549383, 61.086043, 24.346625, 281.901349, 127.227061, 16.551365,
     74.250337],
    [2044, 872.238009, 192.896783, 84.966583, 508.128399, 61.773543, 24.472701, 279.901349, 129.182061, 16.576874,
     74.550337],
    [2045, 873.071140, 192.784283, 84.927648, 508.301349, 62.461043, 24.596817, 277.901349, 131.137061, 16.615377,
     74.850337],
    [2046, 871.801140, 192.671783, 84.527648, 506.726349, 63.148543, 24.726817, 275.901349, 133.092061, 16.615377,
     75.150337],
    [2047, 870.531140, 192.559283, 84.127648, 505.151349, 63.836043, 24.856817, 273.901349, 135.047061, 16.615377,
     75.450337],
    [2048, 869.261140, 192.446783, 83.727648, 503.576349, 64.523543, 24.986817, 271.901349, 137.002061, 16.615377,
     75.750337],
    [2049, 867.991140, 192.334283, 83.327648, 502.001349, 65.211043, 25.116817, 269.901349, 138.957061, 16.615377,
     76.050337],
    [2050, 866.721140, 192.221783, 82.927648, 500.426349, 65.898543, 25.246817, 267.901349, 140.912061, 16.615377,
     76.350337],
    [2051, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2052, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2053, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2054, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2055, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2056, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2057, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2058, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2059, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2060, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]]

# Alternative Cement "First Cost"!C37:C82
soln_pds_install_cost_per_iunit_altcement_nparray = np.array([
    [2015, 32130000.0], [2016, 32130000.0], [2017, 32130000.0], [2018, 32130000.0],
    [2019, 32130000.0], [2020, 32130000.0], [2021, 32130000.0], [2022, 32130000.0],
    [2023, 32130000.0], [2024, 32130000.0], [2025, 32130000.0], [2026, 32130000.0],
    [2027, 32130000.0], [2028, 32130000.0], [2029, 32130000.0], [2030, 32130000.0],
    [2031, 32130000.0], [2032, 32130000.0], [2033, 32130000.0], [2034, 32130000.0],
    [2035, 32130000.0], [2036, 32130000.0], [2037, 32130000.0], [2038, 32130000.0],
    [2039, 32130000.0], [2040, 32130000.0], [2041, 32130000.0], [2042, 32130000.0],
    [2043, 32130000.0], [2044, 32130000.0], [2045, 32130000.0], [2046, 32130000.0],
    [2047, 32130000.0], [2048, 32130000.0], [2049, 32130000.0], [2050, 32130000.0],
    [2051, np.nan], [2052, np.nan], [2053, np.nan], [2054, np.nan], [2055, np.nan],
    [2056, np.nan], [2057, np.nan], [2058, np.nan], [2059, np.nan], [2060, np.nan]])
