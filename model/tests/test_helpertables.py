"""Tests for helpertables.py."""

import pathlib
from model import advanced_controls
from model import helpertables
import numpy as np
import pandas as pd
import pytest

datadir = pathlib.Path(__file__).parents[0].joinpath('data')
ref_tam_per_region_filename = datadir.joinpath('ref_tam_per_region.csv')
ref_tam_per_region = pd.read_csv(ref_tam_per_region_filename, header=0, index_col=0,
                                 skipinitialspace=True, comment='#')
pds_tam_per_region_filename = datadir.joinpath('pds_tam_per_region.csv')
pds_tam_per_region = pd.read_csv(pds_tam_per_region_filename, header=0, index_col=0,
                                 skipinitialspace=True, comment='#')


def test_soln_ref_funits_adopted():
    """Test simple case, compute adoption from linear regression of datapoints."""
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False)
    ref_datapoints = pd.DataFrame([
        [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778,
         14.65061888889, 14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
        [2050, 272.41409799109, 97.40188603589, 0.52311962553, 60.19386560477, 6.43555351544,
         42.24551570326, 31.56519386433, 14.33357622563, 72.82702319498, 16.41524405748]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU",
                 "USA"]).set_index("Year")
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=None,
            ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=None,
            pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
            pds_adoption_is_single_source=False)
    result = ht.soln_ref_funits_adopted()
    expected = pd.DataFrame(soln_ref_funits_adopted_list[1:],
            columns=soln_ref_funits_adopted_list[0]).set_index('Year')
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_ref_funits_adopted_tam_limit():
    """Test when adoption is limited by the Total Addressable Market."""
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False)
    ref_datapoints = pd.DataFrame([
        [2014, 100.0, 100.0, 100.0, 100.0], [2050, 200.0, 200.0, 200.0, 200.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)"]).set_index(
        "Year")
    ref_tam_per_region = pd.DataFrame([
        [2014, 1.0, 1.0, 1.0, 1.0], [2015, 1.0, 1.0, 1.0, 1.0], [2016, 1.0, 1.0, 1.0, 1.0],
        [2017, 1.0, 1.0, 1.0, 1.0], [2018, 1.0, 1.0, 1.0, 1.0], [2019, 1.0, 1.0, 1.0, 1.0],
        [2020, 1.0, 1.0, 1.0, 1.0], [2021, 1.0, 1.0, 1.0, 1.0], [2022, 1.0, 1.0, 1.0, 1.0],
        [2023, 1.0, 1.0, 1.0, 1.0], [2024, 1.0, 1.0, 1.0, 1.0], [2025, 1.0, 1.0, 1.0, 1.0],
        [2026, 1.0, 1.0, 1.0, 1.0], [2027, 1.0, 1.0, 1.0, 1.0], [2028, 1.0, 1.0, 1.0, 1.0],
        [2029, 1.0, 1.0, 1.0, 1.0], [2030, 1.0, 1.0, 1.0, 1.0], [2031, 1.0, 1.0, 1.0, 1.0],
        [2032, 1.0, 1.0, 1.0, 1.0], [2033, 1.0, 1.0, 1.0, 1.0], [2034, 1.0, 1.0, 1.0, 1.0],
        [2035, 1.0, 1.0, 1.0, 1.0], [2036, 1.0, 1.0, 1.0, 1.0], [2037, 1.0, 1.0, 1.0, 1.0],
        [2038, 1.0, 1.0, 1.0, 1.0], [2039, 1.0, 1.0, 1.0, 1.0], [2040, 1.0, 1.0, 1.0, 1.0],
        [2041, 1.0, 1.0, 1.0, 1.0], [2042, 1.0, 1.0, 1.0, 1.0], [2043, 1.0, 1.0, 1.0, 1.0],
        [2044, 1.0, 1.0, 1.0, 1.0], [2045, 1.0, 1.0, 1.0, 1.0], [2046, 1.0, 1.0, 1.0, 1.0],
        [2047, 1.0, 1.0, 1.0, 1.0], [2048, 1.0, 1.0, 1.0, 1.0], [2049, 1.0, 1.0, 1.0, 1.0],
        [2050, 1.0, 1.0, 1.0, 1.0], [2051, 1.0, 1.0, 1.0, 1.0], [2052, 1.0, 1.0, 1.0, 1.0],
        [2053, 1.0, 1.0, 1.0, 1.0], [2054, 1.0, 1.0, 1.0, 1.0], [2055, 1.0, 1.0, 1.0, 1.0],
        [2056, 1.0, 1.0, 1.0, 1.0], [2057, 1.0, 1.0, 1.0, 1.0], [2058, 1.0, 1.0, 1.0, 1.0],
        [2059, 1.0, 1.0, 1.0, 1.0], [2060, 1.0, 1.0, 1.0, 1.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)"]).set_index(
        "Year")
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=None,
                                   ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=None,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_ref_funits_adopted()
    expected = ref_tam_per_region.copy()
    expected.loc[2014, :] = 100.0
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_ref_funits_adopted_base_year_2018():
    """Test when initial year is after 2014, auto-fallback to PDS."""
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
            soln_pds_adoption_basis='Linear')
    columns = ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)"]
    ref_datapoints = pd.DataFrame([[2018, 2.0, 2.0, 2.0, 2.0], [2050, 2.0, 2.0, 2.0, 2.0]],
            columns=columns).set_index("Year")
    pds_datapoints = pd.DataFrame([[2014, 1.0, 1.0, 1.0, 1.0], [2050, 1.0, 1.0, 1.0, 1.0]],
            columns=columns).set_index("Year")
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints,
            pds_datapoints=pds_datapoints, ref_adoption_limits=ref_tam_per_region,
            pds_adoption_limits=None, pds_adoption_data_per_region=None,
            pds_adoption_trend_per_region=None, pds_adoption_is_single_source=False,
            adoption_base_year=2018, copy_pds_to_ref=True)
    result = ht.soln_ref_funits_adopted()
    exp1 = pd.DataFrame(1.0, columns=columns[1:], index=result.index.copy())
    exp2 = pd.DataFrame(2.0, columns=columns[1:], index=result.index.copy())
    pd.testing.assert_series_equal(result.loc[2014:2017, "World"], exp1.loc[2014:2017, "World"])
    for region in columns[2:]:
        pd.testing.assert_series_equal(result.loc[2014:2017, region], exp2.loc[2014:2017, region])
    pd.testing.assert_frame_equal(result.loc[2018:2050, :], exp2.loc[2018:2050, :])
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints,
            pds_datapoints=pds_datapoints, ref_adoption_limits=ref_tam_per_region,
            pds_adoption_limits=None, pds_adoption_data_per_region=None,
            pds_adoption_trend_per_region=None, pds_adoption_is_single_source=False,
            adoption_base_year=2018, copy_pds_to_ref=False)
    result = ht.soln_ref_funits_adopted()
    pd.testing.assert_frame_equal(result, exp2)


