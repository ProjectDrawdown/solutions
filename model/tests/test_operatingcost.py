"""Tests for operatingcost.py."""

from model import advanced_controls
from model import operatingcost
import numpy as np
import pandas as pd
import pytest
import pathlib

datadir = pathlib.Path(__file__).parents[0].joinpath('data')


def _defaultOperatingCost(npv_discount_rate=0.094, single_iunit_purchase_year=2017):
    soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
            columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    conv_ref_annual_tot_iunits = pd.DataFrame(conv_ref_annual_tot_iunits_list[1:],
            columns=conv_ref_annual_tot_iunits_list[0]).set_index('Year')
    soln_ref_annual_world_first_cost = pd.Series(
            soln_ref_annual_world_first_cost_nparray[:, 1],
            index=soln_ref_annual_world_first_cost_nparray[:, 0], dtype=np.float64)
    soln_ref_annual_world_first_cost.index = soln_ref_annual_world_first_cost.index.astype(int)
    conv_ref_annual_world_first_cost = pd.Series(
            conv_ref_annual_world_first_cost_nparray[:, 1],
            index=conv_ref_annual_world_first_cost_nparray[:, 0], dtype=np.float64)
    conv_ref_annual_world_first_cost.index = conv_ref_annual_world_first_cost.index.astype(int)
    soln_pds_annual_world_first_cost = pd.Series(
            soln_pds_annual_world_first_cost_nparray[:, 1],
            index=soln_pds_annual_world_first_cost_nparray[:, 0], dtype=np.float64)
    soln_pds_annual_world_first_cost.index = soln_pds_annual_world_first_cost.index.astype(int)
    soln_pds_install_cost_per_iunit = pd.Series(soln_pds_install_cost_per_iunit_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    conv_ref_install_cost_per_iunit = pd.Series(conv_ref_install_cost_per_iunit_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)

    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_lifetime_capacity=182411.275767661, conv_avg_annual_use=4946.840187342,
            soln_lifetime_capacity=48343.8, soln_avg_annual_use=1841.66857142857,
            conv_var_oper_cost_per_funit=0.00375269040, conv_fuel_cost_per_funit=0.0731,
            conv_fixed_oper_cost_per_iunit=32.95140431108,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=23.18791293579,
            npv_discount_rate=npv_discount_rate)
    oc = operatingcost.OperatingCost(ac=ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_annual_tot_iunits=conv_ref_annual_tot_iunits,
            soln_pds_annual_world_first_cost=soln_pds_annual_world_first_cost,
            soln_ref_annual_world_first_cost=soln_ref_annual_world_first_cost,
            conv_ref_annual_world_first_cost=conv_ref_annual_world_first_cost,
            single_iunit_purchase_year=single_iunit_purchase_year,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit,
            conversion_factor=10 ** 9)
    return oc


def test_soln_pds_annual_breakout():
    oc = _defaultOperatingCost()
    result = oc.soln_pds_annual_breakout()
    filename = datadir.joinpath('oc_soln_pds_annual_breakout_expected.csv')
    expected = pd.read_csv(filename, header=None, index_col=0, skipinitialspace=True,
            dtype=np.float64)
    expected.columns = list(range(2015, 2061))
    expected.name = 'soln_pds_annual_breakout'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_annual_breakout_core():
    oc = _defaultOperatingCost()
    result = oc.soln_pds_annual_breakout_core()
    assert 2014 not in result.index
    assert 2015 in result.index
    assert 2030 in result.index
    assert 2060 in result.index
    assert 2061 not in result.index


def test_conv_ref_annual_breakout():
    oc = _defaultOperatingCost()
    result = oc.conv_ref_annual_breakout()
    filename = datadir.joinpath('oc_conv_ref_annual_breakout_expected.csv')
    expected = pd.read_csv(filename, header=None, index_col=0, skipinitialspace=True,
            dtype=np.float64)
    expected.columns = list(range(2015, 2061))
    expected.name = 'conv_ref_annual_breakout'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_conv_ref_annual_breakout_core():
    oc = _defaultOperatingCost()
    result = oc.conv_ref_annual_breakout_core()
    assert 2014 not in result.index
    assert 2015 in result.index
    assert 2030 in result.index
    assert 2060 in result.index
    assert 2061 not in result.index


