"""Tests for unitadoption.py."""

import pandas as pd
import pytest
import io
from model import unitadoption, tam
import advanced_controls


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

def test_ref_population():
  ua = unitadoption.UnitAdoption()
  population = ua.ref_population()
  assert population['World'][2014] == pytest.approx(7249.180596)
  assert population['Middle East and Africa'][2031] == pytest.approx(2093.543821)
  assert population['USA'][2060] == pytest.approx(465.280628)

def test_ref_gdp():
  ua = unitadoption.UnitAdoption()
  gdp = ua.ref_gdp()
  assert gdp['World'][2014] == pytest.approx(58307.866135)
  assert gdp['Latin America'][2030] == pytest.approx(8390.982338)
  assert gdp['USA'][2060] == pytest.approx(36982.727199)

def test_ref_gdp_per_capita():
  ua = unitadoption.UnitAdoption()
  pop = ua.ref_population()
  gdp = ua.ref_gdp()
  gpc = ua.ref_gdp_per_capita(ref_population=pop, ref_gdp=gdp)
  assert gpc['World'][2060] == pytest.approx(21.67246)
  assert gpc['Asia (Sans Japan)'][2029] == pytest.approx(6.51399)
  assert gpc['USA'][2014] == pytest.approx(43.77208)

def test_ref_tam_per_capita():
  tm = tam.TAM()
  tpr = tm.ref_tam_per_region()
  ua = unitadoption.UnitAdoption()
  pop = ua.ref_population()
  tpc = ua.ref_tam_per_capita(ref_tam_per_region=tpr, ref_population=pop)
  assert tpc['World'][2016] == pytest.approx(3.38350004047)
  assert tpc['Latin America'][2029] == pytest.approx(3.62748818668)
  assert tpc['USA'][2059] == pytest.approx(12.21081396314)

def test_ref_tam_per_gdp_per_capita():
  tm = tam.TAM()
  tpr = tm.ref_tam_per_region()
  ua = unitadoption.UnitAdoption()
  pop = ua.ref_population()
  gdp = ua.ref_gdp()
  gpc = ua.ref_gdp_per_capita(ref_population=pop, ref_gdp=gdp)
  tpgpc = ua.ref_tam_per_gdp_per_capita(ref_tam_per_region=tpr, ref_gdp_per_capita=gpc)
  assert tpgpc['OECD90'][2014] == pytest.approx(256.68795471511)
  assert tpgpc['China'][2033] == pytest.approx(743.15450999975)
  assert tpgpc['EU'][2060] == pytest.approx(85.95558928452)

def test_ref_tam_growth():
  tm = tam.TAM()
  tpr = tm.ref_tam_per_region()
  ua = unitadoption.UnitAdoption()
  tg = ua.ref_tam_growth(ref_tam_per_region=tpr)
  assert tg['Eastern Europe'][2015] == pytest.approx(24.26693428425)
  assert tg['India'][2037] == pytest.approx(171.36849827619)
  assert tg['EU'][2060] == pytest.approx(71.14797759969)
  assert tg['World'][2014] == ''

def test_pds_population():
  ua = unitadoption.UnitAdoption()
  population = ua.pds_population()
  assert population['World'][2016] == pytest.approx(7415.5738320)
  assert population['India'][2031] == pytest.approx(1539.9070540)
  assert population['USA'][2060] == pytest.approx(403.5036840)

def test_pds_gdp():
  ua = unitadoption.UnitAdoption()
  gdp = ua.pds_gdp()
  assert gdp['Eastern Europe'][2014] == pytest.approx(2621.864076293940)
  assert gdp['Latin America'][2030] == pytest.approx(8058.323682075440)
  assert gdp['USA'][2060] == pytest.approx(32072.400550257600)

def test_pds_gdp_per_capita():
  ua = unitadoption.UnitAdoption()
  pop = ua.pds_population()
  gdp = ua.pds_gdp()
  gpc = ua.pds_gdp_per_capita(pds_population=pop, pds_gdp=gdp)
  assert gpc['World'][2060] == pytest.approx(21.703844951868)
  assert gpc['Asia (Sans Japan)'][2029] == pytest.approx(6.52868)
  assert gpc['USA'][2014] == pytest.approx(44.49768)