def test_soln_pds_funits_adopted_by_region_with_tam_limit_world():
    """Test when World adoption is limited by the Total Addressable Market."""
    ac = advanced_controls.AdvancedControls(soln_pds_adoption_regional_data=True,
                                            soln_pds_adoption_basis='Linear')
    pds_datapoints = pd.DataFrame([
        [2020, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        [2030, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America"]).set_index("Year")
    pds_tam_per_region = pd.DataFrame([
        [2020, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2021, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2022, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2023, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2024, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2025, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2026, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2027, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2028, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2029, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [2030, 1.0, 200.0, 200.0, 200.0, 200.0, 200.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America"]).set_index("Year")
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_pds_funits_adopted()
    assert result.loc[2030, 'World'] == pytest.approx(1.0)


def test_soln_ref_funits_adopted_regional_sums():
    """Test with soln_ref_adoption_regional_data=True."""
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=True)
    ref_datapoints = pd.DataFrame([
        [2014, 10.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2050, 20.0, 3.0, 2.0, 1.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America"]).set_index("Year")
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=None,
                                   ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=None,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_ref_funits_adopted()
    expected = pd.DataFrame([
        [2014, 10.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2015, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2016, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2017, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2018, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2019, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2020, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2021, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2022, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2023, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2024, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2025, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2026, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2027, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2028, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2029, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2030, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2031, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2032, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2033, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2034, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2035, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2036, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2037, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2038, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2039, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2040, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2041, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2042, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2043, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2044, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2045, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2046, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2047, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2048, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2049, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2050, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2051, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2052, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2053, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2054, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2055, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2056, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2057, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2058, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0], [2059, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        [2060, 6.0, 3.0, 2.0, 1.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America"]).set_index("Year")
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_ref_funits_adopted_custom_ref_adoption():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_ref_adoption_basis='Custom')
    ref_datapoints = pd.DataFrame([
        [2014, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [2050, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    ref_adoption_data_per_region = pd.DataFrame(ref_adoption_data_per_region_insulation_list[1:],
                                            columns=ref_adoption_data_per_region_insulation_list[0]).set_index('Year')
    ref_adoption_data_per_region.name = 'ref_adoption_data_per_region'
    ref_tam_per_region_insulation = pd.DataFrame(ref_tam_per_region_insulation_list[1:],
                                                 columns=ref_tam_per_region_insulation_list[0]).set_index('Year')
    ref_tam_per_region_insulation.name = 'ref_tam_per_region'
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=None,
                                   ref_adoption_limits=ref_tam_per_region_insulation, pds_adoption_data_per_region=None,
                                   ref_adoption_data_per_region=ref_adoption_data_per_region)
    result = ht.soln_ref_funits_adopted()
    expected = ref_adoption_data_per_region.copy()
    expected.loc[2014, :] = 1.0
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result, expected.loc[2014:], check_exact=False)


def test_soln_ref_funits_adopted_custom_ref_adoption_tam_limit():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_ref_adoption_basis='Custom')
    ref_datapoints = pd.DataFrame([
        [2014, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [2050, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    ref_adoption_data_per_region = pd.DataFrame(ref_adoption_data_per_region_insulation_list[1:],
                                            columns=ref_adoption_data_per_region_insulation_list[0]).set_index('Year')
    ref_adoption_data_per_region.name = 'ref_adoption_data_per_region'
    ref_tam_per_region_limit_seven = pd.DataFrame(ref_tam_per_region_limit_seven_list[1:],
                                                  columns=ref_tam_per_region_limit_seven_list[0]).set_index('Year')
    ref_tam_per_region_limit_seven.name = 'ref_tam_per_region'
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=None,
                                   ref_adoption_limits=ref_tam_per_region_limit_seven,
                                   pds_adoption_data_per_region=None,
                                   ref_adoption_data_per_region=ref_adoption_data_per_region)
    result = ht.soln_ref_funits_adopted()
    expected = ref_tam_per_region_limit_seven
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result.loc[2015:, ['World']], expected.loc[2015:, ['World']],
                                  check_exact=False)


def test_soln_ref_funits_adopted_custom_ref_adoption_base_year_2018():
    ac = advanced_controls.AdvancedControls(
            soln_ref_adoption_regional_data=False, soln_ref_adoption_basis='Custom',
            soln_pds_adoption_basis='Fully Customized PDS')
    regions = ["World", "A", "B", "C"]
    ref_datapoints = pd.DataFrame([[2018, 12.0, 12.0, 12.0, 12.0], [2050, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year"] + regions).set_index("Year")
    ref_ad_per_region = pd.DataFrame(1.0, index=range(2014, 2061), columns=regions)
    ref_ad_per_region.name = 'ref_adoption_data_per_region'
    ref_ad_per_region.index.name = "Year"
    ref_tam_per_region = pd.DataFrame(100.0, index=range(2014, 2061), columns=regions)
    ref_tam_per_region.name = 'ref_tam_per_region'
    pds_datapoints = pd.DataFrame([[2014, 13.0, 13.0, 13.0, 13.0], [2050, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year"] + regions).set_index("Year")
    pds_ad_per_region = pd.DataFrame(2.0, index=range(2014, 2061), columns=regions)
    pds_ad_per_region.name = 'pds_adoption_data_per_region'
    pds_ad_per_region.index.name = "Year"
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints,
            pds_datapoints=pds_datapoints, ref_adoption_limits=ref_tam_per_region,
            pds_adoption_data_per_region=pds_ad_per_region, adoption_base_year=2018,
            ref_adoption_data_per_region=ref_ad_per_region, copy_pds_to_ref=True)
    result = ht.soln_ref_funits_adopted()
    expected = ref_ad_per_region.loc[2014:2017].copy()
    expected.loc[:, 'World'] = pds_ad_per_region.loc[2014:2017, 'World']
    expected.loc[2014, 'World'] = 13.0  # first pds_datapoint always copied into pds result
    expected.loc[2014, ['A', 'B', 'C']] = 12.0
    pd.testing.assert_frame_equal(result.loc[2014:2017], expected)
    pd.testing.assert_frame_equal(result.loc[2018:], ref_ad_per_region.loc[2018:])
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints,
            pds_datapoints=pds_datapoints, ref_adoption_limits=ref_tam_per_region,
            pds_adoption_data_per_region=pds_ad_per_region, adoption_base_year=2018,
            ref_adoption_data_per_region=ref_ad_per_region, copy_pds_to_ref=False)
    result = ht.soln_ref_funits_adopted()
    expected = ref_ad_per_region.copy()
    expected.loc[2018] = 12.0  # first ref_datapoint always copied into pds result
    pd.testing.assert_frame_equal(result, expected)


def test_soln_ref_funits_adopted_regional_tam_limit_NaN():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False)
    # Data from SolarHotWater "Helper Tables"!C21:L22 and "Unit Adoption Calculations"!A16:K63
    ref_datapoints = pd.DataFrame([
        [2014, 335.463, 56.493, 2.374, 240.305, 9.948, 9.113, 231.838, 6.435, 23.777, 17.233],
        [2050, 472.926283, 68.484463, 3.301129, 591.051012, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    ref_tam_per_region_solarhotwater = pd.DataFrame(ref_tam_per_region_solarhotwater_list[1:],
                                                    columns=ref_tam_per_region_solarhotwater_list[0]).set_index('Year')
    ref_tam_per_region_solarhotwater.name = 'ref_tam_per_region'
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=None,
                                   ref_adoption_limits=ref_tam_per_region_solarhotwater, pds_adoption_limits=None,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_ref_funits_adopted()
    expected = pd.DataFrame(soln_ref_funits_adopted_solarhotwater_list[1:],
                            columns=soln_ref_funits_adopted_solarhotwater_list[0]).set_index('Year')
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_funits_adopted_single_source():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_prognostication_growth='Medium',
                                            soln_pds_adoption_prognostication_trend='3rd poly',
                                            soln_pds_adoption_prognostication_source='A',
                                            soln_pds_adoption_basis='Existing Adoption Prognostications')
    pds_datapoints = pd.DataFrame([
        [2014, 112.633033, 75.0042456, 0.332383, 21.072504, 1.575078, 14.650619,
         14.972222, 2.748301, 55.272054, 13.12465],
        [2050, 2603.660640, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_adoption_data_per_region = pd.DataFrame(adoption_data_med_single_source_list[1:],
                                                columns=adoption_data_med_single_source_list[0],
                                                dtype=np.float64).set_index('Year')
    pds_adoption_data_per_region.index = pds_adoption_data_per_region.index.astype(int)
    pds_adoption_trend_per_region = pd.DataFrame(pds_adoption_trend_per_region_list[1:],
                                                 columns=pds_adoption_trend_per_region_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_adoption_trend_per_region.index = pds_adoption_trend_per_region.index.astype(int)
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=pds_adoption_data_per_region,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=True)
    result = ht.soln_pds_funits_adopted()
    expected = pd.DataFrame(soln_pds_funits_adopted_single_source_list[1:],
                            columns=soln_pds_funits_adopted_single_source_list[0]).set_index('Year')
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result.loc[2014:], expected, check_exact=False)


def test_soln_pds_funits_adopted_single_source_2018():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_prognostication_growth='Medium',
                                            soln_pds_adoption_prognostication_trend='3rd poly',
                                            soln_pds_adoption_prognostication_source='A',
                                            soln_pds_adoption_basis='Existing Adoption Prognostications')
    pds_datapoints = pd.DataFrame([
        [2018, 100.0, 75.0, 0.3, 21.0, 1.5, 14.5, 15.0, 2.7, 55.3, 13.1],
        [2050, 2600.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_adoption_data_per_region = pd.DataFrame(adoption_data_med_single_source_list[1:],
                                                columns=adoption_data_med_single_source_list[0],
                                                dtype=np.float64).set_index('Year')
    pds_adoption_data_per_region.index = pds_adoption_data_per_region.index.astype(int)
    pds_adoption_trend_per_region = pd.DataFrame(pds_adoption_trend_per_region_list[1:],
                                                 columns=pds_adoption_trend_per_region_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_adoption_trend_per_region.index = pds_adoption_trend_per_region.index.astype(int)
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=pds_adoption_data_per_region,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=True,
                                   use_first_pds_datapoint_main=False)
    result = ht.soln_pds_funits_adopted()
    expected = pd.DataFrame(soln_pds_funits_adopted_single_source_list[1:],
                            columns=soln_pds_funits_adopted_single_source_list[0]).set_index('Year')
    expected.name = 'soln_ref_funits_adopted'
    # We used to set only years starting with the first datapoint, 2018 in this case. This
    # wasn't correct, check that years starting in 2014 are set.
    pd.testing.assert_series_equal(result.loc[2014:, 'World'], expected['World'], check_exact=False)


def test_soln_pds_funits_adopted_passthru():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_prognostication_growth='Medium',
                                            soln_pds_adoption_prognostication_trend='3rd poly',
                                            soln_pds_adoption_basis='Existing Adoption Prognostications')
    pds_datapoints = pd.DataFrame([
        [2014, 112.633033, 75.0042456, 0.332383, 21.072504, 1.575078, 14.650619,
         14.972222, 2.748301, 55.272054, 13.12465],
        [2050, 2603.660640, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_adoption_data_per_region = pd.DataFrame(adoption_data_med_all_sources_list[1:],
                                                columns=adoption_data_med_all_sources_list[0],
                                                dtype=np.float64).set_index('Year')
    pds_adoption_data_per_region.index = pds_adoption_data_per_region.index.astype(int)
    pds_adoption_trend_per_region = pd.DataFrame(pds_adoption_trend_per_region_list[1:],
                                                 columns=pds_adoption_trend_per_region_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_adoption_trend_per_region.index = pds_adoption_trend_per_region.index.astype(int)
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=pds_adoption_data_per_region,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_pds_funits_adopted()
    expected = pds_adoption_trend_per_region
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_funits_adopted_datapoints_nan():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_prognostication_growth='Medium',
                                            soln_pds_adoption_prognostication_trend='3rd poly',
                                            soln_pds_adoption_basis='Existing Adoption Prognostications')
    pds_datapoints = pd.DataFrame([
        [2014, 112.633033, 1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
        [2050, 2603.660640, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_adoption_data_per_region = pd.DataFrame(adoption_data_med_all_sources_list[1:],
                                                columns=adoption_data_med_all_sources_list[0],
                                                dtype=np.float64).set_index('Year')
    pds_adoption_data_per_region.index = pds_adoption_data_per_region.index.astype(int)
    pds_adoption_trend_per_region = pd.DataFrame(pds_adoption_trend_per_region_list[1:],
                                                 columns=pds_adoption_trend_per_region_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_adoption_trend_per_region.index = pds_adoption_trend_per_region.index.astype(int)
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=pds_adoption_data_per_region,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_pds_funits_adopted()
    assert result.loc[2014, 'World'] == pytest.approx(112.633033)
    assert result.loc[2014, 'OECD90'] == pytest.approx(1.0)
    assert result.loc[2014, 'Eastern Europe'] == pytest.approx(2.0)
    assert result.loc[2014, 'Asia (Sans Japan)'] == pytest.approx(21.072504)
    assert result.loc[2014, 'Middle East and Africa'] == pytest.approx(4.0)


def test_soln_pds_funits_adopted_zero_regional():
    # Case which came up in LandfillMethane, where datapoints for 2014 and 2050 were 0.0
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_prognostication_growth='Medium',
                                            soln_pds_adoption_prognostication_trend='3rd poly',
                                            soln_pds_adoption_basis='Existing Adoption Prognostications')
    pds_datapoints = pd.DataFrame([
        [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_adoption_data_per_region = pd.DataFrame(adoption_data_med_all_sources_list[1:],
                                                columns=adoption_data_med_all_sources_list[0],
                                                dtype=np.float64).set_index('Year')
    pds_adoption_data_per_region.index = pds_adoption_data_per_region.index.astype(int)
    pds_adoption_trend_per_region = pd.DataFrame(pds_adoption_trend_per_region_list[1:],
                                                 columns=pds_adoption_trend_per_region_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_adoption_trend_per_region.index = pds_adoption_trend_per_region.index.astype(int)
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=pds_adoption_data_per_region,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_pds_funits_adopted()
    assert result.loc[2015, 'USA'] == 0
    assert result.loc[2030, 'OECD90'] == 0
    assert result.loc[2043, 'EU'] == 0


def test_soln_pds_funits_custom_pds():
    datadir = pathlib.Path(__file__).parents[0].joinpath('data')
    custom_scen = pd.read_csv(datadir.joinpath('ca_scenario_1_trr.csv'), index_col=0)
    ac = advanced_controls.AdvancedControls(soln_pds_adoption_basis='Fully Customized PDS')
    ht_ref_datapoints = pd.DataFrame([[2014] + [0] * 10, [2050] + [0] * 10],
            columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                'USA']).set_index('Year')
    ht_pds_datapoints = ht_ref_datapoints
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=custom_scen,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints)
    pd.testing.assert_frame_equal(ht.soln_pds_funits_adopted().iloc[1:, :],
            custom_scen.iloc[3:, :])
    assert sum(ht.soln_pds_funits_adopted().loc[2014]) == 0


def test_soln_pds_funits_custom_pds_tam_limit():
    datadir = pathlib.Path(__file__).parents[0].joinpath('data')
    custom_scen = pd.read_csv(datadir.joinpath('ca_scenario_1_trr.csv'), index_col=0)
    ac = advanced_controls.AdvancedControls(soln_pds_adoption_basis='Fully Customized PDS')
    ht_ref_datapoints = pd.DataFrame([[2014] + [0] * 10, [2050] + [0] * 10],
            columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                'USA']).set_index('Year')
    ht_pds_datapoints = ht_ref_datapoints
    pds_tam_per_region_limit_seven = pd.DataFrame(ref_tam_per_region_limit_seven_list[1:],
            columns=ref_tam_per_region_limit_seven_list[0]).set_index('Year')
    pds_tam_per_region_limit_seven.name = 'pds_tam_per_region'
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=custom_scen,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_limits=pds_tam_per_region_limit_seven)
    expected = pds_tam_per_region_limit_seven
    expected.name = 'soln_pds_funits_adopted'
    result = ht.soln_pds_funits_adopted()
    pd.testing.assert_series_equal(result.loc[2015:, 'World'], expected.loc[2015:, 'World'],
            check_exact=False)


def test_soln_pds_funits_adopted_linear_interpolation():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_basis='DEFAULT Linear')
    # from ImprovedCookStoves
    pds_datapoints = pd.DataFrame([
        [2014, 20.30881991465230, 0.0, 0.0, 25.04194984517460, 5.33726613132968, 36.92512711754970,
         0.0, 0.0, 0.0, 0.0],
        [2050, 1620.90420924928000, 0.0, 0.0, 1005.17634180055000, 752.46582309962500,
         39.65480026979520, 187.87596664323300, 463.99033134231300, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_tam_per_region_cookstoves = pd.DataFrame(pds_tam_per_region_cookstoves_list[1:],
                                                 columns=pds_tam_per_region_cookstoves_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_tam_per_region_cookstoves.index = pds_tam_per_region_cookstoves.index.astype(int)
    expected = pd.DataFrame(soln_pds_funits_adopted_cookstoves_list[1:],
                            columns=soln_pds_funits_adopted_cookstoves_list[0]).set_index('Year')
    expected.name = 'soln_ref_funits_adopted'
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region_cookstoves,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_pds_funits_adopted()
    pd.testing.assert_frame_equal(result.loc[2014:], expected, check_exact=False)
    # ensure that pds_adoption_is_single_source has no effect on Linear interpolation.
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region_cookstoves,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=True)
    result = ht.soln_pds_funits_adopted()
    pd.testing.assert_frame_equal(result.loc[2014:], expected, check_exact=False)


def test_soln_pds_funits_adopted_linear_interpolation_regional_data_tam_limit():
    ac = advanced_controls.AdvancedControls(soln_pds_adoption_regional_data=True,
                                            soln_pds_adoption_basis='DEFAULT Linear')
    # from BuildingAutomation
    pds_datapoints = pd.DataFrame([
        [2014, 16577.8259167003, 14915.99, 0.0, 1087.7709445217, 0.0, 0.0, 1087.7709445217,
         0.0, 3622.85, 11293.14],
        [2050, 74070.9544989679, 30578.7612542884, 766.1476519674, 20286.6671800328, 2070.3305354654,

         510.9664612217, 0.0, 0.0, 11003.3574757203, 36879.9583966389]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_tam_per_region_buildingautomation = pd.DataFrame(
        pds_tam_per_region_buildingautomation_list[1:],
        columns=pds_tam_per_region_buildingautomation_list[0], dtype=np.float64).set_index('Year')
    pds_tam_per_region_buildingautomation.index = pds_tam_per_region_buildingautomation.index.astype(
        int)
    # This test uses regional data, and hits the TAM limit in the OECD90 region. The TAM
    # limit has to be applied before the regions are summed to get the World number. If the
    # sum is taken first and then the TAM limit applied, the test will fail.
    expected = pd.DataFrame(soln_pds_funits_adopted_buildingautomation_linear_list[1:],
                            columns=soln_pds_funits_adopted_buildingautomation_linear_list[0]).set_index('Year')
    expected.name = 'soln_ref_funits_adopted'
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region_buildingautomation,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_pds_funits_adopted()
    pd.testing.assert_frame_equal(result.loc[2014:], expected, check_exact=False)


def test_soln_pds_funits_adopted_s_curve():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_basis='Logistic S-Curve')
    pds_datapoints = pd.DataFrame([
        [2014, 20.30881991465230, 0.0, 0.0, 25.04194984517460, 5.33726613132968, 36.92512711754970,
         0.0, 0.0, 0.0, 0.0],
        [2050, 1620.90420924928000, 0.0, 0.0, 1005.17634180055000, 752.46582309962500,
         39.65480026979520, 187.87596664323300, 463.99033134231300, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_adoption_trend_per_region = pd.DataFrame(pds_adoption_trend_per_region_list[1:],
                                                 columns=pds_adoption_trend_per_region_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_adoption_trend_per_region.index = pds_adoption_trend_per_region.index.astype(int)
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=None,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=False)
    expected = pds_adoption_trend_per_region.copy(deep=True)
    expected.name = 'soln_ref_funits_adopted'
    expected.index.name = 'Year'
    result = ht.soln_pds_funits_adopted()
    pd.testing.assert_frame_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)
    # ensure that pds_adoption_is_single_source has no effect on S-Curve interpolation.
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=None, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=None, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=None,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=True)
    result = ht.soln_pds_funits_adopted()
    pd.testing.assert_frame_equal(result.loc[2015:], expected.loc[2015:], check_exact=False)


def test_ref_adoption_use_pds_years_and_vice_versa():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_regional_data=False,
                                            soln_pds_adoption_basis='Existing Adoption Prognostications',
                                            ref_adoption_use_pds_years=range(2030, 2040),
                                            pds_adoption_use_ref_years=range(2020, 2030))
    ref_datapoints = pd.DataFrame([
        [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778,
         14.65061888889, 14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
        [2050, 272.41409799109, 97.40188603589, 0.52311962553, 60.19386560477, 6.43555351544,
         42.24551570326, 31.56519386433, 14.33357622563, 72.82702319498, 16.41524405748]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_datapoints = pd.DataFrame([
        [2014, 112.633033, 75.0042456, 0.332383, 21.072504, 1.575078, 14.650619,
         14.972222, 2.748301, 55.272054, 13.12465],
        [2050, 2603.660640, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    pds_adoption_data_per_region = pd.DataFrame(adoption_data_med_single_source_list[1:],
                                                columns=adoption_data_med_single_source_list[0],
                                                dtype=np.float64).set_index('Year')
    pds_adoption_data_per_region.index = pds_adoption_data_per_region.index.astype(int)
    pds_adoption_trend_per_region = pd.DataFrame(pds_adoption_trend_per_region_list[1:],
                                                 columns=pds_adoption_trend_per_region_list[0],
                                                 dtype=np.float64).set_index('Year')
    pds_adoption_trend_per_region.index = pds_adoption_trend_per_region.index.astype(int)
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=pds_datapoints,
                                   ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
                                   pds_adoption_data_per_region=pds_adoption_data_per_region,
                                   pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                   pds_adoption_is_single_source=True)
    ref_expected = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                columns=soln_ref_funits_adopted_list[0]).set_index('Year')
    ref_expected.name = 'soln_ref_funits_adopted'
    pds_expected = pd.DataFrame(soln_pds_funits_adopted_single_source_list[1:],
                                columns=soln_pds_funits_adopted_single_source_list[0]).set_index(
        'Year')
    pds_expected.name = 'soln_pds_funits_adopted'
    ref_result = ht.soln_ref_funits_adopted()
    pds_result = ht.soln_pds_funits_adopted()
    pd.testing.assert_series_equal(ref_result.loc[2030:2039, 'World'],
                                   pds_expected.loc[2030:2039, 'World'], check_exact=False)
    pd.testing.assert_frame_equal(ref_result.loc[2040:], ref_expected.loc[2040:], check_exact=False)
    pd.testing.assert_series_equal(pds_result.loc[2020:2029, 'World'],
                                   ref_expected.loc[2020:2029, 'World'], check_exact=False)
    pd.testing.assert_frame_equal(pds_result.loc[2040:], pds_expected.loc[2040:], check_exact=False)


def test_soln_ref_funits_adopted_regional_sums_buildingautomation():
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_basis='Default',
                                            soln_ref_adoption_regional_data=True)
    # from BuildingAutomation
    ref_datapoints = pd.DataFrame([
        [2014, 16577.8259167003, 14915.99, 0.0, 1087.7709445217, 0.0, 0.0,
         1087.7709445217, 0.0, 3622.85, 11293.14],
        [2050, 27052.2053117447, 20716.9426918730, 0.0, 1880.4218737321, 0.0, 0.0,
         1607.8783882761, 0.0, 5310.2548457406, 16434.9745506529]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    ref_tam_per_region_buildingautomation = pd.DataFrame(
        ref_tam_per_region_buildingautomation_list[1:],
        columns=ref_tam_per_region_buildingautomation_list[0]).set_index('Year')
    ref_tam_per_region_buildingautomation.name = 'ref_tam_per_region'
    ht = helpertables.HelperTables(ac=ac, ref_datapoints=ref_datapoints, pds_datapoints=None,
                                   ref_adoption_limits=ref_tam_per_region_buildingautomation, pds_adoption_limits=None,
                                   pds_adoption_data_per_region=None, pds_adoption_trend_per_region=None,
                                   pds_adoption_is_single_source=False)
    result = ht.soln_ref_funits_adopted()
    expected = pd.DataFrame(soln_ref_funits_adopted_buildingautomation_list[1:],
                            columns=soln_ref_funits_adopted_buildingautomation_list[0]).set_index('Year')
    expected.name = 'soln_ref_funits_adopted'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_use_first_pds_datapoint():
    datadir = pathlib.Path(__file__).parents[0].joinpath('data')
    custom_scen = pd.read_csv(datadir.joinpath('ca_scenario_1_trr.csv'), index_col=0)
    ac = advanced_controls.AdvancedControls(soln_pds_adoption_basis='Fully Customized PDS')
    regions = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
            'Latin America', 'China', 'India', 'EU', 'USA']
    ht_ref_datapoints = pd.DataFrame([[2014] + [1000] * 10, [2050] + [0] * 10],
            columns=['Year'] + regions).set_index('Year')
    ht_pds_datapoints = ht_ref_datapoints
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=custom_scen,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            use_first_pds_datapoint_main=True)
    for region in regions:
        assert int(ht.soln_pds_funits_adopted().loc[2014, region]) == 1000
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=custom_scen,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            use_first_pds_datapoint_main=False)
    assert int(ht.soln_pds_funits_adopted().loc[2014, regions[0]]) != 1000
    for region in regions[1:]:
        assert int(ht.soln_pds_funits_adopted().loc[2014, region]) == 1000


def test_soln_use_first_pds_datapoint_not_2014():
    datadir = pathlib.Path(__file__).parents[0].joinpath('data')
    custom_scen = pd.read_csv(datadir.joinpath('ca_scenario_1_trr.csv'), index_col=0)
    ac = advanced_controls.AdvancedControls(soln_pds_adoption_basis='Fully Customized PDS')
    regions = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
            'Latin America', 'China', 'India', 'EU', 'USA']
    ht_ref_datapoints = pd.DataFrame([[2020] + [1000] * 10, [2050] + [0] * 10],
            columns=['Year'] + regions).set_index('Year')
    ht_pds_datapoints = ht_ref_datapoints
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=custom_scen,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            use_first_pds_datapoint_main=True)
    result = ht.soln_pds_funits_adopted()
    for region in regions:
        assert int(result.loc[2020, region]) == 1000
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=custom_scen,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            use_first_pds_datapoint_main=False)
    result = ht.soln_pds_funits_adopted()
    assert int(result.loc[2020, regions[0]]) != 1000
    for region in regions[1:]:
        assert int(result.loc[2020, region]) == 1000


def test_copy_ref_datapoint():
    datadir = pathlib.Path(__file__).parents[0].joinpath('data')
    custom_scen = pd.read_csv(datadir.joinpath('ca_scenario_1_trr.csv'), index_col=0).fillna(1.3)
    ac = advanced_controls.AdvancedControls(soln_ref_adoption_basis='Custom')
    regions = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
            'Latin America', 'China', 'India', 'EU', 'USA']
    ht_ref_datapoints = pd.DataFrame([[2014] + [1000] * 10, [2050] + [0] * 10],
            columns=['Year'] + regions).set_index('Year')
    ht_pds_datapoints = ht_ref_datapoints
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=None,
            ref_adoption_data_per_region=custom_scen, copy_ref_datapoint=True,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints)
    for region in regions:
        assert int(ht.soln_ref_funits_adopted().loc[2014, region]) == 1000
    ht = helpertables.HelperTables(ac, pds_adoption_data_per_region=None,
            ref_adoption_data_per_region=custom_scen, copy_ref_datapoint=False,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints)
    for region in regions:
        assert int(ht.soln_ref_funits_adopted().loc[2014, region]) != 1000


soln_ref_funits_adopted_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778, 14.65061888889,
     14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
    [2015, 117.07139624049, 75.62640223557, 0.33768156367, 22.15920892112, 1.71009099271, 15.41714380040,
     15.43313810117, 3.07011430874, 55.75969246529, 13.21605539049],
    [2016, 121.50975914765, 76.24855891557, 0.34297979401, 23.24591339780, 1.84510420765, 16.18366871191,
     15.89405398012, 3.39192750636, 56.24733048614, 13.30746078097],
    [2017, 125.94812205481, 76.87071559558, 0.34827802435, 24.33261787447, 1.98011742258, 16.95019362342,
     16.35496985906, 3.71374070399, 56.73496850699, 13.39886617146],
    [2018, 130.38648496197, 77.49287227559, 0.35357625469, 25.41932235115, 2.11513063752, 17.71671853493,
     16.81588573801, 4.03555390161, 57.22260652784, 13.49027156194],
    [2019, 134.82484786913, 78.11502895560, 0.35887448503, 26.50602682782, 2.25014385245, 18.48324344644,
     17.27680161696, 4.35736709924, 57.71024454869, 13.58167695243],
    [2020, 139.26321077629, 78.73718563561, 0.36417271537, 27.59273130450, 2.38515706739, 19.24976835795,
     17.73771749591, 4.67918029686, 58.19788256953, 13.67308234291],
    [2021, 143.70157368345, 79.35934231562, 0.36947094570, 28.67943578117, 2.52017028232, 20.01629326946,
     18.19863337485, 5.00099349449, 58.68552059038, 13.76448773340],
    [2022, 148.13993659061, 79.98149899563, 0.37476917604, 29.76614025785, 2.65518349726, 20.78281818097,
     18.65954925380, 5.32280669212, 59.17315861123, 13.85589312388],
    [2023, 152.57829949777, 80.60365567564, 0.38006740638, 30.85284473453, 2.79019671219, 21.54934309248,
     19.12046513275, 5.64461988974, 59.66079663208, 13.94729851437],
    [2024, 157.01666240493, 81.22581235565, 0.38536563672, 31.93954921120, 2.92520992713, 22.31586800399,
     19.58138101170, 5.96643308737, 60.14843465293, 14.03870390485],
    [2025, 161.45502531209, 81.84796903566, 0.39066386706, 33.02625368788, 3.06022314206, 23.08239291550,
     20.04229689064, 6.28824628499, 60.63607267378, 14.13010929534],
    [2026, 165.89338821925, 82.47012571567, 0.39596209740, 34.11295816455, 3.19523635700, 23.84891782701,
     20.50321276959, 6.61005948262, 61.12371069462, 14.22151468583],
    [2027, 170.33175112641, 83.09228239568, 0.40126032774, 35.19966264123, 3.33024957193, 24.61544273852,
     20.96412864854, 6.93187268024, 61.61134871547, 14.31292007631],
    [2028, 174.77011403357, 83.71443907569, 0.40655855808, 36.28636711790, 3.46526278687, 25.38196765003,
     21.42504452749, 7.25368587787, 62.09898673632, 14.40432546680],
    [2029, 179.20847694073, 84.33659575570, 0.41185678841, 37.37307159458, 3.60027600180, 26.14849256154,
     21.88596040643, 7.57549907549, 62.58662475717, 14.49573085728],
    [2030, 183.64683984789, 84.95875243571, 0.41715501875, 38.45977607125, 3.73528921674, 26.91501747306,
     22.34687628538, 7.89731227312, 63.07426277802, 14.58713624777],
    [2031, 188.08520275505, 85.58090911572, 0.42245324909, 39.54648054793, 3.87030243167, 27.68154238457,
     22.80779216433, 8.21912547074, 63.56190079887, 14.67854163825],
    [2032, 192.52356566221, 86.20306579573, 0.42775147943, 40.63318502461, 4.00531564661, 28.44806729608,
     23.26870804327, 8.54093866837, 64.04953881971, 14.76994702874],
    [2033, 196.96192856937, 86.82522247573, 0.43304970977, 41.71988950128, 4.14032886154, 29.21459220759,
     23.72962392222, 8.86275186600, 64.53717684056, 14.86135241922],
    [2034, 201.40029147653, 87.44737915574, 0.43834794011, 42.80659397796, 4.27534207648, 29.98111711910,
     24.19053980117, 9.18456506362, 65.02481486141, 14.95275780971],
    [2035, 205.83865438369, 88.06953583575, 0.44364617045, 43.89329845463, 4.41035529141, 30.74764203061,
     24.65145568012, 9.50637826125, 65.51245288226, 15.04416320019],
    [2036, 210.27701729085, 88.69169251576, 0.44894440079, 44.98000293131, 4.54536850635, 31.51416694212,
     25.11237155906, 9.82819145887, 66.00009090311, 15.13556859068],
    [2037, 214.71538019801, 89.31384919577, 0.45424263112, 46.06670740798, 4.68038172128, 32.28069185363,
     25.57328743801, 10.15000465650, 66.48772892395, 15.22697398117],
    [2038, 219.15374310517, 89.93600587578, 0.45954086146, 47.15341188466, 4.81539493622, 33.04721676514,
     26.03420331696, 10.47181785412, 66.97536694480, 15.31837937165],
    [2039, 223.59210601233, 90.55816255579, 0.46483909180, 48.24011636133, 4.95040815115, 33.81374167665,
     26.49511919591, 10.79363105175, 67.46300496565, 15.40978476214],
    [2040, 228.03046891949, 91.18031923580, 0.47013732214, 49.32682083801, 5.08542136609, 34.58026658816,
     26.95603507485, 11.11544424937, 67.95064298650, 15.50119015262],
    [2041, 232.46883182665, 91.80247591581, 0.47543555248, 50.41352531469, 5.22043458102, 35.34679149967,
     27.41695095380, 11.43725744700, 68.43828100735, 15.59259554311],
    [2042, 236.90719473381, 92.42463259582, 0.48073378282, 51.50022979136, 5.35544779596, 36.11331641118,
     27.87786683275, 11.75907064462, 68.92591902820, 15.68400093359],
    [2043, 241.34555764097, 93.04678927583, 0.48603201316, 52.58693426804, 5.49046101089, 36.87984132269,
     28.33878271170, 12.08088384225, 69.41355704904, 15.77540632408],
    [2044, 245.78392054813, 93.66894595584, 0.49133024350, 53.67363874471, 5.62547422583, 37.64636623420,
     28.79969859064, 12.40269703988, 69.90119506989, 15.86681171456],
    [2045, 250.22228345529, 94.29110263585, 0.49662847384, 54.76034322139, 5.76048744076, 38.41289114571,
     29.26061446959, 12.72451023750, 70.38883309074, 15.95821710505],
    [2046, 254.66064636245, 94.91325931586, 0.50192670417, 55.84704769806, 5.89550065570, 39.17941605722,
     29.72153034854, 13.04632343513, 70.87647111159, 16.04962249553],
    [2047, 259.09900926961, 95.53541599587, 0.50722493451, 56.93375217474, 6.03051387063, 39.94594096873,
     30.18244622749, 13.36813663275, 71.36410913244, 16.14102788602],
    [2048, 263.53737217677, 96.15757267588, 0.51252316485, 58.02045665141, 6.16552708557, 40.71246588024,
     30.64336210643, 13.68994983038, 71.85174715329, 16.23243327651],
    [2049, 267.97573508393, 96.77972935589, 0.51782139519, 59.10716112809, 6.30054030050, 41.47899079175,
     31.10427798538, 14.01176302800, 72.33938517413, 16.32383866699],
    [2050, 272.41409799109, 97.40188603589, 0.52311962553, 60.19386560477, 6.43555351544, 42.24551570326,
     31.56519386433, 14.33357622563, 72.82702319498, 16.41524405748],
    [2051, 276.85246089825, 98.02404271590, 0.52841785587, 61.28057008144, 6.57056673037, 43.01204061477,
     32.02610974327, 14.65538942325, 73.31466121583, 16.50664944796],
    [2052, 281.29082380541, 98.64619939591, 0.53371608621, 62.36727455812, 6.70557994531, 43.77856552628,
     32.48702562222, 14.97720262088, 73.80229923668, 16.59805483845],
    [2053, 285.72918671257, 99.26835607592, 0.53901431655, 63.45397903479, 6.84059316024, 44.54509043779,
     32.94794150117, 15.29901581851, 74.28993725753, 16.68946022893],
    [2054, 290.16754961973, 99.89051275593, 0.54431254688, 64.54068351147, 6.97560637518, 45.31161534930,
     33.40885738012, 15.62082901613, 74.77757527838, 16.78086561942],
    [2055, 294.60591252689, 100.51266943594, 0.54961077722, 65.62738798814, 7.11061959011, 46.07814026081,
     33.86977325906, 15.94264221376, 75.26521329922, 16.87227100990],
    [2056, 299.04427543405, 101.13482611595, 0.55490900756, 66.71409246482, 7.24563280505, 46.84466517233,
     34.33068913801, 16.26445541138, 75.75285132007, 16.96367640039],
    [2057, 303.48263834121, 101.75698279596, 0.56020723790, 67.80079694150, 7.38064601998, 47.61119008384,
     34.79160501696, 16.58626860901, 76.24048934092, 17.05508179088],
    [2058, 307.92100124837, 102.37913947597, 0.56550546824, 68.88750141817, 7.51565923492, 48.37771499535,
     35.25252089591, 16.90808180663, 76.72812736177, 17.14648718136],
    [2059, 312.35936415553, 103.00129615598, 0.57080369858, 69.97420589485, 7.65067244985, 49.14423990686,
     35.71343677485, 17.22989500426, 77.21576538262, 17.23789257185],
    [2060, 316.79772706269, 103.62345283599, 0.57610192892, 71.06091037152, 7.78568566479, 49.91076481837,
     36.17435265380, 17.55170820188, 77.70340340347, 17.32929796233]]

# SolarPVUtil "Helper Tables"!B90:L137
soln_pds_funits_adopted_single_source_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778, 14.65061888889,
     14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
    [2015, 176.24092107213, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 272.03135207741, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 383.30935172620, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 509.37947394851, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 649.54627267436, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 654.00000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 969.38811535670, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 1147.67226717322, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 1337.27131121334, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 1537.48980140706, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 1595.40000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 1967.00333597537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 2194.90748820999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 2430.64930231826, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 2673.53333223022, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 3040.20000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 3177.94625518520, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 3438.08425608826, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 3702.58268851506, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 3970.74610639560, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 4241.87906365990, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 4515.28611423798, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 4790.27181205984, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 5066.14071105551, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 5342.19736515499, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 5665.20000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 5892.09215438547, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 6164.53939737649, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 6434.39261119138, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 6700.95634976017, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 6963.53516701285, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 7221.43361687946, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 7473.95625328999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 7720.40763017447, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 7960.09230146291, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 8167.80000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 8416.37974297171, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 8631.59162105212, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 8837.25500925653, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 9032.67446151498, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 9217.15453175747, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 9389.99977391402, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 9550.51474191465, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 9698.00398968936, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 9831.77207116817, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 9951.12354028110, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil 'Adoption Data'!AB46:AD94
adoption_data_med_single_source_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
     'Latin America', 'China', 'India', 'EU', 'USA'],
    [2012, 58.200000, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2013, 81.060000, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2014, 112.633033, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2015, 176.240921, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2016, 272.031352, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2017, 383.309352, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2018, 509.379474, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2019, 649.546273, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2020, 654.000000, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2021, 969.388115, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2022, 1147.672267, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2023, 1337.271311, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2024, 1537.489801, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2025, 1595.400000, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2026, 1967.003336, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2027, 2194.907488, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2028, 2430.649302, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2029, 2673.533332, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2030, 3040.200000, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2031, 3177.946255, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2032, 3438.084256, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2033, 3702.582689, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2034, 3970.746106, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2035, 4241.879064, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2036, 4515.286114, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2037, 4790.271812, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2038, 5066.140711, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2039, 5342.197365, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2040, 5665.200000, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2041, 5892.092154, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2042, 6164.539397, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2043, 6434.392611, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2044, 6700.956350, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2045, 6963.535167, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2046, 7221.433617, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2047, 7473.956253, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2048, 7720.407630, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2049, 7960.092301, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2050, 8167.800000, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2051, 8416.379743, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2052, 8631.591621, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2053, 8837.255009, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2054, 9032.674462, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2055, 9217.154532, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2056, 9389.999774, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2057, 9550.514742, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2058, 9698.003990, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2059, 9831.772071, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0],

    [2060, 9951.123540, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0,
     10000.0]]

# SolarPVUtil 'Adoption Data'!AB46:AD94 with 'Advanced Controls'!$B$265 set to ALL SOURCES, Low growth
adoption_data_low_all_sources_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
     'Latin America', 'China', 'India', 'EU', 'USA'],
    [2012, 58.200000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2013, 81.060000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2014, 112.633033, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 105.603550, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 127.118631, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 145.350020, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 161.744158, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 177.256713, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 233.704628, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 207.789889, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 223.508399, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 239.889454, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 257.159907, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 306.997867, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 295.179590, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 316.304602, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 339.080224, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 363.664416, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 345.183977, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 418.893521, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 449.820470, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 483.134195, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 518.953374, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 537.792556, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 598.513116, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 642.433505, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 689.205335, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 738.875230, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 779.316063, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 847.028954, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 905.512113, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 966.891116, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 1031.106475, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 1119.474313, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 1167.661392, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 1239.739315, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 1314.126484, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 1390.607087, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 1473.209246, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 1541.533750, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 1629.989194, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 1712.033415, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 1794.576241, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 1877.190347, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 1959.419848, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 2040.782840, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 2120.769468, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 2198.847801, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 2274.465696, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil 'Adoption Data'!AB46:AD94 with 'Advanced Controls'!$B$265 set to ALL SOURCES, Medium growth
adoption_data_med_all_sources_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
     'Latin America', 'China', 'India', 'EU', 'USA'],
    [2012, 58.200000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2013, 81.060000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2014, 112.633033, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 143.440773, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 178.031388, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 216.277581, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 258.148941, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 303.617671, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 387.218033, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 405.231407, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 461.326773, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 520.907669, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 583.948981, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 637.237725, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 720.320695, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 793.599762, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 870.234174, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 950.207503, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 1024.344206, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 1120.054476, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 1209.884314, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 1302.950343, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 1399.230459, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 1485.099716, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 1601.357356, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 1707.151977, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 1816.073964, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 1928.107209, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 2049.673002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 2161.406520, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 2282.630807, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 2406.877717, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 2534.119318, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 2680.827286, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 2797.495015, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 2933.582846, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 3072.566724, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 3214.429763, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 3356.568167, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 3500.574665, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 3657.001693, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 3810.097659, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 3965.920268, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 4124.434577, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 4285.613883, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 4449.423870, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 4615.843091, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 4784.848984, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 4956.419760, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil 'Adoption Data'!AB46:AD94 with 'Advanced Controls'!$B$265 set to ALL SOURCES, High growth
adoption_data_high_all_sources_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
     'Latin America', 'China', 'India', 'EU', 'USA'],
    [2012, 58.200000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2013, 81.060000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2014, 112.633033, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 181.277995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 228.944145, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 287.205142, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 354.553723, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 429.978630, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 540.731439, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 602.672926, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 699.145147, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 801.925884, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 910.738056, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 967.477582, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 1145.461801, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 1270.894921, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 1401.388125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 1536.750591, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 1703.504435, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 1821.215430, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 1969.948158, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 2122.766492, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 2279.507544, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 2432.406876, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 2604.201597, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 2771.870450, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 2942.942594, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 3117.339187, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 3320.029942, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 3475.784087, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 3659.749502, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 3846.864319, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 4037.132161, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 4242.180259, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 4427.328638, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 4627.426377, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 4831.006965, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 5038.252438, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 5239.927088, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 5459.615581, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 5684.014191, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 5908.161903, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 6137.264295, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 6371.678808, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 6611.807918, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 6858.064901, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 7110.916715, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 7370.850167, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 7638.373825, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

pds_adoption_trend_per_region_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
     'Latin America', 'China', 'India', 'EU', 'USA'],
    [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778,
     14.65061888889, 14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
    [2015, 165.44445404443, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 233.39381751948, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 306.49853116153, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 384.72127326918, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 468.02472214098, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 556.37155607553, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 649.72445337140, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 748.04609232716, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 851.29915124140, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 959.44630841268, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 1072.45024213959, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 1190.27363072071, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 1312.87915245461, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 1440.22948563987, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 1572.28730857506, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 1709.01529955877, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 1850.37613688956, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 1996.33249886602, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 2146.84706378673, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 2301.88250995026, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 2461.40151565519, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 2625.36675920009, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 2793.74091888354, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 2966.48667300413, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 3143.56669986042, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 3324.94367775100, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 3510.58028497444, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 3700.43919982931, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 3894.48310061420, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 4092.67466562769, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 4294.97657316834, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 4501.35150153474, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 4711.76212902547, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 4926.17113393909, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 5144.54119457420, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 5366.83498922936, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 5593.01519620315, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 5823.04449379415, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 6056.88556030095, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 6294.50107402210, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 6535.85371325619, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 6780.90615630181, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 7029.62108145751, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 7281.96116702190, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 7537.88909129353, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 7797.36753257098, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# ImprovedCookStoves 'Unit Adoption Calculations'!A68:K115
pds_tam_per_region_cookstoves_list = [
    ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
     'Latin America', 'China', 'India', 'EU', 'USA'],
    [2014, 5827.235387, 0.0, 0.0, 4053.298731, 1783.757754, 173.254108, 1086.492157, 1622.370389, 0.0, 0.0],

    [2015, 5194.547540, 0.0, 0.0, 4063.458970, 1813.714359, 173.110086, 1083.167749, 1629.340849, 0.0, 0.0],

    [2016, 5159.098296, 0.0, 0.0, 4072.722322, 1846.401375, 173.132753, 1079.291643, 1640.767842, 0.0, 0.0],

    [2017, 5132.187372, 0.0, 0.0, 4081.370608, 1879.220242, 173.127819, 1074.656400, 1651.913008, 0.0, 0.0],

    [2018, 5113.425079, 0.0, 0.0, 4089.403674, 1912.166934, 173.095459, 1069.301088, 1662.775487, 0.0, 0.0],

    [2019, 5102.421730, 0.0, 0.0, 4096.821366, 1945.237426, 173.035847, 1063.264772, 1673.354415, 0.0, 0.0],

    [2020, 5098.787637, 0.0, 0.0, 4103.623531, 1978.427692, 172.949155, 1056.586516, 1683.648933, 0.0, 0.0],

    [2021, 5102.133112, 0.0, 0.0, 4109.810015, 2011.733707, 172.835559, 1049.305389, 1693.658179, 0.0, 0.0],

    [2022, 5112.068467, 0.0, 0.0, 4115.380664, 2045.151444, 172.695231, 1041.460454, 1703.381292, 0.0, 0.0],

    [2023, 5128.204014, 0.0, 0.0, 4120.335323, 2078.676878, 172.528346, 1033.090778, 1712.817409, 0.0, 0.0],

    [2024, 5150.150065, 0.0, 0.0, 4124.673841, 2112.305984, 172.335078, 1024.235427, 1721.965671, 0.0, 0.0],

    [2025, 5177.516933, 0.0, 0.0, 4128.396061, 2146.034735, 172.115601, 1014.933467, 1730.825215, 0.0, 0.0],

    [2026, 5209.914930, 0.0, 0.0, 4131.501832, 2179.859107, 171.870088, 1005.223962, 1739.395180, 0.0, 0.0],

    [2027, 5246.954367, 0.0, 0.0, 4133.990998, 2213.775072, 171.598714, 995.145980, 1747.674706, 0.0, 0.0],

    [2028, 5288.245556, 0.0, 0.0, 4135.863407, 2247.778607, 171.301651, 984.738586, 1755.662930, 0.0, 0.0],

    [2029, 5333.398810, 0.0, 0.0, 4137.118904, 2281.865684, 170.979075, 974.040846, 1763.358992, 0.0, 0.0],

    [2030, 5382.024442, 0.0, 0.0, 4137.757336, 2316.032279, 170.631159, 963.091825, 1770.762029, 0.0, 0.0],

    [2031, 5433.732762, 0.0, 0.0, 4137.778548, 2350.274365, 170.258076, 951.930590, 1777.871181, 0.0, 0.0],

    [2032, 5488.134083, 0.0, 0.0, 4137.182387, 2384.587918, 169.860002, 940.596206, 1784.685587, 0.0, 0.0],

    [2033, 5544.838717, 0.0, 0.0, 4135.968699, 2418.968910, 169.437109, 929.127739, 1791.204385, 0.0, 0.0],

    [2034, 5603.456977, 0.0, 0.0, 4134.137331, 2453.413318, 168.989571, 917.564254, 1797.426713, 0.0, 0.0],

    [2035, 5663.599174, 0.0, 0.0, 4131.688128, 2487.917114, 168.517563, 905.944819, 1803.351712, 0.0, 0.0],

    [2036, 5724.875621, 0.0, 0.0, 4128.620937, 2522.476274, 168.021258, 894.308497, 1808.978518, 0.0, 0.0],

    [2037, 5786.896628, 0.0, 0.0, 4124.935604, 2557.086772, 167.500830, 882.694356, 1814.306271, 0.0, 0.0],

    [2038, 5849.272510, 0.0, 0.0, 4120.631976, 2591.744581, 166.956453, 871.141461, 1819.334109, 0.0, 0.0],

    [2039, 5911.613577, 0.0, 0.0, 4115.709897, 2626.445677, 166.388301, 859.688878, 1824.061172, 0.0, 0.0],

    [2040, 5973.530143, 0.0, 0.0, 4110.169215, 2661.186034, 165.796548, 848.375673, 1828.486598, 0.0, 0.0],

    [2041, 6034.632518, 0.0, 0.0, 4104.009776, 2695.961626, 165.181368, 837.240910, 1832.609525, 0.0, 0.0],

    [2042, 6094.531015, 0.0, 0.0, 4097.231425, 2730.768427, 164.542934, 826.323658, 1836.429093, 0.0, 0.0],

    [2043, 6152.835946, 0.0, 0.0, 4089.834010, 2765.602412, 163.881420, 815.662980, 1839.944439, 0.0, 0.0],

    [2044, 6209.157624, 0.0, 0.0, 4081.817376, 2800.459554, 163.197001, 805.297943, 1843.154704, 0.0, 0.0],

    [2045, 6263.106360, 0.0, 0.0, 4073.181370, 2835.335830, 162.489849, 795.267613, 1846.059024, 0.0, 0.0],

    [2046, 6314.292466, 0.0, 0.0, 4063.925837, 2870.227211, 161.760140, 785.611056, 1848.656540, 0.0, 0.0],

    [2047, 6362.326255, 0.0, 0.0, 4054.050624, 2905.129674, 161.008047, 776.367336, 1850.946389, 0.0, 0.0],

    [2048, 6406.818038, 0.0, 0.0, 4043.555577, 2940.039192, 160.233743, 767.575521, 1852.927710, 0.0, 0.0],

    [2049, 6447.378128, 0.0, 0.0, 4032.440543, 2974.951740, 159.437403, 759.274676, 1854.599643, 0.0, 0.0],

    [2050, 6483.616837, 0.0, 0.0, 4020.705367, 3009.863292, 158.619201, 751.503867, 1855.961325, 0.0, 0.0],

    [2051, 6515.144477, 0.0, 0.0, 4008.349896, 3044.769823, 157.779310, 744.302159, 1857.011896, 0.0, 0.0],

    [2052, 6541.571360, 0.0, 0.0, 3995.373976, 3079.667306, 156.917904, 737.708618, 1857.750494, 0.0, 0.0],

    [2053, 6562.507797, 0.0, 0.0, 3981.777453, 3114.551716, 156.035158, 731.762311, 1858.176258, 0.0, 0.0],

    [2054, 6577.564103, 0.0, 0.0, 3967.560173, 3149.419027, 155.131245, 726.502302, 1858.288326, 0.0, 0.0],

    [2055, 6586.350587, 0.0, 0.0, 3952.721983, 3184.265214, 154.206338, 721.967659, 1858.085838, 0.0, 0.0],

    [2056, 6588.477563, 0.0, 0.0, 3937.262728, 3219.086252, 153.260612, 718.197446, 1857.567931, 0.0, 0.0],

    [2057, 6583.555342, 0.0, 0.0, 3921.182255, 3253.878113, 152.294241, 715.230729, 1856.733745, 0.0, 0.0],

    [2058, 6571.194237, 0.0, 0.0, 3904.480411, 3288.636773, 151.307399, 713.106575, 1855.582418, 0.0, 0.0],

    [2059, 6551.004559, 0.0, 0.0, 3887.157041, 3323.358207, 150.300259, 711.864048, 1854.113089, 0.0, 0.0],

    [2060, 6522.596622, 0.0, 0.0, 3869.211991, 3358.038387, 149.272995, 711.542216, 1852.324897, 0.0,
     0.0]]

# ImprovedCookStoves "Helper Tables"!B90:L137
soln_pds_funits_adopted_cookstoves_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 20.308820, 0.0, 0.0, 25.041950, 5.337266, 36.925127, 0.0, 0.0, 0.0, 0.0],
    [2015, 64.769803, 0.0, 0.0, 52.267905, 26.090837, 37.000951, 5.218777, 12.888620, 0.0, 0.0],
    [2016, 109.230786, 0.0, 0.0, 79.493861, 46.844408, 37.076776, 10.437554, 25.777241, 0.0, 0.0],
    [2017, 153.691769, 0.0, 0.0, 106.719816, 67.597979, 37.152600, 15.656331, 38.665861, 0.0, 0.0],
    [2018, 198.152752, 0.0, 0.0, 133.945771, 88.351550, 37.228424, 20.875107, 51.554481, 0.0, 0.0],
    [2019, 242.613735, 0.0, 0.0, 161.171727, 109.105121, 37.304248, 26.093884, 64.443102, 0.0, 0.0],
    [2020, 287.074718, 0.0, 0.0, 188.397682, 129.858692, 37.380073, 31.312661, 77.331722, 0.0, 0.0],
    [2021, 331.535701, 0.0, 0.0, 215.623637, 150.612263, 37.455897, 36.531438, 90.220342, 0.0, 0.0],
    [2022, 375.996684, 0.0, 0.0, 242.849593, 171.365834, 37.531721, 41.750215, 103.108963, 0.0, 0.0],

    [2023, 420.457667, 0.0, 0.0, 270.075548, 192.119405, 37.607545, 46.968992, 115.997583, 0.0, 0.0],

    [2024, 464.918650, 0.0, 0.0, 297.301503, 212.872976, 37.683370, 52.187769, 128.886203, 0.0, 0.0],

    [2025, 509.379633, 0.0, 0.0, 324.527458, 233.626547, 37.759194, 57.406545, 141.774823, 0.0, 0.0],

    [2026, 553.840616, 0.0, 0.0, 351.753414, 254.380118, 37.835018, 62.625322, 154.663444, 0.0, 0.0],

    [2027, 598.301599, 0.0, 0.0, 378.979369, 275.133689, 37.910842, 67.844099, 167.552064, 0.0, 0.0],

    [2028, 642.762582, 0.0, 0.0, 406.205324, 295.887261, 37.986667, 73.062876, 180.440684, 0.0, 0.0],

    [2029, 687.223565, 0.0, 0.0, 433.431280, 316.640832, 38.062491, 78.281653, 193.329305, 0.0, 0.0],

    [2030, 731.684549, 0.0, 0.0, 460.657235, 337.394403, 38.138315, 83.500430, 206.217925, 0.0, 0.0],

    [2031, 776.145532, 0.0, 0.0, 487.883190, 358.147974, 38.214139, 88.719206, 219.106545, 0.0, 0.0],

    [2032, 820.606515, 0.0, 0.0, 515.109146, 378.901545, 38.289964, 93.937983, 231.995166, 0.0, 0.0],

    [2033, 865.067498, 0.0, 0.0, 542.335101, 399.655116, 38.365788, 99.156760, 244.883786, 0.0, 0.0],

    [2034, 909.528481, 0.0, 0.0, 569.561056, 420.408687, 38.441612, 104.375537, 257.772406, 0.0, 0.0],

    [2035, 953.989464, 0.0, 0.0, 596.787012, 441.162258, 38.517436, 109.594314, 270.661027, 0.0, 0.0],

    [2036, 998.450447, 0.0, 0.0, 624.012967, 461.915829, 38.593261, 114.813091, 283.549647, 0.0, 0.0],

    [2037, 1042.911430, 0.0, 0.0, 651.238922, 482.669400, 38.669085, 120.031868, 296.438267, 0.0, 0.0],

    [2038, 1087.372413, 0.0, 0.0, 678.464878, 503.422971, 38.744909, 125.250644, 309.326888, 0.0, 0.0],

    [2039, 1131.833396, 0.0, 0.0, 705.690833, 524.176542, 38.820733, 130.469421, 322.215508, 0.0, 0.0],

    [2040, 1176.294379, 0.0, 0.0, 732.916788, 544.930113, 38.896558, 135.688198, 335.104128, 0.0, 0.0],

    [2041, 1220.755362, 0.0, 0.0, 760.142744, 565.683684, 38.972382, 140.906975, 347.992749, 0.0, 0.0],

    [2042, 1265.216345, 0.0, 0.0, 787.368699, 586.437255, 39.048206, 146.125752, 360.881369, 0.0, 0.0],

    [2043, 1309.677328, 0.0, 0.0, 814.594654, 607.190826, 39.124030, 151.344529, 373.769989, 0.0, 0.0],

    [2044, 1354.138311, 0.0, 0.0, 841.820610, 627.944397, 39.199855, 156.563306, 386.658609, 0.0, 0.0],

    [2045, 1398.599294, 0.0, 0.0, 869.046565, 648.697968, 39.275679, 161.782082, 399.547230, 0.0, 0.0],

    [2046, 1443.060277, 0.0, 0.0, 896.272520, 669.451539, 39.351503, 167.000859, 412.435850, 0.0, 0.0],

    [2047, 1487.521260, 0.0, 0.0, 923.498476, 690.205110, 39.427328, 172.219636, 425.324470, 0.0, 0.0],

    [2048, 1531.982243, 0.0, 0.0, 950.724431, 710.958681, 39.503152, 177.438413, 438.213091, 0.0, 0.0],

    [2049, 1576.443226, 0.0, 0.0, 977.950386, 731.712252, 39.578976, 182.657190, 451.101711, 0.0, 0.0],

    [2050, 1620.904209, 0.0, 0.0, 1005.176342, 752.465823, 39.654800, 187.875967, 463.990331, 0.0, 0.0],

    [2051, 1665.365192, 0.0, 0.0, 1032.402297, 773.219394, 39.730625, 193.094743, 476.878952, 0.0, 0.0],

    [2052, 1709.826175, 0.0, 0.0, 1059.628252, 793.972965, 39.806449, 198.313520, 489.767572, 0.0, 0.0],

    [2053, 1754.287158, 0.0, 0.0, 1086.854208, 814.726536, 39.882273, 203.532297, 502.656192, 0.0, 0.0],

    [2054, 1798.748141, 0.0, 0.0, 1114.080163, 835.480107, 39.958097, 208.751074, 515.544813, 0.0, 0.0],

    [2055, 1843.209124, 0.0, 0.0, 1141.306118, 856.233678, 40.033922, 213.969851, 528.433433, 0.0, 0.0],

    [2056, 1887.670107, 0.0, 0.0, 1168.532074, 876.987249, 40.109746, 219.188628, 541.322053, 0.0, 0.0],

    [2057, 1932.131091, 0.0, 0.0, 1195.758029, 897.740820, 40.185570, 224.407405, 554.210674, 0.0, 0.0],

    [2058, 1976.592074, 0.0, 0.0, 1222.983984, 918.494391, 40.261394, 229.626181, 567.099294, 0.0, 0.0],

    [2059, 2021.053057, 0.0, 0.0, 1250.209940, 939.247962, 40.337219, 234.844958, 579.987914, 0.0, 0.0],

    [2060, 2065.514040, 0.0, 0.0, 1277.435895, 960.001533, 40.413043, 240.063735, 592.876534, 0.0,
     0.0]]

# Insulation "Custom REF Adoption"!A22:K71
ref_adoption_data_per_region_insulation_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2012, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2013, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2014, 35739.109727, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 35739.109727, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 36597.985934, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 37501.594659, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 38450.768277, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 39446.355311, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 40489.220588, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 41591.191290, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 42746.000619, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 43954.624805, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 45218.059327, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 46537.319091, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 47913.438612, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 49347.472223, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 50840.494297, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 52349.849469, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 53913.469638, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 55536.473071, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 57216.315636, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 58954.034840, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 60750.687208, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 62607.348541, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 64525.114196, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 66505.099362, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 68548.439354, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 70656.289906, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 72829.827479, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 75073.755671, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 77385.997766, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 79767.789526, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 82220.388881, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 84745.076266, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 87343.154959, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 90015.951424, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 92764.815671, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 95591.121617, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 98496.267456, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 101477.504986, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 104535.374284, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 107670.258148, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 110882.345935, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 114171.590091, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 117537.653910, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 120980.682987, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 124500.744020, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 128097.840486, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 131771.938688, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

ref_tam_per_region_insulation_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 119130, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 122032, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 124929, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 127826, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 130721, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 133616, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 136511, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 139406, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 142300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 145195, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 148089, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 150985, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 153880, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 156777, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 159674, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 162572, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 165471, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 168372, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 171274, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 174177, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 177082, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 179989, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 182898, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 185809, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 188723, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 191639, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 194557, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 197479, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 200403, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 203330, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 206260, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 209194, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 212131, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 215072, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 218016, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 220964, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 223917, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 226874, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 229835, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 232800, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 235770, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 238745, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 241725, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 244710, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 247700, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 250696, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 253697, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

ref_tam_per_region_limit_seven_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2015, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2016, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2017, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2018, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2019, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2020, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2021, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2022, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2023, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2024, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2025, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2026, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2027, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2028, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2029, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2030, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2031, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2032, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2033, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2034, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2035, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2036, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2037, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2038, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2039, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2040, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2041, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2042, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2043, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2044, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2045, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2046, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2047, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2048, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2049, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2050, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2051, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2052, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2053, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2054, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2055, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2056, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2057, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2058, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2059, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
    [2060, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0]]

# Data from SolarHotWater "Unit Adoption Calculations"!A16:K63
ref_tam_per_region_solarhotwater_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 5687.521034, 2419.885387, 677.435403, 1448.504181, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2015, 6155.239436, 2432.209044, 682.287082, 1481.152775, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2016, 6211.582839, 2445.183832, 687.290808, 1516.556258, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2017, 6267.778451, 2458.493246, 692.316305, 1553.600666, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2018, 6323.826271, 2472.114079, 697.374515, 1592.265540, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2019, 6379.726299, 2486.023124, 702.476384, 1632.530422, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2020, 6408.192727, 2500.197175, 707.632853, 1674.374852, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2021, 6491.082981, 2514.613024, 712.854868, 1717.778371, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2022, 6546.539634, 2529.247466, 718.153372, 1762.720521, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2023, 6601.848496, 2544.077294, 723.539309, 1809.180843, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2024, 6657.009565, 2559.079301, 729.023621, 1857.138878, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2025, 6710.996002, 2574.230281, 734.617254, 1906.574168, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2026, 6766.888330, 2589.507026, 740.331150, 1957.466252, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2027, 6821.606024, 2604.886330, 746.176254, 2009.794673, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2028, 6876.175927, 2620.344987, 752.163509, 2063.538971, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2029, 6930.598038, 2635.859789, 758.303859, 2118.678688, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2030, 6964.992668, 2651.407531, 764.608247, 2175.193365, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2031, 7038.998885, 2666.965005, 771.087617, 2233.062543, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2032, 7092.977621, 2682.509005, 777.752914, 2292.265762, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2033, 7146.808565, 2698.016324, 784.615080, 2352.782565, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2034, 7200.491718, 2713.463755, 791.685059, 2414.592492, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2035, 7267.186449, 2728.828093, 798.973795, 2477.675085, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2036, 7307.414647, 2744.086130, 806.492232, 2542.009884, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2037, 7360.654425, 2759.214659, 814.251313, 2607.576431, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2038, 7413.746410, 2774.190474, 822.261982, 2674.354267, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2039, 7466.690604, 2788.990368, 830.535183, 2742.322933, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2040, 7543.715370, 2803.591135, 839.081860, 2811.461970, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2041, 7572.135617, 2817.969568, 847.912956, 2881.750919, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2042, 7624.636435, 2832.102460, 857.039414, 2953.169322, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2043, 7676.989462, 2845.966605, 866.472180, 3025.696719, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2044, 7729.194697, 2859.538795, 876.222195, 3099.312652, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2045, 7793.207865, 2872.795825, 886.300405, 3173.996661, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2046, 7833.161793, 2885.714488, 896.717752, 3249.728289, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2047, 7884.923653, 2898.271577, 907.485180, 3326.487075, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2048, 7936.537721, 2910.443885, 918.613634, 3404.252562, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2049, 7988.003998, 2922.208205, 930.114057, 3483.004290, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2050, 8018.106869, 2933.541332, 941.997392, 3562.721801, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2051, 8090.493176, 2944.420058, 954.274583, 3643.384635, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2052, 8141.516077, 2954.821177, 966.956574, 3724.972334, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2053, 8192.391187, 2964.721481, 980.054308, 3807.464439, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2054, 8243.118505, 2974.097766, 993.578730, 3890.840491, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2055, 8293.698031, 2982.926822, 1007.540783, 3975.080031, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2056, 8344.129765, 2991.185445, 1021.951411, 4060.162600, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2057, 8394.413708, 2998.850428, 1036.821557, 4146.067739, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2058, 8444.549859, 3005.898563, 1052.162165, 4232.774991, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2059, 8494.538219, 3012.306645, 1067.984179, 4320.263894, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2060, 8544.378786, 3018.051465, 1084.298542, 4408.513992, np.nan, np.nan, np.nan, np.nan, np.nan,
     np.nan]]

# Data from SolarHotWater "Helper Tables"!B26:L73
soln_ref_funits_adopted_solarhotwater_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 335.463000, 56.493000, 2.374000, 240.305000, 9.948000, 9.113000, 231.838000, 6.435000, 23.777000, 17.233000],

    [2015, 339.281425, 56.826096, 2.399754, 250.047945, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2016, 343.099849, 57.159192, 2.425507, 259.790890, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2017, 346.918274, 57.492289, 2.451261, 269.533834, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2018, 350.736698, 57.825385, 2.477014, 279.276779, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2019, 354.555123, 58.158481, 2.502768, 289.019724, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2020, 358.373547, 58.491577, 2.528522, 298.762669, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2021, 362.191972, 58.824673, 2.554275, 308.505613, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2022, 366.010396, 59.157769, 2.580029, 318.248558, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2023, 369.828821, 59.490866, 2.605782, 327.991503, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2024, 373.647245, 59.823962, 2.631536, 337.734448, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2025, 377.465670, 60.157058, 2.657289, 347.477393, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2026, 381.284094, 60.490154, 2.683043, 357.220337, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2027, 385.102519, 60.823250, 2.708797, 366.963282, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2028, 388.920944, 61.156347, 2.734550, 376.706227, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2029, 392.739368, 61.489443, 2.760304, 386.449172, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2030, 396.557793, 61.822539, 2.786057, 396.192117, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2031, 400.376217, 62.155635, 2.811811, 405.935061, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2032, 404.194642, 62.488731, 2.837565, 415.678006, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2033, 408.013066, 62.821828, 2.863318, 425.420951, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2034, 411.831491, 63.154924, 2.889072, 435.163896, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2035, 415.649915, 63.488020, 2.914825, 444.906840, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2036, 419.468340, 63.821116, 2.940579, 454.649785, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2037, 423.286764, 64.154212, 2.966333, 464.392730, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2038, 427.105189, 64.487308, 2.992086, 474.135675, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2039, 430.923614, 64.820405, 3.017840, 483.878620, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2040, 434.742038, 65.153501, 3.043593, 493.621564, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2041, 438.560463, 65.486597, 3.069347, 503.364509, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2042, 442.378887, 65.819693, 3.095101, 513.107454, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2043, 446.197312, 66.152789, 3.120854, 522.850399, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2044, 450.015736, 66.485886, 3.146608, 532.593344, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2045, 453.834161, 66.818982, 3.172361, 542.336288, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2046, 457.652585, 67.152078, 3.198115, 552.079233, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2047, 461.471010, 67.485174, 3.223868, 561.822178, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2048, 465.289434, 67.818270, 3.249622, 571.565123, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2049, 469.107859, 68.151366, 3.275376, 581.308067, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2050, 472.926283, 68.484463, 3.301129, 591.051012, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],

    [2051, 476.744708, 68.817559, 3.326883, 600.793957, -0.276333, -0.253139, -6.439944, -0.178750, -0.660472,
     -0.478694],
    [2052, 480.563133, 69.150655, 3.352636, 610.536902, -0.552667, -0.506278, -12.879889, -0.357500, -1.320944,
     -0.957389],
    [2053, 484.381557, 69.483751, 3.378390, 620.279847, -0.829000, -0.759417, -19.319833, -0.536250, -1.981417,
     -1.436083],
    [2054, 488.199982, 69.816847, 3.404144, 630.022791, -1.105333, -1.012556, -25.759778, -0.715000, -2.641889,
     -1.914778],
    [2055, 492.018406, 70.149944, 3.429897, 639.765736, -1.381667, -1.265694, -32.199722, -0.893750, -3.302361,
     -2.393472],
    [2056, 495.836831, 70.483040, 3.455651, 649.508681, -1.658000, -1.518833, -38.639667, -1.072500, -3.962833,
     -2.872167],
    [2057, 499.655255, 70.816136, 3.481404, 659.251626, -1.934333, -1.771972, -45.079611, -1.251250, -4.623306,
     -3.350861],
    [2058, 503.473680, 71.149232, 3.507158, 668.994570, -2.210667, -2.025111, -51.519556, -1.430000, -5.283778,
     -3.829556],
    [2059, 507.292104, 71.482328, 3.532912, 678.737515, -2.487000, -2.278250, -57.959500, -1.608750, -5.944250,
     -4.308250],
    [2060, 511.110529, 71.815425, 3.558665, 688.480460, -2.763333, -2.531389, -64.399444, -1.787500, -6.604722,
     -4.786944]]

# Data from BuildingAutomation "Unit Adoption Calculations"!A16:K63
ref_tam_per_region_buildingautomation_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 47780.340000, 22016.400000, 1079.360000, 14669.080000, 1849.480000, 771.320000, 12830.400000, 746.655422,
     7506.892755, 25341.720614],
    [2015, 48807.247557, 22292.887618, 1095.593698, 15020.021853, 1900.162097, 778.469482, 14733.555488, 908.917982,
     8626.261046, 25531.758439],
    [2016, 49863.872964, 22579.300538, 1111.741837, 15403.602940, 1955.583914, 785.023087, 15199.304907, 952.728405,
     8734.187018, 25840.113502],
    [2017, 50907.710733, 22862.775963, 1127.665888, 15782.005780, 2011.514837, 791.598185, 15633.357611, 1016.259541,
     8839.733364, 26149.441027],
    [2018, 51938.728615, 23143.315305, 1143.366592, 16155.229462, 2067.954533, 798.194974, 16036.751017, 1098.690631,
     8942.902460, 26459.737523],
    [2019, 52956.894362, 23420.919972, 1158.844690, 16523.273074, 2124.902668, 804.813653, 16410.522542, 1199.200916,
     9043.696686, 26770.999499],
    [2020, 53962.175724, 23695.591377, 1174.100923, 16886.135703, 2182.358909, 811.454420, 16755.709604, 1316.969636,
     9142.118420, 27083.223467],
    [2021, 54954.540454, 23967.330928, 1189.136032, 17243.816437, 2240.322923, 818.117473, 17073.349619, 1451.176030,
     9238.170040, 27396.405936],
    [2022, 55933.956303, 24236.140037, 1203.950758, 17596.314364, 2298.794375, 824.803012, 17364.480005, 1600.999340,
     9331.853923, 27710.543417],
    [2023, 56900.391023, 24502.020114, 1218.545841, 17943.628573, 2357.772932, 831.511234, 17630.138179, 1765.618806,
     9423.172449, 28025.632419],
    [2024, 57853.812366, 24764.972568, 1232.922022, 18285.758152, 2417.258261, 838.242339, 17871.361558, 1944.213668,
     9512.127995, 28341.669452],
    [2025, 58794.188082, 25024.998811, 1247.080043, 18622.702187, 2477.250028, 844.996524, 18089.187560, 2135.963166,
     9598.722940, 28658.651027],
    [2026, 59721.485923, 25282.100252, 1261.020643, 18954.459768, 2537.747900, 851.773988, 18284.653600, 2340.046541,
     9682.959663, 28976.573653],
    [2027, 60635.673642, 25536.278302, 1274.744565, 19281.029982, 2598.751543, 858.574930, 18458.797098, 2555.643033,
     9764.840540, 29295.433842],
    [2028, 61536.718989, 25787.534372, 1288.252548, 19602.411917, 2660.260623, 865.399548, 18612.655469, 2781.931883,
     9844.367951, 29615.228102],
    [2029, 62424.589716, 26035.869871, 1301.545334, 19918.604661, 2722.274808, 872.248041, 18747.266131, 3018.092331,
     9921.544273, 29935.952944],
    [2030, 63299.253574, 26281.286210, 1314.623664, 20229.607302, 2784.793763, 879.120606, 18863.666502, 3263.303617,
     9996.371885, 30257.604877],
    [2031, 64160.678316, 26523.784799, 1327.488277, 20535.418929, 2847.817155, 886.017443, 18962.893997, 3516.744981,
     10068.853166, 30580.180413],
    [2032, 65008.831693, 26763.367048, 1340.139916, 20836.038628, 2911.344651, 892.938750, 19045.986035, 3777.595664,
     10138.990492, 30903.676062],
    [2033, 65843.681456, 27000.034369, 1352.579321, 21131.465488, 2975.375917, 899.884726, 19113.980033, 4045.034907,
     10206.786244, 31228.088332],
    [2034, 66665.195356, 27233.788171, 1364.807233, 21421.698597, 3039.910619, 906.855568, 19167.913408, 4318.241949,
     10272.242798, 31553.413735],
    [2035, 67473.341147, 27464.629864, 1376.824393, 21706.737043, 3104.948425, 913.851476, 19208.823576, 4596.396032,
     10335.362533, 31879.648780],
    [2036, 68268.086578, 27692.560859, 1388.631541, 21986.579914, 3170.488999, 920.872648, 19237.747956, 4878.676394,
     10396.147827, 32206.789977],
    [2037, 69049.399401, 27917.582566, 1400.229419, 22261.226298, 3236.532010, 927.919282, 19255.723964, 5164.262277,
     10454.601059, 32534.833837],
    [2038, 69817.247369, 28139.696395, 1411.618767, 22530.675283, 3303.077123, 934.991578, 19263.789018, 5452.332921,
     10510.724606, 32863.776870],
    [2039, 70571.598233, 28358.903757, 1422.800327, 22794.925956, 3370.124005, 942.089733, 19262.980534, 5742.067567,
     10564.520848, 33193.615585],
    [2040, 71312.419743, 28575.206062, 1433.774838, 23053.977406, 3437.672323, 949.213945, 19254.335930, 6032.645454,
     10615.992161, 33524.346493],
    [2041, 72039.679653, 28788.604721, 1444.543043, 23307.828720, 3505.721742, 956.364414, 19238.892623, 6323.245824,
     10665.140925, 33855.966104],
    [2042, 72753.345712, 28999.101143, 1455.105681, 23556.478988, 3574.271930, 963.541338, 19217.688030, 6613.047915,
     10711.969518, 34188.470928],
    [2043, 73453.385674, 29206.696740, 1465.463493, 23799.927295, 3643.322553, 970.744915, 19191.759568, 6901.230970,
     10756.480317, 34521.857475],
    [2044, 74139.767289, 29411.392921, 1475.617222, 24038.172732, 3712.873277, 977.975344, 19162.144655, 7186.974227,
     10798.675702, 34856.122256],
    [2045, 74812.458309, 29613.191096, 1485.567606, 24271.214385, 3782.923768, 985.232824, 19129.880708, 7469.456929,
     10838.558050, 35191.261779],
    [2046, 75471.426486, 29812.092676, 1495.315388, 24499.051342, 3853.473694, 992.517552, 19096.005143, 7747.858313,
     10876.129739, 35527.272556],
    [2047, 76116.639570, 30008.099072, 1504.861308, 24721.682692, 3924.522721, 999.829727, 19061.555378, 8021.357622,
     10911.393148, 35864.151096],
    [2048, 76748.065315, 30201.211693, 1514.206106, 24939.107522, 3996.070515, 1007.169549, 19027.568831, 8289.134096,
     10944.350655, 36201.893909],
    [2049, 77365.671470, 30391.431951, 1523.350525, 25151.324920, 4068.116743, 1014.537214, 18995.082918, 8550.366974,
     10975.004638, 36540.497506],
    [2050, 77969.425788, 30578.761254, 1532.295304, 25358.333975, 4140.661071, 1021.932922, 18965.135056, 8804.235498,
     11003.357476, 36879.958397],
    [2051, 78559.296021, 30763.201014, 1541.041184, 25560.133774, 4213.703166, 1029.356872, 18938.762663, 9049.918907,
     11029.411546, 37220.273091],
    [2052, 79135.249920, 30944.752641, 1549.588907, 25756.723405, 4287.242694, 1036.809261, 18917.003156, 9286.596442,
     11053.169227, 37561.438099],
    [2053, 79697.255236, 31123.417546, 1557.939213, 25948.101957, 4361.279321, 1044.290289, 18900.893952, 9513.447344,
     11074.632897, 37903.449931],
    [2054, 80245.279721, 31299.197138, 1566.092844, 26134.268517, 4435.812715, 1051.800153, 18891.472468, 9729.650852,
     11093.804935, 38246.305097],
    [2055, 80779.291126, 31472.092827, 1574.050539, 26315.222173, 4510.842541, 1059.339052, 18889.776121, 9934.386206,
     11110.687718, 38590.000107],
    [2056, 81299.257204, 31642.106025, 1581.813039, 26490.962012, 4586.368467, 1066.907185, 18896.842329, 10126.832649,
     11125.283625, 38934.531470],
    [2057, 81805.145705, 31809.238142, 1589.381087, 26661.487124, 4662.390158, 1074.504750, 18913.708509, 10306.169418,
     11137.595034, 39279.895699],
    [2058, 82296.924382, 31973.490587, 1596.755422, 26826.796596, 4738.907281, 1082.131946, 18941.412077, 10471.575756,
     11147.624323, 39626.089301],
    [2059, 82774.560985, 32134.864771, 1603.936785, 26986.889516, 4815.919502, 1089.788971, 18980.990452, 10622.230902,
     11155.373871, 39973.108788],
    [2060, 83238.023267, 32293.362105, 1610.925917, 27141.764972, 4893.426489, 1097.476023, 19033.481050, 10757.314097,
     11160.846055, 40320.950669]]

# Data from BuildingAutomation "Helper Tables"!B26:L73, 'PDS1-51p2050-SCurve (Book Ed.1)' scenario
soln_ref_funits_adopted_buildingautomation_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 16577.825917, 14915.990000, 0.0, 1087.770945, 0.0, 0.0, 1087.770945, 0.0, 3622.850000, 11293.140000],

    [2015, 16186.916601, 15077.127575, 0.0, 1109.789026, 0.0, 0.0, 1102.218374, 0.0, 3669.722357, 11435.968738],

    [2016, 16370.072257, 15238.265150, 0.0, 1131.807107, 0.0, 0.0, 1116.665803, 0.0, 3716.594714, 11578.797475],

    [2017, 16553.227913, 15399.402724, 0.0, 1153.825189, 0.0, 0.0, 1131.113232, 0.0, 3763.467070, 11721.626213],

    [2018, 16736.383569, 15560.540299, 0.0, 1175.843270, 0.0, 0.0, 1145.560660, 0.0, 3810.339427, 11864.454950],

    [2019, 16919.539225, 15721.677874, 0.0, 1197.861351, 0.0, 0.0, 1160.008089, 0.0, 3857.211784, 12007.283688],

    [2020, 17102.694881, 15882.815449, 0.0, 1219.879433, 0.0, 0.0, 1174.455518, 0.0, 3904.084141, 12150.112425],

    [2021, 17285.850538, 16043.953023, 0.0, 1241.897514, 0.0, 0.0, 1188.902947, 0.0, 3950.956498, 12292.941163],

    [2022, 17469.006194, 16205.090598, 0.0, 1263.915595, 0.0, 0.0, 1203.350376, 0.0, 3997.828855, 12435.769900],

    [2023, 17652.161850, 16366.228173, 0.0, 1285.933677, 0.0, 0.0, 1217.797805, 0.0, 4044.701211, 12578.598638],

    [2024, 17835.317506, 16527.365748, 0.0, 1307.951758, 0.0, 0.0, 1232.245234, 0.0, 4091.573568, 12721.427375],

    [2025, 18018.473162, 16688.503323, 0.0, 1329.969840, 0.0, 0.0, 1246.692663, 0.0, 4138.445925, 12864.256113],

    [2026, 18201.628818, 16849.640897, 0.0, 1351.987921, 0.0, 0.0, 1261.140092, 0.0, 4185.318282, 13007.084850],

    [2027, 18384.784474, 17010.778472, 0.0, 1374.006002, 0.0, 0.0, 1275.587521, 0.0, 4232.190639, 13149.913588],

    [2028, 18567.940130, 17171.916047, 0.0, 1396.024084, 0.0, 0.0, 1290.034950, 0.0, 4279.062996, 13292.742325],

    [2029, 18751.095787, 17333.053622, 0.0, 1418.042165, 0.0, 0.0, 1304.482379, 0.0, 4325.935352, 13435.571063],

    [2030, 18934.251443, 17494.191196, 0.0, 1440.060246, 0.0, 0.0, 1318.929808, 0.0, 4372.807709, 13578.399800],

    [2031, 19117.407099, 17655.328771, 0.0, 1462.078328, 0.0, 0.0, 1333.377237, 0.0, 4419.680066, 13721.228538],

    [2032, 19300.562755, 17816.466346, 0.0, 1484.096409, 0.0, 0.0, 1347.824666, 0.0, 4466.552423, 13864.057275],

    [2033, 19483.718411, 17977.603921, 0.0, 1506.114490, 0.0, 0.0, 1362.272095, 0.0, 4513.424780, 14006.886013],

    [2034, 19666.874067, 18138.741495, 0.0, 1528.132572, 0.0, 0.0, 1376.719524, 0.0, 4560.297137, 14149.714750],

    [2035, 19850.029723, 18299.879070, 0.0, 1550.150653, 0.0, 0.0, 1391.166953, 0.0, 4607.169493, 14292.543488],

    [2036, 20033.185380, 18461.016645, 0.0, 1572.168735, 0.0, 0.0, 1405.614382, 0.0, 4654.041850, 14435.372225],

    [2037, 20216.341036, 18622.154220, 0.0, 1594.186816, 0.0, 0.0, 1420.061811, 0.0, 4700.914207, 14578.200963],

    [2038, 20399.496692, 18783.291795, 0.0, 1616.204897, 0.0, 0.0, 1434.509240, 0.0, 4747.786564, 14721.029700],

    [2039, 20582.652348, 18944.429369, 0.0, 1638.222979, 0.0, 0.0, 1448.956669, 0.0, 4794.658921, 14863.858438],

    [2040, 20765.808004, 19105.566944, 0.0, 1660.241060, 0.0, 0.0, 1463.404098, 0.0, 4841.531277, 15006.687175],

    [2041, 20948.963660, 19266.704519, 0.0, 1682.259141, 0.0, 0.0, 1477.851527, 0.0, 4888.403634, 15149.515913],

    [2042, 21132.119316, 19427.842094, 0.0, 1704.277223, 0.0, 0.0, 1492.298956, 0.0, 4935.275991, 15292.344651],

    [2043, 21315.274973, 19588.979668, 0.0, 1726.295304, 0.0, 0.0, 1506.746385, 0.0, 4982.148348, 15435.173388],

    [2044, 21498.430629, 19750.117243, 0.0, 1748.313386, 0.0, 0.0, 1521.193814, 0.0, 5029.020705, 15578.002126],

    [2045, 21681.586285, 19911.254818, 0.0, 1770.331467, 0.0, 0.0, 1535.641243, 0.0, 5075.893062, 15720.830863],

    [2046, 21864.741941, 20072.392393, 0.0, 1792.349548, 0.0, 0.0, 1550.088672, 0.0, 5122.765418, 15863.659601],

    [2047, 22047.897597, 20233.529968, 0.0, 1814.367630, 0.0, 0.0, 1564.536101, 0.0, 5169.637775, 16006.488338],

    [2048, 22231.053253, 20394.667542, 0.0, 1836.385711, 0.0, 0.0, 1578.983530, 0.0, 5216.510132, 16149.317076],

    [2049, 22414.208909, 20555.805117, 0.0, 1858.403792, 0.0, 0.0, 1593.430959, 0.0, 5263.382489, 16292.145813],

    [2050, 22597.364566, 20716.942692, 0.0, 1880.421874, 0.0, 0.0, 1607.878388, 0.0, 5310.254846, 16434.974551],

    [2051, 22780.520222, 20878.080267, 0.0, 1902.439955, 0.0, 0.0, 1622.325817, 0.0, 5357.127203, 16577.803288],

    [2052, 22963.675878, 21039.217841, 0.0, 1924.458036, 0.0, 0.0, 1636.773246, 0.0, 5403.999559, 16720.632026],

    [2053, 23146.831534, 21200.355416, 0.0, 1946.476118, 0.0, 0.0, 1651.220675, 0.0, 5450.871916, 16863.460763],

    [2054, 23329.987190, 21361.492991, 0.0, 1968.494199, 0.0, 0.0, 1665.668104, 0.0, 5497.744273, 17006.289501],

    [2055, 23513.142846, 21522.630566, 0.0, 1990.512281, 0.0, 0.0, 1680.115533, 0.0, 5544.616630, 17149.118238],

    [2056, 23696.298502, 21683.768141, 0.0, 2012.530362, 0.0, 0.0, 1694.562962, 0.0, 5591.488987, 17291.946976],

    [2057, 23879.454159, 21844.905715, 0.0, 2034.548443, 0.0, 0.0, 1709.010391, 0.0, 5638.361344, 17434.775713],

    [2058, 24062.609815, 22006.043290, 0.0, 2056.566525, 0.0, 0.0, 1723.457820, 0.0, 5685.233700, 17577.604451],

    [2059, 24245.765471, 22167.180865, 0.0, 2078.584606, 0.0, 0.0, 1737.905249, 0.0, 5732.106057, 17720.433188],

    [2060, 24428.921127, 22328.318440, 0.0, 2100.602687, 0.0, 0.0, 1752.352678, 0.0, 5778.978414,
     17863.261926]]


# Data from BuildingAutomation "Unit Adoption Calculations"!A68:K115
pds_tam_per_region_buildingautomation_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 47780.340000, 22016.400000, 1079.360000, 14669.080000, 1849.480000, 771.320000, 12830.400000, 746.655422,
     7506.892755, 25341.720614],
    [2015, 48807.247557, 22292.887618, 1095.593698, 15020.021853, 1900.162097, 778.469482, 14733.555488, 908.917982,
     8626.261046, 25531.758439],
    [2016, 49863.872964, 22579.300538, 1111.741837, 15403.602940, 1955.583914, 785.023087, 15199.304907, 952.728405,
     8734.187018, 25840.113502],
    [2017, 50907.710733, 22862.775963, 1127.665888, 15782.005780, 2011.514837, 791.598185, 15633.357611, 1016.259541,
     8839.733364, 26149.441027],
    [2018, 51938.728615, 23143.315305, 1143.366592, 16155.229462, 2067.954533, 798.194974, 16036.751017, 1098.690631,
     8942.902460, 26459.737523],
    [2019, 52956.894362, 23420.919972, 1158.844690, 16523.273074, 2124.902668, 804.813653, 16410.522542, 1199.200916,
     9043.696686, 26770.999499],
    [2020, 53962.175724, 23695.591377, 1174.100923, 16886.135703, 2182.358909, 811.454420, 16755.709604, 1316.969636,
     9142.118420, 27083.223467],
    [2021, 54954.540454, 23967.330928, 1189.136032, 17243.816437, 2240.322923, 818.117473, 17073.349619, 1451.176030,
     9238.170040, 27396.405936],
    [2022, 55933.956303, 24236.140037, 1203.950758, 17596.314364, 2298.794375, 824.803012, 17364.480005, 1600.999340,
     9331.853923, 27710.543417],
    [2023, 56900.391023, 24502.020114, 1218.545841, 17943.628573, 2357.772932, 831.511234, 17630.138179, 1765.618806,
     9423.172449, 28025.632419],
    [2024, 57853.812366, 24764.972568, 1232.922022, 18285.758152, 2417.258261, 838.242339, 17871.361558, 1944.213668,
     9512.127995, 28341.669452],
    [2025, 58794.188082, 25024.998811, 1247.080043, 18622.702187, 2477.250028, 844.996524, 18089.187560, 2135.963166,
     9598.722940, 28658.651027],
    [2026, 59721.485923, 25282.100252, 1261.020643, 18954.459768, 2537.747900, 851.773988, 18284.653600, 2340.046541,
     9682.959663, 28976.573653],
    [2027, 60635.673642, 25536.278302, 1274.744565, 19281.029982, 2598.751543, 858.574930, 18458.797098, 2555.643033,
     9764.840540, 29295.433842],
    [2028, 61536.718989, 25787.534372, 1288.252548, 19602.411917, 2660.260623, 865.399548, 18612.655469, 2781.931883,
     9844.367951, 29615.228102],
    [2029, 62424.589716, 26035.869871, 1301.545334, 19918.604661, 2722.274808, 872.248041, 18747.266131, 3018.092331,
     9921.544273, 29935.952944],
    [2030, 63299.253574, 26281.286210, 1314.623664, 20229.607302, 2784.793763, 879.120606, 18863.666502, 3263.303617,
     9996.371885, 30257.604877],
    [2031, 64160.678316, 26523.784799, 1327.488277, 20535.418929, 2847.817155, 886.017443, 18962.893997, 3516.744981,
     10068.853166, 30580.180413],
    [2032, 65008.831693, 26763.367048, 1340.139916, 20836.038628, 2911.344651, 892.938750, 19045.986035, 3777.595664,
     10138.990492, 30903.676062],
    [2033, 65843.681456, 27000.034369, 1352.579321, 21131.465488, 2975.375917, 899.884726, 19113.980033, 4045.034907,
     10206.786244, 31228.088332],
    [2034, 66665.195356, 27233.788171, 1364.807233, 21421.698597, 3039.910619, 906.855568, 19167.913408, 4318.241949,
     10272.242798, 31553.413735],
    [2035, 67473.341147, 27464.629864, 1376.824393, 21706.737043, 3104.948425, 913.851476, 19208.823576, 4596.396032,
     10335.362533, 31879.648780],
    [2036, 68268.086578, 27692.560859, 1388.631541, 21986.579914, 3170.488999, 920.872648, 19237.747956, 4878.676394,
     10396.147827, 32206.789977],
    [2037, 69049.399401, 27917.582566, 1400.229419, 22261.226298, 3236.532010, 927.919282, 19255.723964, 5164.262277,
     10454.601059, 32534.833837],
    [2038, 69817.247369, 28139.696395, 1411.618767, 22530.675283, 3303.077123, 934.991578, 19263.789018, 5452.332921,
     10510.724606, 32863.776870],
    [2039, 70571.598233, 28358.903757, 1422.800327, 22794.925956, 3370.124005, 942.089733, 19262.980534, 5742.067567,
     10564.520848, 33193.615585],
    [2040, 71312.419743, 28575.206062, 1433.774838, 23053.977406, 3437.672323, 949.213945, 19254.335930, 6032.645454,
     10615.992161, 33524.346493],
    [2041, 72039.679653, 28788.604721, 1444.543043, 23307.828720, 3505.721742, 956.364414, 19238.892623, 6323.245824,
     10665.140925, 33855.966104],
    [2042, 72753.345712, 28999.101143, 1455.105681, 23556.478988, 3574.271930, 963.541338, 19217.688030, 6613.047915,
     10711.969518, 34188.470928],
    [2043, 73453.385674, 29206.696740, 1465.463493, 23799.927295, 3643.322553, 970.744915, 19191.759568, 6901.230970,
     10756.480317, 34521.857475],
    [2044, 74139.767289, 29411.392921, 1475.617222, 24038.172732, 3712.873277, 977.975344, 19162.144655, 7186.974227,
     10798.675702, 34856.122256],
    [2045, 74812.458309, 29613.191096, 1485.567606, 24271.214385, 3782.923768, 985.232824, 19129.880708, 7469.456929,
     10838.558050, 35191.261779],
    [2046, 75471.426486, 29812.092676, 1495.315388, 24499.051342, 3853.473694, 992.517552, 19096.005143, 7747.858313,
     10876.129739, 35527.272556],
    [2047, 76116.639570, 30008.099072, 1504.861308, 24721.682692, 3924.522721, 999.829727, 19061.555378, 8021.357622,
     10911.393148, 35864.151096],
    [2048, 76748.065315, 30201.211693, 1514.206106, 24939.107522, 3996.070515, 1007.169549, 19027.568831, 8289.134096,
     10944.350655, 36201.893909],
    [2049, 77365.671470, 30391.431951, 1523.350525, 25151.324920, 4068.116743, 1014.537214, 18995.082918, 8550.366974,
     10975.004638, 36540.497506],
    [2050, 77969.425788, 30578.761254, 1532.295304, 25358.333975, 4140.661071, 1021.932922, 18965.135056, 8804.235498,
     11003.357476, 36879.958397],
    [2051, 78559.296021, 30763.201014, 1541.041184, 25560.133774, 4213.703166, 1029.356872, 18938.762663, 9049.918907,
     11029.411546, 37220.273091],
    [2052, 79135.249920, 30944.752641, 1549.588907, 25756.723405, 4287.242694, 1036.809261, 18917.003156, 9286.596442,
     11053.169227, 37561.438099],
    [2053, 79697.255236, 31123.417546, 1557.939213, 25948.101957, 4361.279321, 1044.290289, 18900.893952, 9513.447344,
     11074.632897, 37903.449931],
    [2054, 80245.279721, 31299.197138, 1566.092844, 26134.268517, 4435.812715, 1051.800153, 18891.472468, 9729.650852,
     11093.804935, 38246.305097],
    [2055, 80779.291126, 31472.092827, 1574.050539, 26315.222173, 4510.842541, 1059.339052, 18889.776121, 9934.386206,
     11110.687718, 38590.000107],
    [2056, 81299.257204, 31642.106025, 1581.813039, 26490.962012, 4586.368467, 1066.907185, 18896.842329, 10126.832649,
     11125.283625, 38934.531470],
    [2057, 81805.145705, 31809.238142, 1589.381087, 26661.487124, 4662.390158, 1074.504750, 18913.708509, 10306.169418,
     11137.595034, 39279.895699],
    [2058, 82296.924382, 31973.490587, 1596.755422, 26826.796596, 4738.907281, 1082.131946, 18941.412077, 10471.575756,
     11147.624323, 39626.089301],
    [2059, 82774.560985, 32134.864771, 1603.936785, 26986.889516, 4815.919502, 1089.788971, 18980.990452, 10622.230902,
     11155.373871, 39973.108788],
    [2060, 83238.023267, 32293.362105, 1610.925917, 27141.764972, 4893.426489, 1097.476023, 19033.481050, 10757.314097,
     11160.846055, 40320.950669]]

# Data from BuildingAutomation "Helper Tables"!B91:L137 'PDS2-70p2050-Linear (Book Ed.1)' scenario
soln_pds_funits_adopted_buildingautomation_linear_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa",
     "Latin America", "China", "India", "EU", "USA"],
    [2014, 16577.825917, 14915.990000, 0.000000, 1087.770945, 0.000000, 0.000000, 1087.770945, 0.000000, 3622.850000,
     11293.140000],
    [2015, 17065.125171, 15351.066979, 21.281879, 1621.073618, 57.509182, 14.193513, 1057.555085, 0.000000, 3827.864097,
     12003.884955],
    [2016, 18126.489397, 15786.143959, 42.563758, 2154.376291, 115.018363, 28.387026, 1027.339225, 0.000000,
     4032.878193, 12714.629911],
    [2017, 19187.853623, 16221.220938, 63.845638, 2687.678964, 172.527545, 42.580538, 997.123366, 0.000000, 4237.892290,
     13425.374866],
    [2018, 20249.217849, 16656.297917, 85.127517, 3220.981637, 230.036726, 56.774051, 966.907506, 0.000000, 4442.906386,
     14136.119822],
    [2019, 21310.582075, 17091.374896, 106.409396, 3754.284311, 287.545908, 70.967564, 936.691647, 0.000000,
     4647.920483, 14846.864777],
    [2020, 22371.946301, 17526.451876, 127.691275, 4287.586984, 345.055089, 85.161077, 906.475787, 0.000000,
     4852.934579, 15557.609733],
    [2021, 23433.310527, 17961.528855, 148.973155, 4820.889657, 402.564271, 99.354590, 876.259928, 0.000000,
     5057.948676, 16268.354688],
    [2022, 24494.674753, 18396.605834, 170.255034, 5354.192330, 460.073452, 113.548102, 846.044068, 0.000000,
     5262.962772, 16979.099644],
    [2023, 25556.038979, 18831.682814, 191.536913, 5887.495003, 517.582634, 127.741615, 815.828208, 0.000000,
     5467.976869, 17689.844599],
    [2024, 26617.403205, 19266.759793, 212.818792, 6420.797677, 575.091815, 141.935128, 785.612349, 0.000000,
     5672.990965, 18400.589555],
    [2025, 27678.767431, 19701.836772, 234.100671, 6954.100350, 632.600997, 156.128641, 755.396489, 0.000000,
     5878.005062, 19111.334510],
    [2026, 28740.131657, 20136.913751, 255.382551, 7487.403023, 690.110178, 170.322154, 725.180630, 0.000000,
     6083.019159, 19822.079466],
    [2027, 29801.495883, 20571.990731, 276.664430, 8020.705696, 747.619360, 184.515667, 694.964770, 0.000000,
     6288.033255, 20532.824421],
    [2028, 30862.860109, 21007.067710, 297.946309, 8554.008369, 805.128542, 198.709179, 664.748911, 0.000000,
     6493.047352, 21243.569376],
    [2029, 31924.224336, 21442.144689, 319.228188, 9087.311043, 862.637723, 212.902692, 634.533051, 0.000000,
     6698.061448, 21954.314332],
    [2030, 32985.588562, 21877.221669, 340.510068, 9620.613716, 920.146905, 227.096205, 604.317191, 0.000000,
     6903.075545, 22665.059287],
    [2031, 34046.952788, 22312.298648, 361.791947, 10153.916389, 977.656086, 241.289718, 574.101332, 0.000000,
     7108.089641, 23375.804243],
    [2032, 35108.317014, 22747.375627, 383.073826, 10687.219062, 1035.165268, 255.483231, 543.885472, 0.000000,
     7313.103738, 24086.549198],
    [2033, 36169.681240, 23182.452606, 404.355705, 11220.521735, 1092.674449, 269.676743, 513.669613, 0.000000,
     7518.117834, 24797.294154],
    [2034, 37231.045466, 23617.529586, 425.637584, 11753.824409, 1150.183631, 283.870256, 483.453753, 0.000000,
     7723.131931, 25508.039109],
    [2035, 38292.409692, 24052.606565, 446.919464, 12287.127082, 1207.692812, 298.063769, 453.237894, 0.000000,
     7928.146028, 26218.784065],
    [2036, 39353.773918, 24487.683544, 468.201343, 12820.429755, 1265.201994, 312.257282, 423.022034, 0.000000,
     8133.160124, 26929.529020],
    [2037, 40415.138144, 24922.760524, 489.483222, 13353.732428, 1322.711175, 326.450795, 392.806174, 0.000000,
     8338.174221, 27640.273976],
    [2038, 41476.502370, 25357.837503, 510.765101, 13887.035102, 1380.220357, 340.644307, 362.590315, 0.000000,
     8543.188317, 28351.018931],
    [2039, 42537.866596, 25792.914482, 532.046981, 14420.337775, 1437.729539, 354.837820, 332.374455, 0.000000,
     8748.202414, 29061.763887],
    [2040, 43599.230822, 26227.991461, 553.328860, 14953.640448, 1495.238720, 369.031333, 302.158596, 0.000000,
     8953.216510, 29772.508842],
    [2041, 44660.595048, 26663.068441, 574.610739, 15486.943121, 1552.747902, 383.224846, 271.942736, 0.000000,
     9158.230607, 30483.253797],
    [2042, 45721.959274, 27098.145420, 595.892618, 16020.245794, 1610.257083, 397.418359, 241.726877, 0.000000,
     9363.244703, 31193.998753],
    [2043, 46783.323500, 27533.222399, 617.174497, 16553.548468, 1667.766265, 411.611872, 211.511017, 0.000000,
     9568.258800, 31904.743708],
    [2044, 47844.687727, 27968.299379, 638.456377, 17086.851141, 1725.275446, 425.805384, 181.295157, 0.000000,
     9773.272896, 32615.488664],
    [2045, 48906.051953, 28403.376358, 659.738256, 17620.153814, 1782.784628, 439.998897, 151.079298, 0.000000,
     9978.286993, 33326.233619],
    [2046, 49967.416179, 28838.453337, 681.020135, 18153.456487, 1840.293809, 454.192410, 120.863438, 0.000000,
     10183.301090, 34036.978575],
    [2047, 51028.780405, 29273.530316, 702.302014, 18686.759160, 1897.802991, 468.385923, 90.647579, 0.000000,
     10388.315186, 34747.723530],
    [2048, 52090.144631, 29708.607296, 723.583894, 19220.061834, 1955.312172, 482.579436, 60.431719, 0.000000,
     10593.329283, 35458.468486],
    [2049, 53151.508857, 30143.684275, 744.865773, 19753.364507, 2012.821354, 496.772948, 30.215860, 0.000000,
     10798.343379, 36169.213441],
    [2050, 54212.873083, 30578.761254, 766.147652, 20286.667180, 2070.330535, 510.966461, 0.000000, 0.000000,
     11003.357476, 36879.958397],
    [2051, 55023.600090, 30763.201014, 787.429531, 20819.969853, 2127.839717, 525.159974, -30.215860, 0.000000,
     11029.411546, 37220.273091],
    [2052, 55831.438964, 30944.752641, 808.711410, 21353.272526, 2185.348899, 539.353487, -60.431719, 0.000000,
     11053.169227, 37561.438099],
    [2053, 56636.391115, 31123.417546, 829.993290, 21886.575200, 2242.858080, 553.547000, -90.647579, 0.000000,
     11074.632897, 37903.449931],
    [2054, 57438.457953, 31299.197138, 851.275169, 22419.877873, 2300.367262, 567.740512, -120.863438, 0.000000,
     11093.804935, 38246.305097],
    [2055, 58237.640890, 31472.092827, 872.557048, 22953.180546, 2357.876443, 581.934025, -151.079298, 0.000000,
     11110.687718, 38590.000107],
    [2056, 59033.941335, 31642.106025, 893.838927, 23486.483219, 2415.385625, 596.127538, -181.295157, 0.000000,
     11125.283625, 38934.531470],
    [2057, 59827.360698, 31809.238142, 915.120807, 24019.785892, 2472.894806, 610.321051, -211.511017, 0.000000,
     11137.595034, 39279.895699],
    [2058, 60617.900390, 31973.490587, 936.402686, 24553.088566, 2530.403988, 624.514564, -241.726877, 0.000000,
     11147.624323, 39626.089301],
    [2059, 61405.561821, 32134.864771, 957.684565, 25086.391239, 2587.913169, 638.708077, -271.942736, 0.000000,
     11155.373871, 39973.108788],
    [2060, 62190.346401, 32293.362105, 978.966444, 25619.693912, 2645.422351, 652.901589, -302.158596, 0.000000,
     11160.846055, 40320.950669]]