def test_soln_pds_annual_operating_cost():
    oc = _defaultOperatingCost()
    result = oc.soln_pds_annual_operating_cost()
    expected = pd.Series(soln_pds_annual_operating_cost_nparray[:, 1],
            index=soln_pds_annual_operating_cost_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    expected.name = 'soln_pds_annual_operating_cost'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_pds_cumulative_operating_cost():
    oc = _defaultOperatingCost()
    result = oc.soln_pds_cumulative_operating_cost()
    expected = pd.Series(soln_pds_cumulative_operating_cost_nparray[:, 1],
            index=soln_pds_cumulative_operating_cost_nparray[:, 0], dtype=np.float64)
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    expected.name = 'soln_pds_cumulative_operating_cost'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_conv_ref_annual_operating_cost():
    oc = _defaultOperatingCost()
    result = oc.conv_ref_annual_operating_cost().iloc[0:46]
    expected = pd.Series(conv_ref_annual_operating_cost_nparray[:, 1],
            index=conv_ref_annual_operating_cost_nparray[:, 0], dtype=np.float64)
    expected.name = 'conv_ref_annual_operating_cost'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_conv_ref_cumulative_operating_cost():
    oc = _defaultOperatingCost()
    result = oc.conv_ref_cumulative_operating_cost()
    expected = pd.Series(conv_ref_cumulative_operating_cost_nparray[:, 1],
            index=conv_ref_cumulative_operating_cost_nparray[:, 0], dtype=np.float64)
    expected.name = 'conv_ref_cumulative_operating_cost'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_marginal_annual_operating_cost():
    oc = _defaultOperatingCost()
    result = oc.marginal_annual_operating_cost()
    expected = pd.Series(marginal_annual_operating_cost_nparray[:, 1],
            index=marginal_annual_operating_cost_nparray[:, 0], dtype=np.float64)
    expected.name = 'marginal_annual_operating_cost'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_pds_new_funits_per_year():
    oc = _defaultOperatingCost()
    expected = pd.DataFrame(soln_pds_new_funits_per_year_list[1:],
            columns=soln_pds_new_funits_per_year_list[0]).set_index('Year')
    expected.name = 'soln_pds_new_funits_per_year'
    expected.index = expected.index.astype(int)
    result = oc.soln_pds_new_funits_per_year()
    # TODO need data to check the rest of the regional columns
    pd.testing.assert_frame_equal(result.loc[2015:, ['World']], expected, check_exact=False)


def test_soln_pds_net_annual_iunits_reqd():
    oc = _defaultOperatingCost()
    expected = pd.DataFrame(soln_pds_net_annual_iunits_reqd_list[1:],
            columns=soln_pds_net_annual_iunits_reqd_list[0]).set_index('Year')
    result = oc.soln_pds_net_annual_iunits_reqd()
    # TODO need data to check the rest of the regional columns
    pd.testing.assert_frame_equal(result.loc[:, ['World']], expected, check_exact=False)


def test_soln_pds_new_annual_iunits_reqd():
    oc = _defaultOperatingCost()
    expected = pd.DataFrame(soln_pds_new_annual_iunits_reqd_list[1:],
            columns=soln_pds_new_annual_iunits_reqd_list[0]).set_index('Year')
    expected.name = 'soln_pds_new_annual_iunits_reqd'
    expected.index = expected.index.astype(int)
    result = oc.soln_pds_new_annual_iunits_reqd()
    # TODO need data to check the rest of the regional columns
    pd.testing.assert_frame_equal(result.loc[2015:, ['World']], expected, check_exact=False)


def test_conv_ref_new_annual_iunits_reqd():
    oc = _defaultOperatingCost()
    expected = pd.DataFrame(conv_ref_new_annual_iunits_reqd_list[1:],
            columns=conv_ref_new_annual_iunits_reqd_list[0]).set_index('Year')
    expected.name = 'conv_ref_new_annual_iunits_reqd'
    expected.index = expected.index.map(int)
    result = oc.conv_ref_new_annual_iunits_reqd()
    pd.testing.assert_frame_equal(result.loc[2015:], expected, check_exact=False)


def test_soln_marginal_first_cost():
    oc = _defaultOperatingCost()
    result = oc.soln_marginal_first_cost()
    expected = pd.Series(soln_marginal_first_cost_nparray[:, 1],
            index=soln_marginal_first_cost_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_marginal_first_cost'
    expected.index = expected.index.astype(int)
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_marginal_operating_cost_savings():
    oc = _defaultOperatingCost()
    result = oc.soln_marginal_operating_cost_savings()
    expected = pd.Series(soln_marginal_operating_cost_savings_nparray[:, 1],
            index=soln_marginal_operating_cost_savings_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_marginal_operating_cost_savings'
    expected.index = expected.index.astype(int)
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_net_cash_flow():
    oc = _defaultOperatingCost()
    result = oc.soln_net_cash_flow()
    expected = pd.Series(soln_net_cash_flow_nparray[:, 1],
            index=soln_net_cash_flow_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_net_cash_flow'
    expected.index = expected.index.astype(int)
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_net_present_value():
    oc = _defaultOperatingCost()
    result = oc.soln_net_present_value()
    expected = pd.Series(soln_net_present_value_nparray[:, 1],
            index=soln_net_present_value_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_net_present_value'
    expected.index = expected.index.astype(int)
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_vs_conv_single_iunit_cashflow():
    oc = _defaultOperatingCost(single_iunit_purchase_year=2017)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    expected = pd.Series(soln_vs_conv_single_iunit_cashflow_nparray[:, 1],
            index=soln_vs_conv_single_iunit_cashflow_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_vs_conv_single_iunit_cashflow'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_vs_conv_single_iunit_cashflow_purchase_year_2026():
    oc = _defaultOperatingCost(single_iunit_purchase_year=2026)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    assert result[2015] == pytest.approx(-18487649169)
    assert result[2016] == pytest.approx(130616812789)


def test_soln_vs_conv_single_iunit_cashflow_improvedcookstoves():
    soln_pds_install_cost_per_iunit = pd.Series(
            soln_pds_install_cost_per_iunit_cookstoves_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_cookstoves_nparray[:, 0],
            dtype=np.float64)
    conv_ref_install_cost_per_iunit = pd.Series(
            conv_ref_install_cost_per_iunit_cookstoves_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_cookstoves_nparray[:, 0],
            dtype=np.float64)
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_lifetime_capacity=2.8590323160579116e-06,
            conv_avg_annual_use=1.6784148689795305e-06,
            soln_lifetime_capacity=7.589875421812185e-06,
            soln_avg_annual_use=1.6784148689795305e-06,
            conv_var_oper_cost_per_funit=45000000.0, conv_fuel_cost_per_funit=0.0,
            conv_fixed_oper_cost_per_iunit=0.0,
            soln_var_oper_cost_per_funit=36000000.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=0.0,
            npv_discount_rate=0.04)
    oc = operatingcost.OperatingCost(ac=ac, soln_net_annual_funits_adopted=None,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit,
            conversion_factor=1.0)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    expected = pd.Series(soln_vs_conv_single_iunit_cashflow_cookstoves_nparray[:, 1],
            index=soln_vs_conv_single_iunit_cashflow_cookstoves_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_vs_conv_single_iunit_cashflow'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result.loc[2015:2023], expected, check_exact=False)


def test_single_iunit_cashflow_instreamhydro():
    soln_pds_install_cost_per_iunit = pd.Series(
            soln_pds_install_cost_per_iunit_instreamhydro_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_instreamhydro_nparray[:, 0],
            dtype=np.float64)
    conv_ref_install_cost_per_iunit = pd.Series(
            conv_ref_install_cost_per_iunit_instreamhydro_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_instreamhydro_nparray[:, 0],
            dtype=np.float64)
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_lifetime_capacity=182411.2757676607,
            conv_avg_annual_use=4946.8401873420025,
            soln_lifetime_capacity=161608.13345783597,
            soln_avg_annual_use=3834.769268491023,
            conv_var_oper_cost_per_funit=0.003752690403548987,
            conv_fuel_cost_per_funit=0.07,
            conv_fixed_oper_cost_per_iunit=32.951404311078015,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=0.0,
            npv_discount_rate=0.063)
    oc = operatingcost.OperatingCost(ac=ac, soln_net_annual_funits_adopted=None,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit,
            conversion_factor=1000000000.0)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    expected = pd.Series(soln_vs_conv_single_iunit_cashflow_instreamhydro_nparray[:, 1],
            index=soln_vs_conv_single_iunit_cashflow_instreamhydro_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_vs_conv_single_iunit_cashflow'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result.loc[2015:2060], expected, check_exact=False)
    result = oc.soln_only_single_iunit_cashflow()
    expected = pd.Series(soln_only_single_iunit_cashflow_instreamhydro_nparray[:, 1],
            index=soln_only_single_iunit_cashflow_instreamhydro_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_only_single_iunit_cashflow'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result.loc[2015:2060], expected.loc[2015:2060],
            check_exact=False)


def test_single_iunit_cashflow_long_soln_lifetime():
    soln_pds_install_cost_per_iunit = pd.Series(
            soln_pds_install_cost_per_iunit_instreamhydro_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_instreamhydro_nparray[:, 0],
            dtype=np.float64)
    conv_ref_install_cost_per_iunit = pd.Series(
            conv_ref_install_cost_per_iunit_instreamhydro_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_instreamhydro_nparray[:, 0],
            dtype=np.float64)
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_lifetime_capacity=20.0, conv_avg_annual_use=1.0,
            soln_lifetime_capacity=88.0, soln_avg_annual_use=1.0,
            conv_var_oper_cost_per_funit=0.003, conv_fuel_cost_per_funit=0.07,
            conv_fixed_oper_cost_per_iunit=32.95,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=0.0,
            npv_discount_rate=0.063)
    oc = operatingcost.OperatingCost(ac=ac, soln_net_annual_funits_adopted=None,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit,
            conversion_factor=1000000000.0)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    assert result.loc[2070] != 0.0
    result = oc.soln_only_single_iunit_cashflow()
    assert result.loc[2070] != 0.0


def test_soln_vs_conv_single_iunit_npv():
    oc = _defaultOperatingCost(single_iunit_purchase_year=2017)
    result = oc.soln_vs_conv_single_iunit_npv()
    expected = pd.Series(soln_vs_conv_single_iunit_npv_nparray[:, 1],
            index=soln_vs_conv_single_iunit_npv_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_vs_conv_single_iunit_npv'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_vs_conv_single_iunit_npv_purchase_year_discount_rate():
    oc = _defaultOperatingCost(npv_discount_rate=0.071, single_iunit_purchase_year=2025)
    result = oc.soln_vs_conv_single_iunit_npv()
    expected = pd.Series(soln_vs_conv_single_iunit_npv_purchase_year_discount_rate_nparray[:, 1],
            index=soln_vs_conv_single_iunit_npv_purchase_year_discount_rate_nparray[:, 0],
            dtype=np.float64)
    expected.name = 'soln_vs_conv_single_iunit_npv'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_vs_conv_single_iunit_payback():
    oc = _defaultOperatingCost()
    result = oc.soln_vs_conv_single_iunit_payback()
    expected = pd.Series(soln_vs_conv_single_iunit_payback_nparray[:, 1],
            index=soln_vs_conv_single_iunit_payback_nparray[:, 0], dtype=np.int64)
    expected.name = 'soln_vs_conv_single_iunit_payback'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_vs_conv_single_iunit_payback_discounted():
    oc = _defaultOperatingCost()
    result = oc.soln_vs_conv_single_iunit_payback_discounted()
    expected = pd.Series(soln_vs_conv_single_iunit_payback_discounted_nparray[:, 1],
            index=soln_vs_conv_single_iunit_payback_discounted_nparray[:, 0],
            dtype=np.int64)
    expected.name = 'soln_vs_conv_single_iunit_payback_discounted'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_only_single_iunit_cashflow():
    oc = _defaultOperatingCost(single_iunit_purchase_year=2017)
    result = oc.soln_only_single_iunit_cashflow()
    expected = pd.Series(soln_only_single_iunit_cashflow_nparray[:, 1],
            index=soln_only_single_iunit_cashflow_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_only_single_iunit_cashflow'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_only_single_iunit_npv():
    oc = _defaultOperatingCost(npv_discount_rate=0.094, single_iunit_purchase_year=2017)
    result = oc.soln_only_single_iunit_npv()
    expected = pd.Series(soln_only_single_iunit_npv_nparray[:, 1],
            index=soln_only_single_iunit_npv_nparray[:, 0], dtype=np.float64)
    expected.name = 'soln_only_single_iunit_npv'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_only_single_iunit_payback():
    oc = _defaultOperatingCost()
    result = oc.soln_only_single_iunit_payback()
    expected = pd.Series(soln_only_single_iunit_payback_nparray[:, 1],
            index=soln_only_single_iunit_payback_nparray[:, 0], dtype=np.int64)
    expected.name = 'soln_only_single_iunit_payback'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_soln_only_single_iunit_payback_discounted():
    oc = _defaultOperatingCost()
    result = oc.soln_only_single_iunit_payback_discounted()
    expected = pd.Series(soln_only_single_iunit_payback_discounted_nparray[:, 1],
            index=soln_only_single_iunit_payback_discounted_nparray[:, 0],
            dtype=np.int64)
    expected.name = 'soln_only_single_iunit_payback_discounted'
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    pd.testing.assert_series_equal(result, expected, check_exact=False)


def test_annual_breakout_no_fractional_years():
    # soln_lifetime_years == 24.000000000000058. The infitesimally small remainder
    # should be less than one cent, and be rounded down to zero.
    soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
            columns=soln_net_annual_funits_adopted_list[0]).set_index( 'Year')
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index( 'Year')
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index( 'Year')
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            soln_lifetime_capacity=41401.1076923077, soln_avg_annual_use=1725.04615384615,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=23.18791293579)
    oc = operatingcost.OperatingCost(ac=ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=None, soln_pds_install_cost_per_iunit=None,
            conv_ref_install_cost_per_iunit=None,
            conversion_factor=10 ** 9)
    result = oc.soln_pds_annual_breakout()
    assert result.loc[2063, 2015] == 0.0
    assert result.loc[2064, 2016] == 0.0
    assert result.loc[2065, 2017] == 0.0
    assert result.loc[2066, 2018] == 0.0
    assert result.loc[2067, 2019] == 0.0


def test_annual_breakout_conversion_factor():
    soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
            columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            soln_lifetime_capacity=41401.1076923077, soln_avg_annual_use=1725.04615384615,
            soln_var_oper_cost_per_funit=17.0, soln_fuel_cost_per_funit=7.0,
            soln_fixed_oper_cost_per_iunit=23.0, conv_var_oper_cost_per_funit=0.0,
            conv_fuel_cost_per_funit=0.0, conv_fixed_oper_cost_per_iunit=0.0)
    oc = operatingcost.OperatingCost(ac=ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=None, soln_pds_install_cost_per_iunit=None,
            conv_ref_install_cost_per_iunit=None, conversion_factor=(27.0, 33.0))
    result = oc.soln_pds_annual_breakout()
    # Expected results from SolarPVUtil with Advanced Controls H128 (var cost) set to 17.0,
    # I128 (fixed cost) set to 23.0, and K128 (fuel cost) set to 7.0 and with Operating Cost
    # E13 (fixed conv factor) set to 27 and E14 (var conv factor) set to 33.
    assert result.loc[2015, 2015] == pytest.approx(46882.2152885102)  # Operating Cost!C262
    assert result.loc[2042, 2018] == pytest.approx(96373.3669039766)  # Operating Cost!F289


def test_annual_breakout_zero_cost_zero_lifetime_replacement():
    soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
            columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            soln_lifetime_capacity=0, soln_avg_annual_use=1725.04615384615,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=0)
    oc = operatingcost.OperatingCost(ac=ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=None, soln_pds_install_cost_per_iunit=None,
            conv_ref_install_cost_per_iunit=None, conversion_factor=1.0)
    result = oc.soln_pds_annual_breakout()
    assert (result == 0).all(axis=None)


def test_annual_breakout_nonzero_cost_zero_lifetime_replacement():
    soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
            columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
    soln_pds_tot_iunits_reqd = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    soln_ref_tot_iunits_reqd = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            soln_lifetime_capacity=0, soln_avg_annual_use=1725.04615384615,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=2)
    oc = operatingcost.OperatingCost(ac=ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=None, soln_pds_install_cost_per_iunit=None,
            conv_ref_install_cost_per_iunit=None, conversion_factor=1.0)
    with pytest.raises(AssertionError):
        result = oc.soln_pds_annual_breakout()


def test_cashflow_no_fractional_years():
    soln_pds_install_cost_per_iunit = pd.Series(soln_pds_install_cost_per_iunit_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    conv_ref_install_cost_per_iunit = pd.Series(conv_ref_install_cost_per_iunit_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_lifetime_capacity=182411.275767661, conv_avg_annual_use=4946.840187342,
            soln_lifetime_capacity=41401.1076923077,
            soln_avg_annual_use=1725.04615384615,
            conv_var_oper_cost_per_funit=0.00375269040, conv_fuel_cost_per_funit=0.0731,
            conv_fixed_oper_cost_per_iunit=32.95140431108,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=23.18791293579)
    oc = operatingcost.OperatingCost(ac=ac, soln_net_annual_funits_adopted=None,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit,
            conversion_factor=10 ** 9)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    assert result[2039] == 0.0
    result = oc.soln_only_single_iunit_cashflow()
    assert result[2039] == 0.0


def test_cashflow_conversion_factor():
    soln_pds_install_cost_per_iunit = pd.Series(soln_pds_install_cost_per_iunit_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    conv_ref_install_cost_per_iunit = pd.Series(conv_ref_install_cost_per_iunit_nparray[:, 1],
            index=conv_ref_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_lifetime_capacity=182411.275767661, conv_avg_annual_use=4946.840187342,
            soln_lifetime_capacity=48343.8, soln_avg_annual_use=1841.66857142857,
            conv_var_oper_cost_per_funit=0.00375269040, conv_fuel_cost_per_funit=0.0731,
            conv_fixed_oper_cost_per_iunit=32.95140431108,
            soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
            soln_fixed_oper_cost_per_iunit=23.18791293579)
    oc = operatingcost.OperatingCost(ac=ac, soln_net_annual_funits_adopted=None,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit,
            conversion_factor=1.0)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    assert result[2016] == pytest.approx(130.616812789)
    result = oc.soln_only_single_iunit_cashflow()
    assert result[2041] == pytest.approx(32.654203197)


def test_conv_lifetime_zero():
    soln_pds_install_cost_per_iunit = pd.Series(soln_pds_install_cost_per_iunit_nparray[:, 1],
            index=soln_pds_install_cost_per_iunit_nparray[:, 0], dtype=np.float64)
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_lifetime_capacity=0.0, conv_avg_annual_use=1.0,
            soln_lifetime_capacity=70.0, soln_avg_annual_use=1.0,
            conv_fixed_oper_cost_per_iunit=3.0, soln_fixed_oper_cost_per_iunit=4.0)
    oc = operatingcost.OperatingCost(ac=ac, soln_net_annual_funits_adopted=None,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=None, conversion_factor=1.0)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    assert pd.isna(result.loc[2015:2060]).all()  # also tests that there is no DivideByZero error

    # Same test, using conv_expected_lifetime = 0.0 for LAND models.
    ac = advanced_controls.AdvancedControls(report_end_year=2050,
            conv_expected_lifetime=0.0, soln_expected_lifetime=70.0,
            conv_fixed_oper_cost_per_iunit=3.0, soln_fixed_oper_cost_per_iunit=4.0)
    oc = operatingcost.OperatingCost(ac=ac, soln_net_annual_funits_adopted=None,
            soln_pds_tot_iunits_reqd=None, soln_ref_tot_iunits_reqd=None,
            conv_ref_annual_tot_iunits=None, soln_pds_annual_world_first_cost=None,
            soln_ref_annual_world_first_cost=None, conv_ref_annual_world_first_cost=None,
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
            conv_ref_install_cost_per_iunit=None, conversion_factor=1.0)
    result = oc.soln_vs_conv_single_iunit_cashflow()
    assert pd.isna(result.loc[2015:2060]).all()  # also tests that there is no DivideByZero error



# SolarPVUtil 'Unit Adoption Calculations'!AX135:BH182
soln_pds_tot_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
        "Latin America", "China", "India", "EU", "USA"],
    [2014, 0.06115814489, 0.04072624506, 0.00018047945, 0.01144207203, 0.00085524497, 0.00795507895,
        0.00812970502, 0.00149228865, 0.03001194422, 0.00712649942],
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
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
        "Latin America", "China", "India", "EU", "USA"],
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

# SolarPVUtil 'Unit Adoption Calculations'!AX251:BH298
conv_ref_annual_tot_iunits_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 0.01196107466399, -0.01528781997629, -0.00006826207253, -0.00447949132584, -0.00034569359994,
     -0.00311656395124, -0.00311979718703, -0.00062062128398, -0.01127177963177, -0.00267161559500],
    [2016, 0.03042782609289, -0.01541358847829, -0.00006933310579, -0.00469919182633, -0.00037298641916,
     -0.00327151638198, -0.00321297098313, -0.00068567557833, -0.01137035528863, -0.00269009312551],
    [2017, 0.05202537780176, -0.01553935698030, -0.00007040413904, -0.00491889232683, -0.00040027923838,
     -0.00342646881272, -0.00330614477923, -0.00075072987268, -0.01146893094549, -0.00270857065602],
    [2018, 0.07661314589388, -0.01566512548230, -0.00007147517229, -0.00513859282733, -0.00042757205760,
     -0.00358142124346, -0.00339931857533, -0.00081578416702, -0.01156750660235, -0.00272704818653],
    [2019, 0.10405054647253, -0.01579089398430, -0.00007254620554, -0.00535829332783, -0.00045486487682,
     -0.00373637367420, -0.00349249237143, -0.00088083846137, -0.01166608225921, -0.00274552571704],
    [2020, 0.10405365237810, -0.01591666248630, -0.00007361723880, -0.00557799382833, -0.00048215769604,
     -0.00389132610494, -0.00358566616753, -0.00094589275571, -0.01176465791607, -0.00276400324755],
    [2021, 0.16691190950256, -0.01604243098831, -0.00007468827205, -0.00579769432883, -0.00050945051525,
     -0.00404627853568, -0.00367883996362, -0.00101094705006, -0.01186323357293, -0.00278248077806],
    [2022, 0.20205470416049, -0.01616819949031, -0.00007575930530, -0.00601739482933, -0.00053674333447,
     -0.00420123096642, -0.00377201375972, -0.00107600134440, -0.01196180922979, -0.00280095830857],
    [2023, 0.23948479571808, -0.01629396799231, -0.00007683033856, -0.00623709532983, -0.00056403615369,
     -0.00435618339716, -0.00386518755582, -0.00114105563875, -0.01206038488665, -0.00281943583908],
    [2024, 0.27906160027860, -0.01641973649432, -0.00007790137181, -0.00645679583032, -0.00059132897291,
     -0.00451113582790, -0.00395836135192, -0.00120610993309, -0.01215896054351, -0.00283791336958],
    [2025, 0.28987089139388, -0.01654550499632, -0.00007897240506, -0.00667649633082, -0.00061862179213,
     -0.00466608825864, -0.00405153514802, -0.00127116422744, -0.01225753620037, -0.00285639090009],
    [2026, 0.36409301282156, -0.01667127349832, -0.00008004343832, -0.00689619683132, -0.00064591461135,
     -0.00482104068938, -0.00414470894412, -0.00133621852178, -0.01235611185723, -0.00287486843060],
    [2027, 0.40926645301056, -0.01679704200032, -0.00008111447157, -0.00711589733182, -0.00067320743056,
     -0.00497599312012, -0.00423788274021, -0.00140127281613, -0.01245468751409, -0.00289334596111],
    [2028, 0.45602427061562, -0.01692281050233, -0.00008218550482, -0.00733559783232, -0.00070050024978,
     -0.00513094555086, -0.00433105653631, -0.00146632711047, -0.01255326317095, -0.00291182349162],
    [2029, 0.50422588174002, -0.01704857900433, -0.00008325653808, -0.00755529833282, -0.00072779306900,
     -0.00528589798160, -0.00442423033241, -0.00153138140482, -0.01265183882781, -0.00293030102213],
    [2030, 0.57745005942611, -0.01717434750633, -0.00008432757133, -0.00777499883332, -0.00075508588822,
     -0.00544085041233, -0.00451740412851, -0.00159643569916, -0.01275041448467, -0.00294877855264],
    [2031, 0.60439814895994, -0.01730011600834, -0.00008539860458, -0.00799469933382, -0.00078237870744,
     -0.00559580284307, -0.00461057792461, -0.00166148999351, -0.01284899014153, -0.00296725608315],
    [2032, 0.65608763726203, -0.01742588451034, -0.00008646963784, -0.00821439983432, -0.00080967152666,
     -0.00575075527381, -0.00470375172071, -0.00172654428785, -0.01294756579839, -0.00298573361366],
    [2033, 0.70865858349657, -0.01755165301234, -0.00008754067109, -0.00843410033481, -0.00083696434587,
     -0.00590570770455, -0.00479692551681, -0.00179159858220, -0.01304614145525, -0.00300421114417],
    [2034, 0.76197040376685, -0.01767742151434, -0.00008861170434, -0.00865380083531, -0.00086425716509,
     -0.00606066013529, -0.00489009931290, -0.00185665287654, -0.01314471711211, -0.00302268867468],
    [2035, 0.81588251417615, -0.01780319001635, -0.00008968273760, -0.00887350133581, -0.00089154998431,
     -0.00621561256603, -0.00498327310900, -0.00192170717089, -0.01324329276897, -0.00304116620518],
    [2036, 0.87025433082775, -0.01792895851835, -0.00009075377085, -0.00909320183631, -0.00091884280353,
     -0.00637056499677, -0.00507644690510, -0.00198676146523, -0.01334186842583, -0.00305964373569],
    [2037, 0.92494526982493, -0.01805472702035, -0.00009182480410, -0.00931290233681, -0.00094613562275,
     -0.00652551742751, -0.00516962070120, -0.00205181575958, -0.01344044408269, -0.00307812126620],
    [2038, 0.97981474727096, -0.01818049552236, -0.00009289583735, -0.00953260283731, -0.00097342844197,
     -0.00668046985825, -0.00526279449730, -0.00211687005392, -0.01353901973955, -0.00309659879671],
    [2039, 1.03472217926914, -0.01830626402436, -0.00009396687061, -0.00975230333781, -0.00100072126118,
     -0.00683542228899, -0.00535596829340, -0.00218192434827, -0.01363759539641, -0.00311507632722],
    [2040, 1.09911970574533, -0.01843203252636, -0.00009503790386, -0.00997200383831, -0.00102801408040,
     -0.00699037471973, -0.00544914208950, -0.00224697864261, -0.01373617105327, -0.00313355385773],
    [2041, 1.14408857133503, -0.01855780102836, -0.00009610893711, -0.01019170433881, -0.00105530689962,
     -0.00714532715047, -0.00554231588559, -0.00231203293696, -0.01383474671013, -0.00315203138824],
    [2042, 1.19826636360931, -0.01868356953037, -0.00009717997037, -0.01041140483930, -0.00108259971884,
     -0.00730027958121, -0.00563548968169, -0.00237708723130, -0.01393332236699, -0.00317050891875],
    [2043, 1.25191977484884, -0.01880933803237, -0.00009825100362, -0.01063110533980, -0.00110989253806,
     -0.00745523201195, -0.00572866347779, -0.00244214152565, -0.01403189802385, -0.00318898644926],
    [2044, 1.30490822115692, -0.01893510653437, -0.00009932203687, -0.01085080584030, -0.00113718535728,
     -0.00761018444269, -0.00582183727389, -0.00250719581999, -0.01413047368071, -0.00320746397977],
    [2045, 1.35709111863683, -0.01906087503638, -0.00010039307013, -0.01107050634080, -0.00116447817649,
     -0.00776513687343, -0.00591501106999, -0.00257225011434, -0.01422904933757, -0.00322594151028],
    [2046, 1.40832788339183, -0.01918664353838, -0.00010146410338, -0.01129020684130, -0.00119177099571,
     -0.00792008930417, -0.00600818486609, -0.00263730440868, -0.01432762499443, -0.00324441904079],
    [2047, 1.45847793152522, -0.01931241204038, -0.00010253513663, -0.01150990734180, -0.00121906381493,
     -0.00807504173491, -0.00610135866219, -0.00270235870303, -0.01442620065129, -0.00326289657129],
    [2048, 1.50740067914027, -0.01943818054238, -0.00010360616989, -0.01172960784230, -0.00124635663415,
     -0.00822999416565, -0.00619453245828, -0.00276741299737, -0.01452477630815, -0.00328137410180],
    [2049, 1.55495554234026, -0.01956394904439, -0.00010467720314, -0.01194930834280, -0.00127364945337,
     -0.00838494659639, -0.00628770625438, -0.00283246729172, -0.01462335196501, -0.00329985163231],
    [2050, 1.59604628469941, -0.01968971754639, -0.00010574823639, -0.01216900884329, -0.00130094227259,
     -0.00853989902713, -0.00638088005048, -0.00289752158606, -0.01472192762187, -0.00331832916282],
    [2051, 1.64539927990820, -0.01981548604839, -0.00010681926965, -0.01238870934379, -0.00132823509180,
     -0.00869485145787, -0.00647405384658, -0.00296257588041, -0.01482050327872, -0.00333680669333],
    [2052, 1.68800698648270, -0.01994125455040, -0.00010789030290, -0.01260840984429, -0.00135552791102,
     -0.00884980388861, -0.00656722764268, -0.00302763017475, -0.01491907893558, -0.00335528422384],
    [2053, 1.72868447305527, -0.02006702305240, -0.00010896133615, -0.01282811034479, -0.00138282073024,
     -0.00900475631935, -0.00666040143878, -0.00309268446910, -0.01501765459244, -0.00337376175435],
    [2054, 1.76729115572919, -0.02019279155440, -0.00011003236941, -0.01304781084529, -0.00141011354946,
     -0.00915970875009, -0.00675357523487, -0.00315773876344, -0.01511623024930, -0.00339223928486],
    [2055, 1.80368645060773, -0.02031856005640, -0.00011110340266, -0.01326751134579, -0.00143740636868,
     -0.00931466118083, -0.00684674903097, -0.00322279305779, -0.01521480590616, -0.00341071681537],
    [2056, 1.83772977379418, -0.02044432855841, -0.00011217443591, -0.01348721184629, -0.00146469918789,
     -0.00946961361157, -0.00693992282707, -0.00328784735213, -0.01531338156302, -0.00342919434588],
    [2057, 1.86928054139181, -0.02057009706041, -0.00011324546917, -0.01370691234679, -0.00149199200711,
     -0.00962456604231, -0.00703309662317, -0.00335290164648, -0.01541195721988, -0.00344767187639],
    [2058, 1.89819816950391, -0.02069586556241, -0.00011431650242, -0.01392661284729, -0.00151928482633,
     -0.00977951847305, -0.00712627041927, -0.00341795594082, -0.01551053287674, -0.00346614940690],
    [2059, 1.92434207423376, -0.02082163406442, -0.00011538753567, -0.01414631334778, -0.00154657764555,
     -0.00993447090379, -0.00721944421537, -0.00348301023517, -0.01560910853360, -0.00348462693740],
    [2060, 1.94757167168464, -0.02094740256642, -0.00011645856892, -0.01436601384828, -0.00157387046477,
     -0.01008942333453, -0.00731261801147, -0.00354806452951, -0.01570768419046, -0.00350310446791]]