def test_pds_tam_per_capita():
  tm = tam.TAM()
  tpr = tm.pds_tam_per_region()
  ua = unitadoption.UnitAdoption()
  pop = ua.pds_population()
  tpc = ua.pds_tam_per_capita(pds_tam_per_region=tpr, pds_population=pop)
  assert tpc['World'][2015] == pytest.approx(3.357451)
  assert tpc['India'][2039] == pytest.approx(2.945601)
  assert tpc['USA'][2058] == pytest.approx(13.978179)

def test_pds_tam_per_gdp_per_capita():
  tm = tam.TAM()
  tpr = tm.pds_tam_per_region()
  ua = unitadoption.UnitAdoption()
  pop = ua.pds_population()
  gdp = ua.pds_gdp()
  gpc = ua.pds_gdp_per_capita(pds_population=pop, pds_gdp=gdp)
  tpgpc = ua.pds_tam_per_gdp_per_capita(pds_tam_per_region=tpr, pds_gdp_per_capita=gpc)
  assert tpgpc['OECD90'][2015] == pytest.approx(247.759624)
  assert tpgpc['China'][2032] == pytest.approx(759.164408)
  assert tpgpc['EU'][2060] == pytest.approx(85.955589)

def test_pds_tam_growth():
  tm = tam.TAM()
  tpr = tm.pds_tam_per_region()
  ua = unitadoption.UnitAdoption()
  tg = ua.pds_tam_growth(pds_tam_per_region=tpr)
  assert tg['Eastern Europe'][2015] == pytest.approx(24.266934)
  assert tg['India'][2033] == pytest.approx(159.378951)
  assert tg['USA'][2060] == pytest.approx(33.502722)
  assert tg['OECD90'][2014] == ''

def test_soln_pds_cumulative_funits():
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
      [2015, 176.24, 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1],
      [2016, 272.03, 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1],
      [2017, 383.31, 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1]]
  soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  soln_funit_adoption_2014 = pd.DataFrame([[112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12]],
      columns=['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
        'Latin America', 'China', 'India', 'EU', 'USA'], index=[2014])
  ac = advanced_controls.AdvancedControls(soln_funit_adoption_2014=soln_funit_adoption_2014)
  ua = unitadoption.UnitAdoption(ac=ac)
  result = ua.soln_pds_cumulative_funits(soln_pds_funits_adopted)
  v = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      [2014, 112.63, 150.01, 0.66, 42.15, 3.15, 29.30, 29.94, 5.50, 110.54, 26.25],
      [2015, 288.87, 151.01, 1.66, 43.15, 4.15, 30.30, 30.94, 6.50, 111.54, 27.25],
      [2016, 560.91, 152.01, 2.66, 44.15, 5.15, 31.30, 31.94, 7.50, 112.54, 28.25],
      [2017, 944.21, 153.01, 3.66, 45.15, 6.15, 32.30, 32.94, 8.50, 113.54, 29.25]]
  expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
  pd.testing.assert_frame_equal(result.iloc[0:5], expected, check_exact=False, check_less_precise=2, check_names=False)

def test_soln_pds_new_iunits_reqd():
  v = [["Year", "World", "OECD90"],
      [2014, 0.06115814489, 0.04072624506],
      [2015, 0.09569632876, 0.00000000000], [2016, 0.14770917868, 0.00000000000],
      [2017, 0.20813155943, 0.00000000000], [2018, 0.27658585364, 0.00000000000],
      [2019, 0.35269444391, 0.00000000000], [2020, 0.35511275489, 0.00000000000],
      [2021, 0.52636404313, 0.00000000000], [2022, 0.62316981729, 0.00000000000],
      [2023, 0.72611941799, 0.00000000000], [2024, 0.83483522783, 0.00000000000],
      [2025, 0.86627964703, 0.00000000000], [2026, 1.06805500539, 0.00000000000],
      [2027, 1.19180373834, 0.00000000000], [2028, 1.31980821089, 0.00000000000],
      [2029, 1.45169080567, 0.00000000000], [2030, 1.65078562298, 0.00000000000],
      [2031, 1.72557989233, 0.00000000000], [2032, 1.86683114944, 0.00000000000],
      [2033, 2.01045005923, 0.00000000000], [2034, 2.15605900432, 0.00000000000],
      [2035, 2.30328036731, 0.00000000000], [2036, 2.45173653082, 0.00000000000],
      [2037, 2.60104987747, 0.00000000000], [2038, 2.75084278988, 0.00000000000],
      [2039, 2.90073765065, 0.00000000000], [2040, 3.07612351532, 0.00000000000],
      [2041, 3.19932274775, 0.00000000000], [2042, 3.34725774931, 0.00000000000],
      [2043, 3.49378422970, 0.00000000000], [2044, 3.63852457153, 0.00000000000],
      [2045, 3.78110115742, 0.00000000000], [2046, 3.92113636998, 0.00000000000],
      [2047, 4.05825259183, 0.00000000000], [2048, 4.19207220558, 0.00000000000],
      [2049, 4.32221759385, 0.00000000000], [2050, 4.43499993794, 0.00000000000],
      [2051, 4.56997522439, 0.00000000000], [2052, 4.68683223190, 0.00000000000],
      [2053, 4.79850454439, 0.00000000000], [2054, 4.90461454447, 0.00000000000],
      [2055, 5.00478461475, 0.00000000000], [2056, 5.09863713786, 0.00000000000],
      [2057, 5.18579449640, 0.00000000000], [2058, 5.26587907300, 0.00000000000],
      [2059, 5.33851325027, 0.00000000000], [2060, 5.40331941081, 0.00000000000]]
  soln_pds_tot_iunits_req = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
  ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=48343.80, soln_avg_annual_use=1841.67)
  ua = unitadoption.UnitAdoption(ac=ac)
  result = ua.soln_pds_new_iunits_reqd(soln_pds_tot_iunits_req)
  v = [["Year", "World", "OECD90"],
      [2015, 0.03453818387, 0.00000000000], [2016, 0.05201284992, 0.00000000000],
      [2017, 0.06042238076, 0.00000000000], [2018, 0.06845429421, 0.00000000000],
      [2019, 0.07610859028, 0.00000000000], [2020, 0.00241831098, 0.00000000000],
      [2021, 0.17125128823, 0.00000000000], [2022, 0.09680577417, 0.00000000000],
      [2023, 0.10294960069, 0.00000000000], [2024, 0.10871580984, 0.00000000000],
      [2025, 0.03144441920, 0.00000000000], [2026, 0.20177535836, 0.00000000000],
      [2027, 0.12374873295, 0.00000000000], [2028, 0.12800447256, 0.00000000000],
      [2029, 0.13188259477, 0.00000000000], [2030, 0.19909481731, 0.00000000000],
      [2031, 0.07479426935, 0.00000000000], [2032, 0.14125125711, 0.00000000000],
      [2033, 0.14361890979, 0.00000000000], [2034, 0.14560894508, 0.00000000000],
      [2035, 0.14722136299, 0.00000000000], [2036, 0.14845616351, 0.00000000000],
      [2037, 0.14931334665, 0.00000000000], [2038, 0.14979291240, 0.00000000000],
      [2039, 0.14989486077, 0.00000000000], [2040, 0.17538586468, 0.00000000000],
      [2041, 0.12319923243, 0.00000000000], [2042, 0.18247318543, 0.00000000000],
      [2043, 0.19853933031, 0.00000000000], [2044, 0.20516272259, 0.00000000000],
      [2045, 0.21103088010, 0.00000000000], [2046, 0.21614380284, 0.00000000000],
      [2047, 0.13953453283, 0.00000000000], [2048, 0.30507090198, 0.00000000000],
      [2049, 0.22695116243, 0.00000000000], [2050, 0.21573194479, 0.00000000000],
      [2051, 0.24369109629, 0.00000000000], [2052, 0.14830142671, 0.00000000000],
      [2053, 0.31344767084, 0.00000000000], [2054, 0.22985873303, 0.00000000000],
      [2055, 0.22817454284, 0.00000000000], [2056, 0.22573511788, 0.00000000000],
      [2057, 0.28625217585, 0.00000000000], [2058, 0.15487884595, 0.00000000000],
      [2059, 0.21388543438, 0.00000000000], [2060, 0.20842507034, 0.00000000000]]
  expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_soln_ref_cumulative_funits():
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
      [2015, 117.07, 75.63, 0.34, 22.16, 1.71, 15.42, 15.43, 3.07, 55.76, 13.22],
      [2016, 121.51, 76.25, 0.34, 23.25, 1.85, 16.18, 15.89, 3.39, 56.25, 13.31],
      [2017, 125.95, 76.87, 0.35, 24.33, 1.98, 16.95, 16.35, 3.71, 56.73, 13.40]]
  soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  ua = unitadoption.UnitAdoption()
  result = ua.soln_ref_cumulative_funits(soln_ref_funits_adopted)
  v = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
      [2015, 229.70, 150.63, 0.67, 43.23, 3.29, 30.07, 30.41, 5.82, 111.03, 26.34],
      [2016, 351.21, 226.88, 1.01, 66.48, 5.13, 46.25, 46.30, 9.21, 167.28, 39.65],
      [2017, 477.16, 303.75, 1.36, 90.81, 7.11, 63.20, 62.65, 12.92, 224.01, 53.05]]
  expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
  pd.testing.assert_frame_equal(result.iloc[0:5], expected, check_exact=False, check_less_precise=2, check_names=False)