# SolarPVUtil 'Operating Cost'!I531:I576
soln_pds_net_annual_iunits_reqd_list = [
    ['Year', 'World'],
    [2014, 0],
    [2015, 0.03212821555], [2016, 0.08173109715], [2017, 0.13974350959], [2018, 0.20578783548],
    [2019, 0.27948645744], [2020, 0.27949480010], [2021, 0.44833612002], [2022, 0.54273192587],
    [2023, 0.64327155825], [2024, 0.74957739977], [2025, 0.77861185065], [2026, 0.97797724069],
    [2027, 1.09931600533], [2028, 1.22491050957], [2029, 1.35438313602], [2030, 1.55106798502],
    [2031, 1.62345228605], [2032, 1.76229357485], [2033, 1.90350251632], [2034, 2.04670149309],
    [2035, 2.19151288776], [2036, 2.33755908296], [2037, 2.48446246130], [2038, 2.63184540538],
    [2039, 2.77933029784], [2040, 2.95230619419], [2041, 3.07309545830], [2042, 3.21862049155],
    [2043, 3.36273700362], [2044, 3.50506737714], [2045, 3.64523399471], [2046, 3.78285923895],
    [2047, 3.91756549248], [2048, 4.04897513792], [2049, 4.17671055787], [2050, 4.28708293365],
    [2051, 4.41964825178], [2052, 4.53409529097], [2053, 4.64335763514], [2054, 4.74705766690],
    [2055, 4.84481776887], [2056, 4.93626032366], [2057, 5.02100771389], [2058, 5.09868232217],
    [2059, 5.16890653112], [2060, 5.23130272335]]

# SolarPVUtil 'Operating Cost'!K531:K576
soln_pds_new_annual_iunits_reqd_list = [
    ['Year', 'World'],
    [2015, 0.03212821555], [2016, 0.04960288160], [2017, 0.05801241244], [2018, 0.06604432589],
    [2019, 0.07369862196], [2020, 0.00000834266], [2021, 0.16884131992], [2022, 0.09439580585],
    [2023, 0.10053963238], [2024, 0.10630584152], [2025, 0.02903445089], [2026, 0.19936539004],
    [2027, 0.12133876464], [2028, 0.12559450424], [2029, 0.12947262646], [2030, 0.19668484899],
    [2031, 0.07238430103], [2032, 0.13884128880], [2033, 0.14120894148], [2034, 0.14319897677],
    [2035, 0.14481139467], [2036, 0.14604619520], [2037, 0.14690337833], [2038, 0.14738294409],
    [2039, 0.14748489245], [2040, 0.17297589636], [2041, 0.12078926411], [2042, 0.14552503325],
    [2043, 0.14411651207], [2044, 0.14233037351], [2045, 0.14016661757], [2046, 0.13762524424],
    [2047, 0.13470625353], [2048, 0.13140964543], [2049, 0.12773541995], [2050, 0.11037237578],
    [2051, 0.13256531813], [2052, 0.11444703919], [2053, 0.10926234417], [2054, 0.10370003176],
    [2055, 0.09776010197], [2056, 0.09144255479], [2057, 0.08474739023], [2058, 0.07767460828],
    [2059, 0.07022420895], [2060, 0.06239619223]]