def test_soln_net_annual_funits_adopted():
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe'],
      [2014, 112.63, 75.00, 0.33],
      [2015, 117.07, 75.63, 0.34],
      [2016, 121.51, 76.25, 0.34]]
  soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe'],
      [2014, 112.63, 75.00, 0.33],
      [2015, 176.24, 0.0, 0.0],
      [2016, 272.03, 0.0, 0.0]]
  soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  ua = unitadoption.UnitAdoption()
  result = ua.soln_net_annual_funits_adopted(soln_ref_funits_adopted=soln_ref_funits_adopted,
      soln_pds_funits_adopted=soln_pds_funits_adopted)
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe'],
      [2014, 0.0, 0.0, 0.0],
      [2015, 59.17, -75.63, -0.34],
      [2016, 150.52, -76.25, -0.34]]
  expected = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_conv_ref_tot_iunits():
  ac = advanced_controls.AdvancedControls(conv_ref_avg_annual_use=4946.840187342)
  ua = unitadoption.UnitAdoption(ac=ac)
  tm = tam.TAM()
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
      [2015, 117.07, 75.63, 0.34, 22.16, 1.71, 15.42, 15.43, 3.07, 55.76, 13.22],
      [2016, 121.51, 76.25, 0.34, 23.25, 1.85, 16.18, 15.89, 3.39, 56.25, 13.31]]
  soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  result = ua.conv_ref_tot_iunits(tm.ref_tam_per_region(), soln_ref_funits_adopted)
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe'],
      [2014, 4.53535289538, 1.93172544646, 0.40864109200],
      [2015, 4.87963781659, 1.94274331751, 0.41354556337],
      [2016, 5.05302431141, 1.95081104871, 0.41846626996]]
  expected = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  pd.testing.assert_frame_equal(result.iloc[0:3,0:3], expected, check_exact=False)

def test_conv_ref_annual_tot_iunits():
  ac = advanced_controls.AdvancedControls(conv_ref_avg_annual_use=4946.840187342)
  ua = unitadoption.UnitAdoption(ac=ac)
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe'],
      [2015, 59.16952483163, -75.62640223557, -0.33768156367],
      [2016, 150.52159292976, -76.24855891557, -0.34297979401]]
  soln_net_annual_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  result = ua.conv_ref_annual_tot_iunits(
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)
  funits = [['Year', 'World', 'OECD90', 'Eastern Europe'],
      [2015, 0.01196107466, -0.01528781998, -0.00006826207],
      [2016, 0.03042782609, -0.01541358848, -0.00006933311]]
  expected = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_soln_pds_net_grid_electricity_units_saved():
  v = [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]
  soln_net_annual_funits_adopted = pd.DataFrame(v)
  ac = advanced_controls.AdvancedControls(soln_energy_efficiency_factor=0,
      conv_annual_energy_used=0)
  ua = unitadoption.UnitAdoption(ac=ac)
  result = ua.soln_pds_net_grid_electricity_units_saved(
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)
  expected = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
  pd.testing.assert_frame_equal(result, expected)

  ac = advanced_controls.AdvancedControls(soln_energy_efficiency_factor=2,
      conv_annual_energy_used=3)
  ua = unitadoption.UnitAdoption(ac=ac)
  expected = pd.DataFrame([[6.0, 12.0, 18.0, 24.0], [30.0, 36.0, 42.0, 48.0]])
  result = ua.soln_pds_net_grid_electricity_units_saved(
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_soln_pds_fuel_units_avoided():
  v = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
  soln_net_annual_funits_adopted = pd.DataFrame(v)
  ac = advanced_controls.AdvancedControls(conv_fuel_consumed_per_funit=0,
      soln_fuel_efficiency_factor=1)
  ua = unitadoption.UnitAdoption(ac=ac)
  result = ua.soln_pds_fuel_units_avoided(soln_net_annual_funits_adopted)
  expected = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
  pd.testing.assert_frame_equal(result, expected)

  ac = advanced_controls.AdvancedControls(conv_fuel_consumed_per_funit=2,
      soln_fuel_efficiency_factor=2)
  ua = unitadoption.UnitAdoption(ac=ac)
  result = ua.soln_pds_fuel_units_avoided(soln_net_annual_funits_adopted)
  expected = pd.DataFrame([[4.0, 8.0, 12.0, 16.0], [4.0, 8.0, 12.0, 16.0]])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_soln_pds_direct_co2_emissions_saved():
  ac = advanced_controls.AdvancedControls(conv_emissions_per_funit=7,
      soln_emissions_per_funit=5)
  ua = unitadoption.UnitAdoption(ac=ac)
  v = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
  soln_net_annual_funits_adopted = pd.DataFrame(v)
  result = ua.soln_pds_direct_co2_emissions_saved(soln_net_annual_funits_adopted)
  expected = pd.DataFrame([[2.0, 4.0, 6.0, 8.0], [2.0, 4.0, 6.0, 8.0]])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_soln_pds_direct_ch4_emissions_saved():
  ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback')
  ua = unitadoption.UnitAdoption(ac=ac)
  v = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
  soln_net_annual_funits_adopted = pd.DataFrame(v)
  result = ua.soln_pds_direct_ch4_co2_emissions_saved(soln_net_annual_funits_adopted,
      ch4_per_funit=2)
  expected = pd.DataFrame([[68.0, 136.0, 204.0, 272.0], [68.0, 136.0, 204.0, 272.0]])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

  ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback')
  ua = unitadoption.UnitAdoption(ac=ac)
  v = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
  soln_net_annual_funits_adopted = pd.DataFrame(v)
  result = ua.soln_pds_direct_ch4_co2_emissions_saved(soln_net_annual_funits_adopted,
      ch4_co2equiv_per_funit=2)
  expected = pd.DataFrame([[2.0, 4.0, 6.0, 8.0], [2.0, 4.0, 6.0, 8.0]])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_soln_pds_direct_n2o_emissions_saved():
  ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback')
  ua = unitadoption.UnitAdoption(ac=ac)
  v = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
  soln_net_annual_funits_adopted = pd.DataFrame(v)
  result = ua.soln_pds_direct_n2o_co2_emissions_saved(soln_net_annual_funits_adopted,
      n2o_per_funit=2)
  print(str(result))
  expected = pd.DataFrame([[596.0, 1192.0, 1788.0, 2384.0], [596.0, 1192.0, 1788.0, 2384.0]])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

  ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback')
  ua = unitadoption.UnitAdoption(ac=ac)
  v = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
  soln_net_annual_funits_adopted = pd.DataFrame(v)
  result = ua.soln_pds_direct_n2o_co2_emissions_saved(soln_net_annual_funits_adopted,
      n2o_co2equiv_per_funit=2)
  expected = pd.DataFrame([[2.0, 4.0, 6.0, 8.0], [2.0, 4.0, 6.0, 8.0]])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)