# SolarPVUtil 'Operating Cost'!F19:F64
soln_pds_new_funits_per_year_list = [
    ['Year', 'World'],
    [2015, 59.16952483163], [2016, 91.35206809813], [2017, 106.83963674163], [2018, 121.63175931515],

    [2019, 135.72843581868], [2020, 0.01536441848], [2021, 310.94975244954], [2022, 173.84578890937],

    [2023, 185.16068113296], [2024, 195.78012728656], [2025, 53.47183568578], [2026, 367.16497306821],

    [2027, 223.46578932746], [2028, 231.30345120112], [2029, 238.44566700479], [2030, 362.22830486262],

    [2031, 133.30789227804], [2032, 255.69963799590], [2033, 260.06006951964], [2034, 263.72505497338],

    [2035, 266.69459435714], [2036, 268.96868767092], [2037, 270.54733491470], [2038, 271.43053608851],

    [2039, 271.61829119232], [2040, 318.56427193785], [2041, 222.45379147831], [2042, 268.00888008386],

    [2043, 265.41485090774], [2044, 262.12537566162], [2045, 258.14045434553], [2046, 253.46008695944],

    [2047, 248.08427350337], [2048, 242.01301397732], [2049, 235.24630838128], [2050, 203.26933562993],

    [2051, 244.14138006456], [2052, 210.77351517324], [2053, 201.22502529726], [2054, 190.98108935129],

    [2055, 180.04170733533], [2056, 168.40687924939], [2057, 156.07660509346], [2058, 143.05088486755],

    [2059, 129.32971857165], [2060, 114.91310620577]]

# Computed by taking the difference A2-A1 over the range
# SolarPVUtil 'Unit Adoption Calculations'!AX252:BH298
# World column matches SolarPVUtil 'Operating Cost'!L531:L576.
conv_ref_new_annual_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2015, 0.011961074664, -0.015287819976, -0.000068262073, -0.004479491326, -0.000345693600, -0.003116563951,
     -0.003119797187, -0.000620621284, -0.011271779632, -0.002671615595],
    [2016, 0.018466751429, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2017, 0.021597551709, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2018, 0.024587768092, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2019, 0.027437400579, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2020, 0.000003105906, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2021, 0.062858257124, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2022, 0.035142794658, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2023, 0.037430091558, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2024, 0.039576804561, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2025, 0.010809291115, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2026, 0.074222121428, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2027, 0.045173440189, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2028, 0.046757817605, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2029, 0.048201611124, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2030, 0.073224177686, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2031, 0.026948089534, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2032, 0.051689488302, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2033, 0.052570946235, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2034, 0.053311820270, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2035, 0.053912110409, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2036, 0.054371816652, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2037, 0.054690938997, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2038, 0.054869477446, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2039, 0.054907431998, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2040, 0.064397526476, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2041, 0.044968865590, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2042, 0.054177792274, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2043, 0.053653411240, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2044, 0.052988446308, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2045, 0.052182897480, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2046, 0.051236764755, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2047, 0.050150048133, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2048, 0.048922747615, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2049, 0.047554863200, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2050, 0.041090742359, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2051, 0.049352995209, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2052, 0.042607706575, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2053, 0.040677486573, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2054, 0.038606682674, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2055, 0.036395294879, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2056, 0.034043323186, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2057, 0.031550767598, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2058, 0.028917628112, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2059, 0.026143904730, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531],
    [2060, 0.023229597451, -0.000125768502, -0.000001071033, -0.000219700500, -0.000027292819, -0.000154952431,
     -0.000093173796, -0.000065054294, -0.000098575657, -0.000018477531]]

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
    [2060, 113851352078.09], [2061, 426814950937.32], [2062, 404399835480.80],
    [2063, 381838361372.37], [2064, 359188607950.38], [2065, 336508654553.14],
    [2066, 310884303472.73], [2067, 287828970480.61], [2068, 260112337712.87],
    [2069, 229616507406.10], [2070, 198116487900.99], [2071, 165728437874.21],
    [2072, 138795066384.77], [2073, 104979431344.61], [2074, 64397691430.40],
    [2075, 29619106083.51], [2076, 4243948246.16],
    [2077, 0.0], [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0],
    [2083, 0.0], [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0],
    [2089, 0.0], [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0],
    [2095, 0.0], [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0],
    [2101, 0.0], [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0],
    [2107, 0.0], [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0],
    [2113, 0.0], [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0],
    [2119, 0.0], [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0],
    [2125, 0.0], [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0],
    [2131, 0.0], [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0],
    [2137, 0.0], [2138, 0.0], [2139, 0.0]])

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

# SolarPVUtil "Operating Cost"!D19:D64
soln_pds_annual_operating_cost_nparray = np.array([
    [2015, 744986264.92], [2016, 1895173564.86], [2017, 3240360333.69],
    [2018, 4771790412.36], [2019, 6480707641.83], [2020, 6480901090.75],
    [2021, 10395978916.95], [2022, 12584820644.51], [2023, 14916124886.68],
    [2024, 17381135484.41], [2025, 18054383803.70], [2026, 22677251110.37],
    [2027, 25490843820.50], [2028, 28403118250.01], [2029, 31405318239.85],
    [2030, 35966029394.04], [2031, 37644470264.32], [2032, 40863909980.86],
    [2033, 44138250621.54], [2034, 47458736027.32], [2035, 50816610039.15],
    [2036, 54203116497.98], [2037, 57609499244.77], [2038, 61027002120.46],
    [2039, 64446868966.02], [2040, 68457818990.77], [2041, 71258669930.54],
    [2042, 74633091731.41], [2043, 77974852865.96], [2044, 81275197175.13],
    [2045, 84525368499.90], [2046, 87716610681.19], [2047, 90840167559.98],
    [2048, 93887282977.22], [2049, 96849200773.85], [2050, 97559747865.68],
    [2051, 96438558976.78], [2052, 92803096416.96], [2053, 89537185057.69],
    [2054, 86649581058.02], [2055, 83669862458.27], [2056, 79498779095.17],
    [2057, 77099770653.91], [2058, 74265580648.94], [2059, 71004965239.29],
    [2060, 67696016024.78], [2061, 64347489164.47], [2062, 60968140817.39],
    [2063, 57566727142.59], [2064, 54152004299.12], [2065, 50732728446.03],
    [2066, 46869549216.08], [2067, 43393680372.60], [2068, 39215064504.57],
    [2069, 34617451169.06], [2070, 29868444229.79], [2071, 24985556004.86],
    [2072, 20925026198.50], [2073, 15826912356.53], [2074, 9708726797.02],
    [2075, 4465436610.37], [2076, 639826260.03],
    [2077, 0.0], [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0],
    [2083, 0.0], [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0],
    [2089, 0.0], [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0],
    [2095, 0.0], [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0],
    [2101, 0.0], [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0],
    [2107, 0.0], [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0],
    [2113, 0.0], [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0],
    [2119, 0.0], [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0],
    [2125, 0.0], [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0],
    [2131, 0.0], [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0],
    [2137, 0.0], [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!E19:E64
soln_pds_cumulative_operating_cost_nparray = np.array([
    [2015, 744986264.92], [2016, 2640159829.78], [2017, 5880520163.48],
    [2018, 10652310575.84], [2019, 17133018217.67], [2020, 23613919308.42],
    [2021, 34009898225.37], [2022, 46594718869.88], [2023, 61510843756.56],
    [2024, 78891979240.97], [2025, 96946363044.67], [2026, 119623614155.04],
    [2027, 145114457975.54], [2028, 173517576225.55], [2029, 204922894465.40],
    [2030, 240888923859.44], [2031, 278533394123.76], [2032, 319397304104.61],
    [2033, 363535554726.16], [2034, 410994290753.48], [2035, 461810900792.63],
    [2036, 516014017290.61], [2037, 573623516535.37], [2038, 634650518655.84],
    [2039, 699097387621.86], [2040, 767555206612.63], [2041, 838813876543.17],
    [2042, 913446968274.58], [2043, 991421821140.54], [2044, 1072697018315.67],
    [2045, 1157222386815.57], [2046, 1244938997496.76], [2047, 1335779165056.74],
    [2048, 1429666448033.96], [2049, 1526515648807.81], [2050, 1624075396673.49],
    [2051, 1720513955650.27], [2052, 1813317052067.23], [2053, 1902854237124.91],
    [2054, 1989503818182.94], [2055, 2073173680641.21], [2056, 2152672459736.38],
    [2057, 2229772230390.29], [2058, 2304037811039.22], [2059, 2375042776278.51],
    [2060, 2442738792303.29], [2061, 2507086281467.76], [2062, 2568054422285.15],
    [2063, 2625621149427.73], [2064, 2679773153726.86], [2065, 2730505882172.88],
    [2066, 2777375431388.96], [2067, 2820769111761.57], [2068, 2859984176266.13],
    [2069, 2894601627435.19], [2070, 2924470071664.98], [2071, 2949455627669.84],
    [2072, 2970380653868.34], [2073, 2986207566224.87], [2074, 2995916293021.89],
    [2075, 3000381729632.26], [2076, 3001021555892.29],
    [2077, 3001021555892.30], [2078, 3001021555892.30],
    [2079, 3001021555892.30], [2080, 3001021555892.30],
    [2081, 3001021555892.30], [2082, 3001021555892.30],
    [2083, 3001021555892.30], [2084, 3001021555892.30],
    [2085, 3001021555892.30], [2086, 3001021555892.30],
    [2087, 3001021555892.30], [2088, 3001021555892.30],
    [2089, 3001021555892.30], [2090, 3001021555892.30],
    [2091, 3001021555892.30], [2092, 3001021555892.30],
    [2093, 3001021555892.30], [2094, 3001021555892.30],
    [2095, 3001021555892.30], [2096, 3001021555892.30],
    [2097, 3001021555892.30], [2098, 3001021555892.30],
    [2099, 3001021555892.30], [2100, 3001021555892.30],
    [2101, 3001021555892.30], [2102, 3001021555892.30],
    [2103, 3001021555892.30], [2104, 3001021555892.30],
    [2105, 3001021555892.30], [2106, 3001021555892.30],
    [2107, 3001021555892.30], [2108, 3001021555892.30],
    [2109, 3001021555892.30], [2110, 3001021555892.30],
    [2111, 3001021555892.30], [2112, 3001021555892.30],
    [2113, 3001021555892.30], [2114, 3001021555892.30],
    [2115, 3001021555892.30], [2116, 3001021555892.30],
    [2117, 3001021555892.30], [2118, 3001021555892.30],
    [2119, 3001021555892.30], [2120, 3001021555892.30],
    [2121, 3001021555892.30], [2122, 3001021555892.30],
    [2123, 3001021555892.30], [2124, 3001021555892.30],
    [2125, 3001021555892.30], [2126, 3001021555892.30],
    [2127, 3001021555892.30], [2128, 3001021555892.30],
    [2129, 3001021555892.30], [2130, 3001021555892.30],
    [2131, 3001021555892.30], [2132, 3001021555892.30],
    [2133, 3001021555892.30], [2134, 3001021555892.30],
    [2135, 3001021555892.30], [2136, 3001021555892.30],
    [2137, 3001021555892.30], [2138, 3001021555892.30],
    [2139, 3001021555892.30]
])

# SolarPVUtil "Operating Cost"!K19:K64
conv_ref_annual_operating_cost_nparray = np.array([
    [2015, 4941471380.46], [2016, 12570628980.37], [2017, 21493212164.19],
    [2018, 31651141593.59], [2019, 42986337930.23], [2020, 42987621071.08],
    [2021, 68956213971.94], [2022, 83474735000.35], [2023, 98938205582.69],
    [2024, 115288546380.62], [2025, 119754182135.75], [2026, 150417521269.98],
    [2027, 169079996684.73], [2028, 188397024961.77], [2029, 208310526762.77],
    [2030, 238561586016.06], [2031, 249694633583.29], [2032, 271049079926.16],
    [2033, 292767682439.67], [2034, 314792361785.49], [2035, 337065038625.28],
    [2036, 359527633620.71], [2037, 382122067433.47], [2038, 404790260725.21],
    [2039, 427474134157.61], [2040, 454078644454.03], [2041, 472656604091.06],
    [2042, 495039041915.46], [2043, 517204842527.20], [2044, 539095926587.95],
    [2045, 560654214759.38], [2046, 581821627703.17], [2047, 602540086080.97],
    [2048, 622751510554.47], [2049, 642397821785.34], [2050, 647110859171.51],
    [2051, 639674047155.68], [2052, 615560133866.23], [2053, 593897442521.60],
    [2054, 574744052460.14], [2055, 554979669040.13], [2056, 527312999149.92],
    [2057, 511400448661.17], [2058, 492601352012.20], [2059, 470973788541.35],
    [2060, 449025628403.62]])

# SolarPVUtil "Operating Cost"!E19:E64
conv_ref_cumulative_operating_cost_nparray = np.array([
    [2015, 4941471380.46], [2016, 17512100360.83], [2017, 39005312525.03],
    [2018, 70656454118.62], [2019, 113642792048.85], [2020, 156630413119.94],
    [2021, 225586627091.88], [2022, 309061362092.23], [2023, 407999567674.92],
    [2024, 523288114055.54], [2025, 643042296191.29], [2026, 793459817461.26],
    [2027, 962539814145.99], [2028, 1150936839107.77], [2029, 1359247365870.53],
    [2030, 1597808951886.59], [2031, 1847503585469.88], [2032, 2118552665396.04],
    [2033, 2411320347835.71], [2034, 2726112709621.20], [2035, 3063177748246.47],
    [2036, 3422705381867.18], [2037, 3804827449300.65], [2038, 4209617710025.86],
    [2039, 4637091844183.46], [2040, 5091170488637.49], [2041, 5563827092728.55],
    [2042, 6058866134644.01], [2043, 6576070977171.21], [2044, 7115166903759.16],
    [2045, 7675821118518.54], [2046, 8257642746221.71], [2047, 8860182832302.68],
    [2048, 9482934342857.16], [2049, 10125332164642.50], [2050, 10772443023814.00],
    [2051, 11412117070969.70], [2052, 12027677204835.90], [2053, 12621574647357.50],
    [2054, 13196318699817.70], [2055, 13751298368857.80], [2056, 14278611368007.70],
    [2057, 14790011816668.90], [2058, 15282613168681.10], [2059, 15753586957222.40],
    [2060, 16202612585626.00]])

# SolarPVUtil "Operating Cost"!D69:D114
marginal_annual_operating_cost_nparray = np.array([
    [2015, 4196485115.54], [2016, 10675455415.51], [2017, 18252851830.50],
    [2018, 26879351181.23], [2019, 36505630288.41], [2020, 36506719980.33],
    [2021, 58560235055.00], [2022, 70889914355.84], [2023, 84022080696.01],
    [2024, 97907410896.21], [2025, 101699798332.05], [2026, 127740270159.61],
    [2027, 143589152864.23], [2028, 159993906711.76], [2029, 176905208522.92],
    [2030, 202595556622.02], [2031, 212050163318.97], [2032, 230185169945.30],
    [2033, 248629431818.13], [2034, 267333625758.16], [2035, 286248428586.13],
    [2036, 305324517122.73], [2037, 324512568188.70], [2038, 343763258604.75],
    [2039, 363027265191.59], [2040, 385620825463.26], [2041, 401397934160.52],
    [2042, 420405950184.05], [2043, 439229989661.24], [2044, 457820729412.82],
    [2045, 476128846259.49], [2046, 494105017021.97], [2047, 511699918520.99],
    [2048, 528864227577.26], [2049, 545548621011.49], [2050, 549551111305.83],
    [2051, 543235488178.90], [2052, 522757037449.27], [2053, 504360257463.92],
    [2054, 488094471402.11], [2055, 471309806581.86], [2056, 447814220054.75],
    [2057, 434300678007.26], [2058, 418335771363.27], [2059, 399968823302.07],
    [2060, 381329612378.83]])

# SolarPVUtil "Operating Cost"!B19:B64
soln_marginal_first_cost_nparray = np.array([
    [2015, -22432407009.64], [2016, -25103540446.96], [2017, -21709643060.00],
    [2018, -18256235647.59], [2019, -14754936171.86], [2020, 991539625.99],
    [2021, -15963799121.32], [2022, -4237893109.54], [2023, -812299303.65],
    [2024, 2539250353.69], [2025, 1943570621.51], [2026, 14248289863.97],
    [2027, 12002921852.21], [2028, 14922133995.01], [2029, 17708581650.51],
    [2030, 30812206896.05], [2031, 12904677243.36], [2032, 25204610762.49],
    [2033, 27397666857.60], [2034, 29430757586.21], [2035, 31300455525.94],
    [2036, 33003810257.21], [2037, 34538293305.07], [2038, 35901752528.66],
    [2039, 37092374291.88], [2040, 44715046624.56], [2041, 32392123175.17],
    [2042, 26122281172.29], [2043, 18684881335.09], [2044, 15424572287.54],
    [2045, 12230933599.22], [2046, 9090220293.95], [2047, 41907133633.22],
    [2048, -32631409259.37], [2049, -129569945.21], [2050, -7226584060.81],
    [2051, 0.0], [2052, 0.0], [2053, 0.0],
    [2054, 0.0], [2055, 0.0], [2056, 0.0], [2057, 0.0], [2058, 0.0], [2059, 0.0],
    [2060, 0.0], [2061, 0.0], [2062, 0.0], [2063, 0.0], [2064, 0.0], [2065, 0.0],
    [2066, 0.0], [2067, 0.0], [2068, 0.0], [2069, 0.0], [2070, 0.0], [2071, 0.0],
    [2072, 0.0], [2073, 0.0], [2074, 0.0], [2075, 0.0], [2076, 0.0], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!C19:C64
soln_marginal_operating_cost_savings_nparray = np.array([
    [2015, 4196485115.54], [2016, 10675455415.51], [2017, 18252851830.50],
    [2018, 26879351181.23], [2019, 36505630288.41], [2020, 36506719980.33],
    [2021, 58560235055.00], [2022, 70889914355.84], [2023, 84022080696.01],
    [2024, 97907410896.21], [2025, 101699798332.05], [2026, 127740270159.61],
    [2027, 143589152864.23], [2028, 159993906711.76], [2029, 176905208522.92],
    [2030, 202595556622.02], [2031, 212050163318.97], [2032, 230185169945.30],
    [2033, 248629431818.13], [2034, 267333625758.16], [2035, 286248428586.13],
    [2036, 305324517122.73], [2037, 324512568188.70], [2038, 343763258604.75],
    [2039, 363027265191.59], [2040, 385620825463.26], [2041, 401397934160.52],
    [2042, 420405950184.05], [2043, 439229989661.24], [2044, 457820729412.82],
    [2045, 476128846259.49], [2046, 494105017021.97], [2047, 511699918520.99],
    [2048, 528864227577.26], [2049, 545548621011.49], [2050, 549551111305.83],
    [2051, 543235488178.90], [2052, 522757037449.27], [2053, 504360257463.92],
    [2054, 488094471402.11], [2055, 471309806581.86], [2056, 447814220054.75],
    [2057, 434300678007.26], [2058, 418335771363.27], [2059, 399968823302.07],
    [2060, 381329612378.83], [2061, 362467461772.85], [2062, 343431694663.41],
    [2063, 324271634229.78], [2064, 305036603651.26], [2065, 285775926107.11],
    [2066, 264014754256.65], [2067, 244435290108.02], [2068, 220897273208.30],
    [2069, 194999056237.04], [2070, 168248043671.20], [2071, 140742881869.35],
    [2072, 117870040186.27], [2073, 89152518988.09], [2074, 54688964633.38],
    [2075, 25153669473.13], [2076, 3604121986.12], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!D19:D64
soln_net_cash_flow_nparray = np.array([
    [2015, -18235921894.10], [2016, -14428085031.45], [2017, -3456791229.50],
    [2018, 8623115533.63], [2019, 21750694116.54], [2020, 37498259606.32],
    [2021, 42596435933.68], [2022, 66652021246.30], [2023, 83209781392.35],
    [2024, 100446661249.90], [2025, 103643368953.56], [2026, 141988560023.58],
    [2027, 155592074716.44], [2028, 174916040706.77], [2029, 194613790173.42],
    [2030, 233407763518.07], [2031, 224954840562.34], [2032, 255389780707.79],
    [2033, 276027098675.73], [2034, 296764383344.37], [2035, 317548884112.07],
    [2036, 338328327379.94], [2037, 359050861493.77], [2038, 379665011133.40],
    [2039, 400119639483.47], [2040, 430335872087.82], [2041, 433790057335.69],
    [2042, 446528231356.34], [2043, 457914870996.33], [2044, 473245301700.35],
    [2045, 488359779858.71], [2046, 503195237315.93], [2047, 553607052154.21],
    [2048, 496232818317.89], [2049, 545419051066.28], [2050, 542324527245.02],
    [2051, 543235488178.90], [2052, 522757037449.27], [2053, 504360257463.92],
    [2054, 488094471402.11], [2055, 471309806581.86], [2056, 447814220054.75],
    [2057, 434300678007.26], [2058, 418335771363.27], [2059, 399968823302.07],
    [2060, 381329612378.83], [2061, 362467461772.85], [2062, 343431694663.41],
    [2063, 324271634229.78], [2064, 305036603651.26], [2065, 285775926107.11],
    [2066, 264014754256.65], [2067, 244435290108.02], [2068, 220897273208.30],
    [2069, 194999056237.04], [2070, 168248043671.20], [2071, 140742881869.35],
    [2072, 117870040186.27], [2073, 89152518988.09], [2074, 54688964633.38],
    [2075, 25153669473.13], [2076, 3604121986.12], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!A19:E64
soln_net_present_value_nparray = np.array([
    [2015, -16669032809.96], [2016, -12055189709.74], [2017, -2640104913.84],
    [2018, 6019978176.76], [2019, 13879905551.81], [2020, 21872940897.27],
    [2021, 22711823734.61], [2022, 32484392409.82], [2023, 37069649785.36],
    [2024, 40903670928.75], [2025, 38579001176.59], [2026, 48310940342.91],
    [2027, 48390742499.23], [2028, 49726412740.70], [2029, 50572425210.92],
    [2030, 55441905125.08], [2031, 48842835547.56], [2032, 50686431824.69],
    [2033, 50075189632.25], [2034, 49211356591.25], [2035, 48133432026.13],
    [2036, 46876726648.57], [2037, 45473414656.54], [2038, 43952628031.55],
    [2039, 42340581560.58], [2040, 41625280943.60], [2041, 38354109131.00],
    [2042, 36088090737.59], [2043, 33828474195.33], [2044, 31957047716.80],
    [2045, 30144140641.27], [2046, 28391099908.67], [2047, 28551569574.97],
    [2048, 23393571733.32], [2049, 23503039665.57], [2050, 21361692268.72],
    [2051, 19559025803.46], [2052, 17204484018.39], [2053, 15172784859.71],
    [2054, 13421807587.99], [2055, 11846669547.52], [2056, 10288933406.16],
    [2057, 9121067326.91], [2058, 8030874409.34], [2059, 7018537916.45],
    [2060, 6116510422.41], [2061, 5314407994.35], [2062, 4602660237.54],
    [2063, 3972465941.46], [2064, 3415748268.73], [2065, 2925110110.54],
    [2066, 2470173474.91], [2067, 2090479153.53], [2068, 1726851400.09],
    [2069, 1393412812.57], [2070, 1098955207.36], [2071, 840309136.58],
    [2072, 643278084.27], [2073, 444745559.63], [2074, 249379288.53],
    [2075, 104844271.89], [2076, 13731738.30], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

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

# SolarPVUtil "Operating Cost"!I126:I250
soln_vs_conv_single_iunit_cashflow_nparray = np.array([
    [2015, -469994891712], [2016, 130616812789], [2017, 130616812789],
    [2018, 130616812789], [2019, 130616812789], [2020, 130616812789],
    [2021, 130616812789], [2022, 130616812789], [2023, 130616812789],
    [2024, 130616812789], [2025, 130616812789], [2026, 130616812789],
    [2027, 130616812789], [2028, 130616812789], [2029, 130616812789],
    [2030, 130616812789], [2031, 130616812789], [2032, 130616812789],
    [2033, 130616812789], [2034, 130616812789], [2035, 130616812789],
    [2036, 130616812789], [2037, 130616812789], [2038, 130616812789],
    [2039, 130616812789], [2040, 130616812789], [2041, 32654203197],
    [2042, 0], [2043, 0], [2044, 0], [2045, 0], [2046, 0], [2047, 0], [2048, 0],
    [2049, 0], [2050, 0], [2051, 0], [2052, 0], [2053, 0], [2054, 0], [2055, 0],
    [2056, 0], [2057, 0], [2058, 0], [2059, 0], [2060, 0], [2061, 0], [2062, 0],
    [2063, 0], [2064, 0], [2065, 0], [2066, 0], [2067, 0], [2068, 0], [2069, 0],
    [2070, 0], [2071, 0], [2072, 0], [2073, 0], [2074, 0], [2075, 0], [2076, 0],
    [2077, 0], [2078, 0], [2079, 0], [2080, 0], [2081, 0], [2082, 0], [2083, 0],
    [2084, 0], [2085, 0], [2086, 0], [2087, 0], [2088, 0], [2089, 0], [2090, 0],
    [2091, 0], [2092, 0], [2093, 0], [2094, 0], [2095, 0], [2096, 0], [2097, 0],
    [2098, 0], [2099, 0], [2100, 0], [2101, 0], [2102, 0], [2103, 0], [2104, 0],
    [2105, 0], [2106, 0], [2107, 0], [2108, 0], [2109, 0], [2110, 0], [2111, 0],
    [2112, 0], [2113, 0], [2114, 0], [2115, 0], [2116, 0], [2117, 0], [2118, 0],
    [2119, 0], [2120, 0], [2121, 0], [2122, 0], [2123, 0], [2124, 0], [2125, 0],
    [2126, 0], [2127, 0], [2128, 0], [2129, 0], [2130, 0], [2131, 0], [2132, 0],
    [2133, 0], [2134, 0], [2135, 0], [2136, 0], [2137, 0], [2138, 0], [2139, 0]])

# SolarPVUtil "Operating Cost"!J126:J250
soln_vs_conv_single_iunit_npv_nparray = np.array([
    [2015, -358955962541.30], [2016, 91186342041.03], [2017, 83351318136.23],
    [2018, 76189504694.91], [2019, 69643057307.96], [2020, 63659101744.02],
    [2021, 58189306895.81], [2022, 53189494420.31], [2023, 48619281919.84],
    [2024, 44441756782.30], [2025, 40623178045.98], [2026, 37132703881.15],
    [2027, 33942142487.34], [2028, 31025724394.28], [2029, 28359894327.50],
    [2030, 25923120957.49], [2031, 23695722995.88], [2032, 21659710233.89],
    [2033, 19798638239.39], [2034, 18097475538.75], [2035, 16542482210.92],
    [2036, 15121098913.09], [2037, 13821845441.58], [2038, 12634228008.76],
    [2039, 11548654486.98], [2040, 10556356935.08], [2041, 2412330195.40],
    [2042, 0.0], [2043, 0.0], [2044, 0.0], [2045, 0.0], [2046, 0.0], [2047, 0.0],
    [2048, 0.0], [2049, 0.0], [2050, 0.0], [2051, 0.0], [2052, 0.0], [2053, 0.0],
    [2054, 0.0], [2055, 0.0], [2056, 0.0], [2057, 0.0], [2058, 0.0], [2059, 0.0],
    [2060, 0.0], [2061, 0.0], [2062, 0.0], [2063, 0.0], [2064, 0.0], [2065, 0.0],
    [2066, 0.0], [2067, 0.0], [2068, 0.0], [2069, 0.0], [2070, 0.0], [2071, 0.0],
    [2072, 0.0], [2073, 0.0], [2074, 0.0], [2075, 0.0], [2076, 0.0], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!J126:J250 with purchase_year=2026, discount_rate=7.1, but
# holding I126:I250 unchanged
soln_vs_conv_single_iunit_npv_purchase_year_discount_rate_nparray = np.array([
    [2015, -30176388296.25], [2016, 57348944906.19], [2017, 53547100752.74],
    [2018, 49997292953.08], [2019, 46682813214.82], [2020, 43588060891.52],
    [2021, 40698469553.24], [2022, 38000438425.06], [2023, 35481268370.74],
    [2024, 33129102120.21], [2025, 30932868459.58], [2026, 28882230120.99],
    [2027, 26967535126.97], [2028, 25179771360.38], [2029, 23510524146.02],
    [2030, 21951936644.27], [2031, 20496672870.47], [2032, 19137883165.71],
    [2033, 17869171956.77], [2034, 16684567653.38], [2035, 15578494540.98],
    [2036, 14545746536.86], [2037, 13581462686.14], [2038, 12681104282.11],
    [2039, 11840433503.37], [2040, 11055493467.20], [2041, 2580647401.31],
    [2042, 0.0], [2043, 0.0], [2044, 0.0], [2045, 0.0], [2046, 0.0], [2047, 0.0],
    [2048, 0.0], [2049, 0.0], [2050, 0.0], [2051, 0.0], [2052, 0.0], [2053, 0.0],
    [2054, 0.0], [2055, 0.0], [2056, 0.0], [2057, 0.0], [2058, 0.0], [2059, 0.0],
    [2060, 0.0], [2061, 0.0], [2062, 0.0], [2063, 0.0], [2064, 0.0], [2065, 0.0],
    [2066, 0.0], [2067, 0.0], [2068, 0.0], [2069, 0.0], [2070, 0.0], [2071, 0.0],
    [2072, 0.0], [2073, 0.0], [2074, 0.0], [2075, 0.0], [2076, 0.0], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!K126:K250
soln_vs_conv_single_iunit_payback_nparray = np.array([
    [2015, 0], [2016, 0], [2017, 0], [2018, 0], [2019, 1], [2020, 1], [2021, 1],
    [2022, 1], [2023, 1], [2024, 1], [2025, 1], [2026, 1], [2027, 1], [2028, 1],
    [2029, 1], [2030, 1], [2031, 1], [2032, 1], [2033, 1], [2034, 1], [2035, 1],
    [2036, 1], [2037, 1], [2038, 1], [2039, 1], [2040, 1], [2041, 1], [2042, 1],
    [2043, 1], [2044, 1], [2045, 1], [2046, 1], [2047, 1], [2048, 1], [2049, 1],
    [2050, 1], [2051, 1], [2052, 1], [2053, 1], [2054, 1], [2055, 1], [2056, 1],
    [2057, 1], [2058, 1], [2059, 1], [2060, 1], [2061, 1], [2062, 1], [2063, 1],
    [2064, 1], [2065, 1], [2066, 1], [2067, 1], [2068, 1], [2069, 1], [2070, 1],
    [2071, 1], [2072, 1], [2073, 1], [2074, 1], [2075, 1], [2076, 1], [2077, 1],
    [2078, 1], [2079, 1], [2080, 1], [2081, 1], [2082, 1], [2083, 1], [2084, 1],
    [2085, 1], [2086, 1], [2087, 1], [2088, 1], [2089, 1], [2090, 1], [2091, 1],
    [2092, 1], [2093, 1], [2094, 1], [2095, 1], [2096, 1], [2097, 1], [2098, 1],
    [2099, 1], [2100, 1], [2101, 1], [2102, 1], [2103, 1], [2104, 1], [2105, 1],
    [2106, 1], [2107, 1], [2108, 1], [2109, 1], [2110, 1], [2111, 1], [2112, 1],
    [2113, 1], [2114, 1], [2115, 1], [2116, 1], [2117, 1], [2118, 1], [2119, 1],
    [2120, 1], [2121, 1], [2122, 1], [2123, 1], [2124, 1], [2125, 1], [2126, 1],
    [2127, 1], [2128, 1], [2129, 1], [2130, 1], [2131, 1], [2132, 1], [2133, 1],
    [2134, 1], [2135, 1], [2136, 1], [2137, 1], [2138, 1], [2139, 1]])

# SolarPVUtil "Operating Cost"!L126:L250
soln_vs_conv_single_iunit_payback_discounted_nparray = np.array([
    [2015, 0], [2016, 0], [2017, 0], [2018, 0], [2019, 0], [2020, 1], [2021, 1],
    [2022, 1], [2023, 1], [2024, 1], [2025, 1], [2026, 1], [2027, 1], [2028, 1],
    [2029, 1], [2030, 1], [2031, 1], [2032, 1], [2033, 1], [2034, 1], [2035, 1],
    [2036, 1], [2037, 1], [2038, 1], [2039, 1], [2040, 1], [2041, 1], [2042, 1],
    [2043, 1], [2044, 1], [2045, 1], [2046, 1], [2047, 1], [2048, 1], [2049, 1],
    [2050, 1], [2051, 1], [2052, 1], [2053, 1], [2054, 1], [2055, 1], [2056, 1],
    [2057, 1], [2058, 1], [2059, 1], [2060, 1], [2061, 1], [2062, 1], [2063, 1],
    [2064, 1], [2065, 1], [2066, 1], [2067, 1], [2068, 1], [2069, 1], [2070, 1],
    [2071, 1], [2072, 1], [2073, 1], [2074, 1], [2075, 1], [2076, 1], [2077, 1],
    [2078, 1], [2079, 1], [2080, 1], [2081, 1], [2082, 1], [2083, 1], [2084, 1],
    [2085, 1], [2086, 1], [2087, 1], [2088, 1], [2089, 1], [2090, 1], [2091, 1],
    [2092, 1], [2093, 1], [2094, 1], [2095, 1], [2096, 1], [2097, 1], [2098, 1],
    [2099, 1], [2100, 1], [2101, 1], [2102, 1], [2103, 1], [2104, 1], [2105, 1],
    [2106, 1], [2107, 1], [2108, 1], [2109, 1], [2110, 1], [2111, 1], [2112, 1],
    [2113, 1], [2114, 1], [2115, 1], [2116, 1], [2117, 1], [2118, 1], [2119, 1],
    [2120, 1], [2121, 1], [2122, 1], [2123, 1], [2124, 1], [2125, 1], [2126, 1],
    [2127, 1], [2128, 1], [2129, 1], [2130, 1], [2131, 1], [2132, 1], [2133, 1],
    [2134, 1], [2135, 1], [2136, 1], [2137, 1], [2138, 1], [2139, 1]])

# SolarPVUtil "Operating Cost"!M126:M250
soln_only_single_iunit_cashflow_nparray = np.array([
    [2015, -1000508958473], [2016, 130616812789], [2017, 130616812789], [2018, 130616812789],
    [2019, 130616812789], [2020, 130616812789], [2021, 130616812789], [2022, 130616812789],
    [2023, 130616812789], [2024, 130616812789], [2025, 130616812789], [2026, 130616812789],
    [2027, 130616812789], [2028, 130616812789], [2029, 130616812789], [2030, 130616812789],
    [2031, 130616812789], [2032, 130616812789], [2033, 130616812789], [2034, 130616812789],
    [2035, 130616812789], [2036, 130616812789], [2037, 130616812789], [2038, 130616812789],
    [2039, 130616812789], [2040, 130616812789], [2041, 32654203197],
    [2042, 0.0], [2043, 0.0], [2044, 0.0], [2045, 0.0], [2046, 0.0], [2047, 0.0],
    [2048, 0.0], [2049, 0.0], [2050, 0.0], [2051, 0.0], [2052, 0.0], [2053, 0.0],
    [2054, 0.0], [2055, 0.0], [2056, 0.0], [2057, 0.0], [2058, 0.0], [2059, 0.0],
    [2060, 0.0], [2061, 0.0], [2062, 0.0], [2063, 0.0], [2064, 0.0], [2065, 0.0],
    [2066, 0.0], [2067, 0.0], [2068, 0.0], [2069, 0.0], [2070, 0.0], [2071, 0.0],
    [2072, 0.0], [2073, 0.0], [2074, 0.0], [2075, 0.0], [2076, 0.0], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!N126:N250
soln_only_single_iunit_npv_nparray = np.array([
    [2015, -764133105599], [2016, 91186342041], [2017, 83351318136], [2018, 76189504695],
    [2019, 69643057308], [2020, 63659101744], [2021, 58189306896], [2022, 53189494420],
    [2023, 48619281920], [2024, 44441756782], [2025, 40623178046], [2026, 37132703881],
    [2027, 33942142487], [2028, 31025724394], [2029, 28359894327], [2030, 25923120957],
    [2031, 23695722996], [2032, 21659710234], [2033, 19798638239], [2034, 18097475539],
    [2035, 16542482211], [2036, 15121098913], [2037, 13821845442], [2038, 12634228009],
    [2039, 11548654487], [2040, 10556356935], [2041, 2412330195],
    [2042, 0.0], [2043, 0.0], [2044, 0.0], [2045, 0.0], [2046, 0.0], [2047, 0.0],
    [2048, 0.0], [2049, 0.0], [2050, 0.0], [2051, 0.0], [2052, 0.0], [2053, 0.0],
    [2054, 0.0], [2055, 0.0], [2056, 0.0], [2057, 0.0], [2058, 0.0], [2059, 0.0],
    [2060, 0.0], [2061, 0.0], [2062, 0.0], [2063, 0.0], [2064, 0.0], [2065, 0.0],
    [2066, 0.0], [2067, 0.0], [2068, 0.0], [2069, 0.0], [2070, 0.0], [2071, 0.0],
    [2072, 0.0], [2073, 0.0], [2074, 0.0], [2075, 0.0], [2076, 0.0], [2077, 0.0],
    [2078, 0.0], [2079, 0.0], [2080, 0.0], [2081, 0.0], [2082, 0.0], [2083, 0.0],
    [2084, 0.0], [2085, 0.0], [2086, 0.0], [2087, 0.0], [2088, 0.0], [2089, 0.0],
    [2090, 0.0], [2091, 0.0], [2092, 0.0], [2093, 0.0], [2094, 0.0], [2095, 0.0],
    [2096, 0.0], [2097, 0.0], [2098, 0.0], [2099, 0.0], [2100, 0.0], [2101, 0.0],
    [2102, 0.0], [2103, 0.0], [2104, 0.0], [2105, 0.0], [2106, 0.0], [2107, 0.0],
    [2108, 0.0], [2109, 0.0], [2110, 0.0], [2111, 0.0], [2112, 0.0], [2113, 0.0],
    [2114, 0.0], [2115, 0.0], [2116, 0.0], [2117, 0.0], [2118, 0.0], [2119, 0.0],
    [2120, 0.0], [2121, 0.0], [2122, 0.0], [2123, 0.0], [2124, 0.0], [2125, 0.0],
    [2126, 0.0], [2127, 0.0], [2128, 0.0], [2129, 0.0], [2130, 0.0], [2131, 0.0],
    [2132, 0.0], [2133, 0.0], [2134, 0.0], [2135, 0.0], [2136, 0.0], [2137, 0.0],
    [2138, 0.0], [2139, 0.0]])

# SolarPVUtil "Operating Cost"!O126:O250
soln_only_single_iunit_payback_nparray = np.array([
    [2015, 0], [2016, 0], [2017, 0], [2018, 0], [2019, 0], [2020, 0], [2021, 0],
    [2022, 0], [2023, 1], [2024, 1], [2025, 1], [2026, 1], [2027, 1], [2028, 1],
    [2029, 1], [2030, 1], [2031, 1], [2032, 1], [2033, 1], [2034, 1], [2035, 1],
    [2036, 1], [2037, 1], [2038, 1], [2039, 1], [2040, 1], [2041, 1], [2042, 1],
    [2043, 1], [2044, 1], [2045, 1], [2046, 1], [2047, 1], [2048, 1], [2049, 1],
    [2050, 1], [2051, 1], [2052, 1], [2053, 1], [2054, 1], [2055, 1], [2056, 1],
    [2057, 1], [2058, 1], [2059, 1], [2060, 1], [2061, 1], [2062, 1], [2063, 1],
    [2064, 1], [2065, 1], [2066, 1], [2067, 1], [2068, 1], [2069, 1], [2070, 1],
    [2071, 1], [2072, 1], [2073, 1], [2074, 1], [2075, 1], [2076, 1], [2077, 1],
    [2078, 1], [2079, 1], [2080, 1], [2081, 1], [2082, 1], [2083, 1], [2084, 1],
    [2085, 1], [2086, 1], [2087, 1], [2088, 1], [2089, 1], [2090, 1], [2091, 1],
    [2092, 1], [2093, 1], [2094, 1], [2095, 1], [2096, 1], [2097, 1], [2098, 1],
    [2099, 1], [2100, 1], [2101, 1], [2102, 1], [2103, 1], [2104, 1], [2105, 1],
    [2106, 1], [2107, 1], [2108, 1], [2109, 1], [2110, 1], [2111, 1], [2112, 1],
    [2113, 1], [2114, 1], [2115, 1], [2116, 1], [2117, 1], [2118, 1], [2119, 1],
    [2120, 1], [2121, 1], [2122, 1], [2123, 1], [2124, 1], [2125, 1], [2126, 1],
    [2127, 1], [2128, 1], [2129, 1], [2130, 1], [2131, 1], [2132, 1], [2133, 1],
    [2134, 1], [2135, 1], [2136, 1], [2137, 1], [2138, 1], [2139, 1]])

# SolarPVUtil "Operating Cost"!P126:P250
soln_only_single_iunit_payback_discounted_nparray = np.array([
    [2015, 0], [2016, 0], [2017, 0], [2018, 0], [2019, 0], [2020, 0], [2021, 0],
    [2022, 0], [2023, 0], [2024, 0], [2025, 0], [2026, 0], [2027, 0], [2028, 0],
    [2029, 0], [2030, 1], [2031, 1], [2032, 1], [2033, 1], [2034, 1], [2035, 1],
    [2036, 1], [2037, 1], [2038, 1], [2039, 1], [2040, 1], [2041, 1], [2042, 1],
    [2043, 1], [2044, 1], [2045, 1], [2046, 1], [2047, 1], [2048, 1], [2049, 1],
    [2050, 1], [2051, 1], [2052, 1], [2053, 1], [2054, 1], [2055, 1], [2056, 1],
    [2057, 1], [2058, 1], [2059, 1], [2060, 1], [2061, 1], [2062, 1], [2063, 1],
    [2064, 1], [2065, 1], [2066, 1], [2067, 1], [2068, 1], [2069, 1], [2070, 1],
    [2071, 1], [2072, 1], [2073, 1], [2074, 1], [2075, 1], [2076, 1], [2077, 1],
    [2078, 1], [2079, 1], [2080, 1], [2081, 1], [2082, 1], [2083, 1], [2084, 1],
    [2085, 1], [2086, 1], [2087, 1], [2088, 1], [2089, 1], [2090, 1], [2091, 1],
    [2092, 1], [2093, 1], [2094, 1], [2095, 1], [2096, 1], [2097, 1], [2098, 1],
    [2099, 1], [2100, 1], [2101, 1], [2102, 1], [2103, 1], [2104, 1], [2105, 1],
    [2106, 1], [2107, 1], [2108, 1], [2109, 1], [2110, 1], [2111, 1], [2112, 1],
    [2113, 1], [2114, 1], [2115, 1], [2116, 1], [2117, 1], [2118, 1], [2119, 1],
    [2120, 1], [2121, 1], [2122, 1], [2123, 1], [2124, 1], [2125, 1], [2126, 1],
    [2127, 1], [2128, 1], [2129, 1], [2130, 1], [2131, 1], [2132, 1], [2133, 1],
    [2134, 1], [2135, 1], [2136, 1], [2137, 1], [2138, 1], [2139, 1]])

# SolarPVUtil 'Unit Adoption'!B251:L298
soln_net_annual_funits_adopted_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 59.16952483163, -75.62640223557, -0.33768156367, -22.15920892112, -1.71009099271, -15.41714380040,
     -15.43313810117, -3.07011430874, -55.75969246529, -13.21605539049],
    [2016, 150.52159292976, -76.24855891557, -0.34297979401, -23.24591339780, -1.84510420765, -16.18366871191,
     -15.89405398012, -3.39192750636, -56.24733048614, -13.30746078097],
    [2017, 257.36122967139, -76.87071559558, -0.34827802435, -24.33261787447, -1.98011742258, -16.95019362342,
     -16.35496985906, -3.71374070399, -56.73496850699, -13.39886617146],
    [2018, 378.99298898654, -77.49287227559, -0.35357625469, -25.41932235115, -2.11513063752, -17.71671853493,
     -16.81588573801, -4.03555390161, -57.22260652784, -13.49027156194],
    [2019, 514.72142480523, -78.11502895560, -0.35887448503, -26.50602682782, -2.25014385245, -18.48324344644,
     -17.27680161696, -4.35736709924, -57.71024454869, -13.58167695243],
    [2020, 514.73678922371, -78.73718563561, -0.36417271537, -27.59273130450, -2.38515706739, -19.24976835795,
     -17.73771749591, -4.67918029686, -58.19788256953, -13.67308234291],
    [2021, 825.68654167325, -79.35934231562, -0.36947094570, -28.67943578117, -2.52017028232, -20.01629326946,
     -18.19863337485, -5.00099349449, -58.68552059038, -13.76448773340],
    [2022, 999.53233058261, -79.98149899563, -0.37476917604, -29.76614025785, -2.65518349726, -20.78281818097,
     -18.65954925380, -5.32280669212, -59.17315861123, -13.85589312388],
    [2023, 1184.69301171557, -80.60365567564, -0.38006740638, -30.85284473453, -2.79019671219, -21.54934309248,
     -19.12046513275, -5.64461988974, -59.66079663208, -13.94729851437],
    [2024, 1380.47313900213, -81.22581235565, -0.38536563672, -31.93954921120, -2.92520992713, -22.31586800399,
     -19.58138101170, -5.96643308737, -60.14843465293, -14.03870390485],
    [2025, 1433.94497468791, -81.84796903566, -0.39066386706, -33.02625368788, -3.06022314206, -23.08239291550,
     -20.04229689064, -6.28824628499, -60.63607267378, -14.13010929534],
    [2026, 1801.10994775612, -82.47012571567, -0.39596209740, -34.11295816455, -3.19523635700, -23.84891782701,
     -20.50321276959, -6.61005948262, -61.12371069462, -14.22151468583],
    [2027, 2024.57573708357, -83.09228239568, -0.40126032774, -35.19966264123, -3.33024957193, -24.61544273852,
     -20.96412864854, -6.93187268024, -61.61134871547, -14.31292007631],
    [2028, 2255.87918828469, -83.71443907569, -0.40655855808, -36.28636711790, -3.46526278687, -25.38196765003,
     -21.42504452749, -7.25368587787, -62.09898673632, -14.40432546680],
    [2029, 2494.32485528949, -84.33659575570, -0.41185678841, -37.37307159458, -3.60027600180, -26.14849256154,
     -21.88596040643, -7.57549907549, -62.58662475717, -14.49573085728],
    [2030, 2856.55316015211, -84.95875243571, -0.41715501875, -38.45977607125, -3.73528921674, -26.91501747306,
     -22.34687628538, -7.89731227312, -63.07426277802, -14.58713624777],
    [2031, 2989.86105243015, -85.58090911572, -0.42245324909, -39.54648054793, -3.87030243167, -27.68154238457,
     -22.80779216433, -8.21912547074, -63.56190079887, -14.67854163825],
    [2032, 3245.56069042605, -86.20306579573, -0.42775147943, -40.63318502461, -4.00531564661, -28.44806729608,
     -23.26870804327, -8.54093866837, -64.04953881971, -14.76994702874],
    [2033, 3505.62075994569, -86.82522247573, -0.43304970977, -41.71988950128, -4.14032886154, -29.21459220759,
     -23.72962392222, -8.86275186600, -64.53717684056, -14.86135241922],
    [2034, 3769.34581491907, -87.44737915574, -0.43834794011, -42.80659397796, -4.27534207648, -29.98111711910,
     -24.19053980117, -9.18456506362, -65.02481486141, -14.95275780971],
    [2035, 4036.04040927621, -88.06953583575, -0.44364617045, -43.89329845463, -4.41035529141, -30.74764203061,
     -24.65145568012, -9.50637826125, -65.51245288226, -15.04416320019],
    [2036, 4305.00909694713, -88.69169251576, -0.44894440079, -44.98000293131, -4.54536850635, -31.51416694212,
     -25.11237155906, -9.82819145887, -66.00009090311, -15.13556859068],
    [2037, 4575.55643186183, -89.31384919577, -0.45424263112, -46.06670740798, -4.68038172128, -32.28069185363,
     -25.57328743801, -10.15000465650, -66.48772892395, -15.22697398117],
    [2038, 4846.98696795034, -89.93600587578, -0.45954086146, -47.15341188466, -4.81539493622, -33.04721676514,
     -26.03420331696, -10.47181785412, -66.97536694480, -15.31837937165],
    [2039, 5118.60525914267, -90.55816255579, -0.46483909180, -48.24011636133, -4.95040815115, -33.81374167665,
     -26.49511919591, -10.79363105175, -67.46300496565, -15.40978476214],
    [2040, 5437.16953108051, -91.18031923580, -0.47013732214, -49.32682083801, -5.08542136609, -34.58026658816,
     -26.95603507485, -11.11544424937, -67.95064298650, -15.50119015262],
    [2041, 5659.62332255882, -91.80247591581, -0.47543555248, -50.41352531469, -5.22043458102, -35.34679149967,
     -27.41695095380, -11.43725744700, -68.43828100735, -15.59259554311],
    [2042, 5927.63220264268, -92.42463259582, -0.48073378282, -51.50022979136, -5.35544779596, -36.11331641118,
     -27.87786683275, -11.75907064462, -68.92591902820, -15.68400093359],
    [2043, 6193.04705355042, -93.04678927583, -0.48603201316, -52.58693426804, -5.49046101089, -36.87984132269,
     -28.33878271170, -12.08088384225, -69.41355704904, -15.77540632408],
    [2044, 6455.17242921204, -93.66894595584, -0.49133024350, -53.67363874471, -5.62547422583, -37.64636623420,
     -28.79969859064, -12.40269703988, -69.90119506989, -15.86681171456],
    [2045, 6713.31288355757, -94.29110263585, -0.49662847384, -54.76034322139, -5.76048744076, -38.41289114571,
     -29.26061446959, -12.72451023750, -70.38883309074, -15.95821710505],
    [2046, 6966.77297051701, -94.91325931586, -0.50192670417, -55.84704769806, -5.89550065570, -39.17941605722,
     -29.72153034854, -13.04632343513, -70.87647111159, -16.04962249553],
    [2047, 7214.85724402038, -95.53541599587, -0.50722493451, -56.93375217474, -6.03051387063, -39.94594096873,
     -30.18244622749, -13.36813663275, -71.36410913244, -16.14102788602],
    [2048, 7456.87025799770, -96.15757267588, -0.51252316485, -58.02045665141, -6.16552708557, -40.71246588024,
     -30.64336210643, -13.68994983038, -71.85174715329, -16.23243327651],
    [2049, 7692.11656637898, -96.77972935589, -0.51782139519, -59.10716112809, -6.30054030050, -41.47899079175,
     -31.10427798538, -14.01176302800, -72.33938517413, -16.32383866699],
    [2050, 7895.38590200891, -97.40188603589, -0.52311962553, -60.19386560477, -6.43555351544, -42.24551570326,
     -31.56519386433, -14.33357622563, -72.82702319498, -16.41524405748],
    [2051, 8139.52728207347, -98.02404271590, -0.52841785587, -61.28057008144, -6.57056673037, -43.01204061477,
     -32.02610974327, -14.65538942325, -73.31466121583, -16.50664944796],
    [2052, 8350.30079724671, -98.64619939591, -0.53371608621, -62.36727455812, -6.70557994531, -43.77856552628,
     -32.48702562222, -14.97720262088, -73.80229923668, -16.59805483845],
    [2053, 8551.52582254397, -99.26835607592, -0.53901431655, -63.45397903479, -6.84059316024, -44.54509043779,
     -32.94794150117, -15.29901581851, -74.28993725753, -16.68946022893],
    [2054, 8742.50691189525, -99.89051275593, -0.54431254688, -64.54068351147, -6.97560637518, -45.31161534930,
     -33.40885738012, -15.62082901613, -74.77757527838, -16.78086561942],
    [2055, 8922.54861923059, -100.51266943594, -0.54961077722, -65.62738798814, -7.11061959011, -46.07814026081,
     -33.86977325906, -15.94264221376, -75.26521329922, -16.87227100990],
    [2056, 9090.95549847998, -101.13482611595, -0.55490900756, -66.71409246482, -7.24563280505, -46.84466517233,
     -34.33068913801, -16.26445541138, -75.75285132007, -16.96367640039],
    [2057, 9247.03210357344, -101.75698279596, -0.56020723790, -67.80079694150, -7.38064601998, -47.61119008384,
     -34.79160501696, -16.58626860901, -76.24048934092, -17.05508179088],
    [2058, 9390.08298844099, -102.37913947597, -0.56550546824, -68.88750141817, -7.51565923492, -48.37771499535,
     -35.25252089591, -16.90808180663, -76.72812736177, -17.14648718136],
    [2059, 9519.41270701265, -103.00129615598, -0.57080369858, -69.97420589485, -7.65067244985, -49.14423990686,
     -35.71343677485, -17.22989500426, -77.21576538262, -17.23789257185],
    [2060, 9634.32581321841, -103.62345283599, -0.57610192892, -71.06091037152, -7.78568566479, -49.91076481837,
     -36.17435265380, -17.55170820188, -77.70340340347, -17.32929796233]]

# ImprovedCookStoves "First Cost"!C37:C82
soln_pds_install_cost_per_iunit_cookstoves_nparray = np.array([
    [2015, 39.0], [2016, 39.0], [2017, 39.0], [2018, 39.0], [2019, 39.0], [2020, 39.0],
    [2021, 39.0], [2022, 39.0], [2023, 39.0], [2024, 39.0], [2025, 39.0], [2026, 39.0],
    [2027, 39.0], [2028, 39.0], [2029, 39.0], [2030, 39.0], [2031, 39.0], [2032, 39.0],
    [2033, 39.0], [2034, 39.0], [2035, 39.0], [2036, 39.0], [2037, 39.0], [2038, 39.0],
    [2039, 39.0], [2040, 39.0], [2041, 39.0], [2042, 39.0], [2043, 39.0], [2044, 39.0],
    [2045, 39.0], [2046, 39.0], [2047, 39.0], [2048, 39.0], [2049, 39.0], [2050, 39.0],
    [2051, 39.0], [2052, 39.0], [2053, 39.0], [2054, 39.0], [2055, 39.0], [2056, 39.0],
    [2057, 39.0], [2058, 39.0], [2059, 39.0], [2060, 39.0]])

# ImprovedCookStoves "First Cost"!O37:O82
conv_ref_install_cost_per_iunit_cookstoves_nparray = np.array([
    [2015, 2.048761039056780], [2016, 2.048761039056780],
    [2017, 2.048761039056780], [2018, 2.048761039056780],
    [2019, 2.048761039056780], [2020, 2.048761039056780],
    [2021, 2.048761039056780], [2022, 2.048761039056780],
    [2023, 2.048761039056780], [2024, 2.048761039056780],
    [2025, 2.048761039056780], [2026, 2.048761039056780],
    [2027, 2.048761039056780], [2028, 2.048761039056780],
    [2029, 2.048761039056780], [2030, 2.048761039056780],
    [2031, 2.048761039056780], [2032, 2.048761039056780],
    [2033, 2.048761039056780], [2034, 2.048761039056780],
    [2035, 2.048761039056780], [2036, 2.048761039056780],
    [2037, 2.048761039056780], [2038, 2.048761039056780],
    [2039, 2.048761039056780], [2040, 2.048761039056780],
    [2041, 2.048761039056780], [2042, 2.048761039056780],
    [2043, 2.048761039056780], [2044, 2.048761039056780],
    [2045, 2.048761039056780], [2046, 2.048761039056780],
    [2047, 2.048761039056780], [2048, 2.048761039056780],
    [2049, 2.048761039056780], [2050, 2.048761039056780],
    [2051, 2.048761039056780], [2052, 2.048761039056780],
    [2053, 2.048761039056780], [2054, 2.048761039056780],
    [2055, 2.048761039056780], [2056, 2.048761039056780],
    [2057, 2.048761039056780], [2058, 2.048761039056780],
    [2059, 2.048761039056780], [2060, 2.048761039056780]])

# ImprovedCookStoves "Operating Cost"!I126:I250
soln_vs_conv_single_iunit_cashflow_cookstoves_nparray = np.array([
    [2015, -21.84550514012750], [2016, 17.15449485987250],
    [2017, 15.10573382081580], [2018, 16.93636303521490], [2019, 7.88594351304656],
    [2020, 0.0], [2021, 0.0], [2022, 0.0], [2023, 0.0]])

# InstreamHydro "First Cost"!C37:C82
soln_pds_install_cost_per_iunit_instreamhydro_nparray = np.array([
    [2015, 2721605263157.90], [2016, 2718655137354.17],
    [2017, 2715813888421.44], [2018, 2713073867305.68],
    [2019, 2710428200385.54], [2020, 2707870688287.98],
    [2021, 2705395720668.42], [2022, 2702998204027.43],
    [2023, 2700673500243.46], [2024, 2697826976867.23],
    [2025, 2694924218031.68], [2026, 2692010851374.75],
    [2027, 2689092152106.43], [2028, 2686172857269.08],
    [2029, 2683257201285.35], [2030, 2680348952109.59],
    [2031, 2677451447168.92], [2032, 2674567628475.18],
    [2033, 2671700076450.78], [2034, 2668851042147.30],
    [2035, 2666022477645.31], [2036, 2663216064514.37],
    [2037, 2660433240279.16], [2038, 2657675222893.09],
    [2039, 2654943033258.43], [2040, 2652237515862.35],
    [2041, 2649559357617.90], [2042, 2646909105009.72],
    [2043, 2644287179655.00], [2044, 2641693892390.48],
    [2045, 2639129455996.76], [2046, 2636593996670.27],
    [2047, 2634087564347.09], [2048, 2631610141979.27],
    [2049, 2629161653857.33], [2050, 2626741973067.38],
    [2051, 2624350928164.51], [2052, 2621988309136.95],
    [2053, 2619653872731.43], [2054, 2617347347201.86],
    [2055, 2615068436539.78], [2056, 2612816824238.41],
    [2057, 2610592176638.52], [2058, 2608394145898.56],
    [2059, 2606222372628.25], [2060, 2604076488220.56]])

# InstreamHydro "First Cost"!O37:O82
conv_ref_install_cost_per_iunit_instreamhydro_nparray = np.array([
    [2015, 2005710507515.67], [2016, 2003672951568.66],
    [2017, 2001706434985.60], [2018, 1999806175641.75],
    [2019, 1997967852145.23], [2020, 1996187546615.34],
    [2021, 1994461696067.01], [2022, 1992787050894.79],
    [2023, 1991160639248.32], [2024, 1989579736324.55],
    [2025, 1988041837784.85], [2026, 1986544636649.93],
    [2027, 1985086003141.06], [2028, 1983663967028.16],
    [2029, 1982276702120.15], [2030, 1980922512593.09],
    [2031, 1979599820901.14], [2032, 1978307157055.61],
    [2033, 1977043149090.45], [2034, 1975806514560.27],
    [2035, 1974596052939.68], [2036, 1973410638811.61],
    [2037, 1972249215748.60], [2038, 1971110790804.09],
    [2039, 1969994429542.25], [2040, 1968899251544.49],
    [2041, 1967824426338.76], [2042, 1966769169704.93],
    [2043, 1965732740315.30], [2044, 1964714436674.42],
    [2045, 1963713594326.85], [2046, 1962729583305.21],
    [2047, 1961761805794.08], [2048, 1960809693988.36],
    [2049, 1959872708126.83], [2050, 1958950334684.14],
    [2051, 1958042084706.13], [2052, 1957147492274.98],
    [2053, 1956266113092.40], [2054, 1955397523170.02],
    [2055, 1954541317617.36], [2056, 1953697109519.01],
    [2057, 1952864528892.96], [2058, 1952043221723.39],
    [2059, 1951232849061.51], [2060, 1950433086188.81]])

# InstreamHydro "Operating Cost"!I126:I250
soln_vs_conv_single_iunit_cashflow_instreamhydro_nparray = np.array([
    [2015, -855731318827.22], [2016, 308368337736.67],
    [2017, 308368337736.67], [2018, 308368337736.67],
    [2019, 308368337736.67], [2020, 308368337736.67],
    [2021, 308368337736.67], [2022, 308368337736.67],
    [2023, 308368337736.67], [2024, 308368337736.67],
    [2025, 308368337736.67], [2026, 308368337736.67],
    [2027, 308368337736.67], [2028, 308368337736.67],
    [2029, 308368337736.67], [2030, 308368337736.67],
    [2031, 308368337736.67], [2032, 308368337736.67],
    [2033, 308368337736.67], [2034, 308368337736.67],
    [2035, 308368337736.67], [2036, 308368337736.67],
    [2037, 308368337736.67], [2038, 308368337736.67],
    [2039, 308368337736.67], [2040, 308368337736.67],
    [2041, 308368337736.67], [2042, 308368337736.67],
    [2043, 308368337736.67], [2044, 308368337736.67],
    [2045, 308368337736.67], [2046, 308368337736.67],
    [2047, 308368337736.67], [2048, 308368337736.67],
    [2049, 308368337736.67], [2050, 308368337736.67],
    [2051, 560998909594.51], [2052, 308368337736.67],
    [2053, 308368337736.67], [2054, 308368337736.67],
    [2055, 308368337736.67], [2056, 308368337736.67],
    [2057, 44052619676.67], [2058, 0.0], [2059, 0.0], [2060, 0.0]])

# InstreamHydro "Operating Cost"!M126:M250
soln_only_single_iunit_cashflow_instreamhydro_nparray = np.array([
    [2015, -2407445550685], [2016, 308368337737],
    [2017, 308368337737], [2018, 308368337737],
    [2019, 308368337737], [2020, 308368337737],
    [2021, 308368337737], [2022, 308368337737],
    [2023, 308368337737], [2024, 308368337737],
    [2025, 308368337737], [2026, 308368337737],
    [2027, 308368337737], [2028, 308368337737],
    [2029, 308368337737], [2030, 308368337737],
    [2031, 308368337737], [2032, 308368337737],
    [2033, 308368337737], [2034, 308368337737],
    [2035, 308368337737], [2036, 308368337737],
    [2037, 308368337737], [2038, 308368337737],
    [2039, 308368337737], [2040, 308368337737],
    [2041, 308368337737], [2042, 308368337737],
    [2043, 308368337737], [2044, 308368337737],
    [2045, 308368337737], [2046, 308368337737],
    [2047, 308368337737], [2048, 308368337737],
    [2049, 308368337737], [2050, 308368337737],
    [2051, 308368337737], [2052, 308368337737],
    [2053, 308368337737], [2054, 308368337737],
    [2055, 308368337737], [2056, 308368337737],
    [2057, 44052619677], [2058, 0.0], [2059, 0.0], [2060, 0.0]])
