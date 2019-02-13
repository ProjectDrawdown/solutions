"""Tests for adoptiondata.py."""

import pathlib
import numpy as np
import pandas as pd
import pytest
from model import adoptiondata
from model import advanced_controls

datadir = pathlib.Path(__file__).parents[0].joinpath('data')

# arguments used in SolarPVUtil 28Aug18, used in many tests
adconfig_list = [
    ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
      'Latin America', 'China', 'India', 'EU', 'USA'],
    ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
      '3rd Poly', '3rd Poly', '3rd Poly'],
    ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
      'Medium', 'Medium'],
    ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
g_adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')

g_data_sources = {
  'Baseline Cases': {
    '6DS': str(datadir.joinpath('ad_based_on_IEA_ETP_2016_6DS.csv')),
    'IRefpol': str(datadir.joinpath('ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv')),
    'MREFPol': str(datadir.joinpath('ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv')),
    'GREFpol': str(datadir.joinpath('ad_based_on_AMPERE_2014_GEM_E3_Reference.csv')),
  },
  'Conservative Cases': {
    '4DS': str(datadir.joinpath('ad_based_on_IEA_ETP_2016_4DS.csv')),
    'I550': str(datadir.joinpath('ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv')),
    'M550': str(datadir.joinpath('ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv')),
    'G550': str(datadir.joinpath('ad_based_on_AMPERE_2014_GEM_E3_550.csv')),
    'Greenpeace R': str(datadir.joinpath('ad_based_on_Greenpeace_2015_Reference.csv')),
  },
  'Ambitious Cases': {
    '2DS': str(datadir.joinpath('ad_based_on_IEA_ETP_2016_2DS.csv')),
    'I450': str(datadir.joinpath('ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv')),
    'M450': str(datadir.joinpath('ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv')),
    'G450': str(datadir.joinpath('ad_based_on_AMPERE_2014_GEM_E3_450.csv')),
    'Greenpeace ER': str(datadir.joinpath('ad_based_on_Greenpeace_2015_Energy_Revolution.csv')),
  },
  '100% RES2050 Case': {
    'Greenpeace AER': str(datadir.joinpath('ad_based_on_Greenpeace_2015_Advanced_Revolution.csv')),
  },
}

def test_adoption_data():
  ad = adoptiondata.AdoptionData(ac=None, data_sources=g_data_sources, adconfig=None)
  a = ad.adoption_data_global()
  assert a['4DS'][2035] == pytest.approx(898.010968835815)
  assert a['Greenpeace R'][2027] == pytest.approx(327.712635691309)
  a = ad.adoption_data_oecd90()
  assert a['Greenpeace AER'][2040] == pytest.approx(58)
  a = ad.adoption_data_eastern_europe()
  assert a['Greenpeace AER'][2050] == pytest.approx(117)
  a = ad.adoption_data_asia_sans_japan()
  assert a['Greenpeace AER'][2014] == pytest.approx(15)
  a = ad.adoption_data_middle_east_and_africa()
  assert a['Greenpeace AER'][2017] == pytest.approx(42)
  a = ad.adoption_data_latin_america()
  assert a['Greenpeace AER'][2057] == pytest.approx(506)
  a = ad.adoption_data_china()
  assert a['Greenpeace AER'][2036] == pytest.approx(325)
  a = ad.adoption_data_india()
  assert a['Greenpeace AER'][2022] == pytest.approx(187)
  a = ad.adoption_data_eu()
  assert a['Greenpeace AER'][2031] == pytest.approx(380)
  a = ad.adoption_data_usa()
  assert a['Greenpeace AER'][2053] == pytest.approx(966)

def test_CSP_LA():
  # ConcentratedSolar Latin America exposed a corner case, test it specifically.
  data_sources = {
    'Baseline Cases': {
      'source1': str(datadir.joinpath('ad_CSP_LA_source1.csv')),
      'source2': str(datadir.joinpath('ad_CSP_LA_source2.csv')),
      'source3': str(datadir.joinpath('ad_CSP_LA_source3.csv')),
      'source4': str(datadir.joinpath('ad_CSP_LA_source4.csv')),
      },
    'Conservative Cases': {},
    'Ambitious Cases': {},
    '100% RES2050 Case': {},
  }
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source='Baseline Cases',
      soln_pds_adoption_prognostication_growth='Medium')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=data_sources, adconfig=g_adconfig)
  result = ad.adoption_trend_latin_america()
  assert result.loc[2014, 'adoption'] == pytest.approx(-3.39541250661)
  assert result.loc[2037, 'adoption'] == pytest.approx(13.14383564892)
  assert result.loc[2060, 'adoption'] == pytest.approx(295.34923165295)

def test_CSP_World():
  # ConcentratedSolar World exposed a corner case, test it specifically.
  data_sources = {
    'Ambitious Cases': {
      'source1': str(datadir.joinpath('ad_CSP_World_source1.csv')),
      'source2': str(datadir.joinpath('ad_CSP_World_source2.csv')),
      'source3': str(datadir.joinpath('ad_CSP_World_source3.csv')),
      'source4': str(datadir.joinpath('ad_CSP_World_source4.csv')),
      'source5': str(datadir.joinpath('ad_CSP_World_source5.csv')),
      'source6': str(datadir.joinpath('ad_CSP_World_source6.csv')),
      },
    'Conservative Cases': {},
    'Baseline Cases': {},
    '100% RES2050 Case': {},
  }
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source='Ambitious Cases',
      soln_pds_adoption_prognostication_growth='Low')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=data_sources, adconfig=g_adconfig)
  result = ad.adoption_trend_global()
  assert result.loc[2014, 'adoption'] == pytest.approx(34.94818207)
  assert result.loc[2015, 'adoption'] == pytest.approx(24.85041545)
  assert result.loc[2016, 'adoption'] == pytest.approx(17.78567283)
  assert result.loc[2060, 'adoption'] == pytest.approx(4079.461034)

def test_adoption_min_max_sd_global():
  s = 'Greenpeace AER'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s)
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  result = ad.adoption_min_max_sd_global()
  expected = pd.DataFrame(adoption_min_max_sd_global_list[1:],
      columns=adoption_min_max_sd_global_list[0],
      dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_adoption_min_max_sd_global_ambitious():
  s = 'Ambitious Cases'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s)
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  result = ad.adoption_min_max_sd_global()
  expected = pd.DataFrame(adoption_min_max_sd_global_ambitious_list[1:],
      columns=adoption_min_max_sd_global_ambitious_list[0],
      dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_adoption_low_med_high_global():
  s = 'Greenpeace AER'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s)
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  result = ad.adoption_low_med_high_global()
  expected = pd.DataFrame(adoption_low_med_high_global_list[1:],
      columns=adoption_low_med_high_global_list[0],
      dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_adoption_low_med_high_global_all_sources():
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source='ALL SOURCES')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  result = ad.adoption_low_med_high_global()
  expected = pd.DataFrame(adoption_low_med_high_global_all_sources_list[1:],
      columns=adoption_low_med_high_global_all_sources_list[0],
      dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_adoption_trend_global():
  s = 'Greenpeace AER'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s,
      soln_pds_adoption_prognostication_growth='Medium')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  result = ad.adoption_trend_global(trend='Linear')
  expected = pd.DataFrame(linear_trend_global_list[1:],
      columns=linear_trend_global_list[0], dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

  result = ad.adoption_trend_global(trend='Degree2')
  expected = pd.DataFrame(poly_degree2_trend_global_list[1:],
      columns=poly_degree2_trend_global_list[0], dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

  result = ad.adoption_trend_global(trend='Degree3')
  expected = pd.DataFrame(poly_degree3_trend_global_list[1:],
      columns=poly_degree3_trend_global_list[0], dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

  result = ad.adoption_trend_global(trend='Exponential')
  expected = pd.DataFrame(exponential_trend_global_list[1:],
      columns=exponential_trend_global_list[0], dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

  adconfig_mod = g_adconfig.copy()
  adconfig_mod.loc['trend', 'World'] = 'Exponential'
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=adconfig_mod)
  result = ad.adoption_trend_global()
  expected = pd.DataFrame(exponential_trend_global_list[1:],
      columns=exponential_trend_global_list[0], dtype=np.float64).set_index('Year')
  expected.index = expected.index.astype(int)
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_adoption_is_single_source():
  s = 'Greenpeace AER'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s)
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  assert ad.adoption_is_single_source() == True
  s = 'ALL SOURCES'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s)
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  assert ad.adoption_is_single_source() == False
  s = 'Ambitious Cases'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s)
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  assert ad.adoption_is_single_source() == False
  s = 'No such name'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s)
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  with pytest.raises(ValueError):
    _ = ad.adoption_is_single_source()

def test_adoption_data_per_region():
  data_sources = {
    'Baseline Cases': {
      'george': str(datadir.joinpath('ad_all_regions.csv')),
      },
    'Conservative Cases': {},
    'Ambitious Cases': {},
    '100% RES2050 Case': {},
  }
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source='george',
      soln_pds_adoption_prognostication_growth='Medium')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=data_sources, adconfig=g_adconfig)
  result = ad.adoption_data_per_region()
  assert result.loc[2030, 'EU'] == pytest.approx(437.0)
  assert result.loc[2046, 'Eastern Europe'] == pytest.approx(175.0)

def test_adoption_data_per_region_no_data():
  # Verify that if there is no data, the returned DF contains N/A not filled with 0.0.
  data_sources = {
    'Baseline Cases': {
      's1': str(datadir.joinpath('ad_all_regions_no_data.csv')),
      },
    'Conservative Cases': {},
    'Ambitious Cases': {},
    '100% RES2050 Case': {},
  }
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source='s1',
      soln_pds_adoption_prognostication_growth='Medium')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=data_sources, adconfig=g_adconfig)
  result = ad.adoption_data_per_region()
  for region in result.columns:
    assert result.loc[:, region].count() == 0

def test_adoption_data_per_region_missing_data():
  # regional data with NaN for 2012-2013
  data_sources = {
    'Baseline Cases': {
      's1': str(datadir.joinpath('ad_missing_region_data_s1.csv')),
      's2': str(datadir.joinpath('ad_missing_region_data_s2.csv')),
      's3': str(datadir.joinpath('ad_missing_region_data_s3.csv')),
      },
    'Conservative Cases': {},
    'Ambitious Cases': {},
    '100% RES2050 Case': {},
  }
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source='ALL SOURCES',
      soln_pds_adoption_prognostication_growth='Medium')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=data_sources, adconfig=g_adconfig)
  result = ad.adoption_trend_per_region()
  # Expected values from LandfillMethane Middle East (renamed OECD90 here)
  expected = pd.DataFrame(
    [0.04274361694, 0.10439941173, 0.16201388582, 0.21580091091, 0.26597435870, 0.31274810090, 0.35633600920,
     0.39695195531, 0.43480981094, 0.47012344779, 0.50310673755, 0.53397355194, 0.56293776265, 0.59021324139,
     0.61601385986, 0.64055348976, 0.66404600281, 0.68670527069, 0.70874516512, 0.73037955779, 0.75182232041,
     0.77328732468, 0.79498844231, 0.81713954500, 0.83995450444, 0.86364719235, 0.88843148043, 0.91452124038,
     0.94213034390, 0.97147266269, 1.00276206847, 1.03621243292, 1.07203762776, 1.11045152469, 1.15166799540,
     1.19590091161, 1.24336414502, 1.29427156733, 1.34883705023, 1.40727446545, 1.46979768467, 1.53662057960,
     1.60795702194, 1.68402088340, 1.76502603569, 1.85118635049, 1.94271569952],
    index=list(range(2014,2061)), columns=['OECD90'])
  pd.testing.assert_frame_equal(result[['OECD90']], expected, check_exact=False, check_names=False)

def test_adoption_trend_per_region():
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source='ALL SOURCES',
      soln_pds_adoption_prognostication_growth='Medium')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  result = ad.adoption_trend_per_region()
  pd.testing.assert_series_equal(result['World'],
      ad.adoption_trend_global()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['OECD90'],
      ad.adoption_trend_oecd90()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['Eastern Europe'],
      ad.adoption_trend_eastern_europe()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['Asia (Sans Japan)'],
      ad.adoption_trend_asia_sans_japan()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['Middle East and Africa'],
      ad.adoption_trend_middle_east_and_africa()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['Latin America'],
      ad.adoption_trend_latin_america()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['China'],
      ad.adoption_trend_china()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['India'],
      ad.adoption_trend_india()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['EU'],
      ad.adoption_trend_eu()['adoption'], check_names=False)
  pd.testing.assert_series_equal(result['USA'],
      ad.adoption_trend_usa()['adoption'], check_names=False)

def test_to_dict():
  s = 'Greenpeace AER'
  ac = advanced_controls.AdvancedControls(soln_pds_adoption_prognostication_source=s,
      soln_pds_adoption_prognostication_growth='Medium')
  ad = adoptiondata.AdoptionData(ac=ac, data_sources=g_data_sources, adconfig=g_adconfig)
  result = ad.to_dict()
  expected = ['adoption_data_global', 'adoption_min_max_sd_global',
      'adoption_low_med_high_global', 'adoption_trend_linear_global',
      'adoption_trend_poly_degree2_global', 'adoption_trend_poly_degree3_global',
      'adoption_trend_exponential_global',
      'adoption_data_oecd90', 'adoption_min_max_sd_oecd90',
      'adoption_low_med_high_oecd90', 'adoption_trend_linear_oecd90',
      'adoption_trend_poly_degree2_oecd90', 'adoption_trend_poly_degree3_oecd90',
      'adoption_trend_exponential_oecd90',
      'adoption_data_eastern_europe', 'adoption_min_max_sd_eastern_europe',
      'adoption_low_med_high_eastern_europe', 'adoption_trend_linear_eastern_europe',
      'adoption_trend_poly_degree2_eastern_europe', 'adoption_trend_poly_degree3_eastern_europe',
      'adoption_trend_exponential_eastern_europe',
      'adoption_data_asia_sans_japan', 'adoption_min_max_sd_asia_sans_japan',
      'adoption_low_med_high_asia_sans_japan', 'adoption_trend_linear_asia_sans_japan',
      'adoption_trend_poly_degree2_asia_sans_japan', 'adoption_trend_poly_degree3_asia_sans_japan',
      'adoption_trend_exponential_asia_sans_japan',
      'adoption_data_middle_east_and_africa', 'adoption_min_max_sd_middle_east_and_africa',
      'adoption_low_med_high_middle_east_and_africa', 'adoption_trend_linear_middle_east_and_africa',
      'adoption_trend_poly_degree2_middle_east_and_africa',
      'adoption_trend_poly_degree3_middle_east_and_africa',
      'adoption_trend_exponential_middle_east_and_africa',
      'adoption_data_latin_america', 'adoption_min_max_sd_latin_america',
      'adoption_low_med_high_latin_america', 'adoption_trend_linear_latin_america',
      'adoption_trend_poly_degree2_latin_america', 'adoption_trend_poly_degree3_latin_america',
      'adoption_trend_exponential_latin_america',
      'adoption_data_china', 'adoption_min_max_sd_china', 'adoption_low_med_high_china',
      'adoption_trend_linear_china', 'adoption_trend_poly_degree2_china',
      'adoption_trend_poly_degree3_china', 'adoption_trend_exponential_china',
      'adoption_data_india', 'adoption_min_max_sd_india', 'adoption_low_med_high_india',
      'adoption_trend_linear_india', 'adoption_trend_poly_degree2_india',
      'adoption_trend_poly_degree3_india', 'adoption_trend_exponential_india',
      'adoption_data_eu', 'adoption_min_max_sd_eu', 'adoption_low_med_high_eu',
      'adoption_trend_linear_eu', 'adoption_trend_poly_degree2_eu',
      'adoption_trend_poly_degree3_eu', 'adoption_trend_exponential_eu',
      'adoption_data_usa', 'adoption_min_max_sd_usa', 'adoption_low_med_high_usa',
      'adoption_trend_linear_usa', 'adoption_trend_poly_degree2_usa',
      'adoption_trend_poly_degree3_usa', 'adoption_trend_exponential_usa',
      ]
  for ex in expected:
    assert ex in result
    f = getattr(ad, ex, None)
    if f:
      check = f()
      if isinstance(check, pd.DataFrame):
        pd.testing.assert_frame_equal(result[ex], check, check_exact=False)
      elif isinstance(check, pd.Series):
        pd.testing.assert_series_equal(result[ex], check, check_exact=False)
      else:
        assert result[ex] == pytest.approx(check)


# 'Adoption Data'!X46:Z94
adoption_min_max_sd_global_list = [['Year', 'Min', 'Max', 'S.D'],
    [2012, 58.200000, 58.200000, 0.000000], [2013, 81.060000, 81.060000, 0.000000],
    [2014, 112.633033, 112.633033, 0.000000], [2015, 94.240258, 218.061459, 37.837223],
    [2016, 115.457997, 272.031352, 50.912757], [2017, 139.360289, 383.309352, 70.927561],
    [2018, 166.022587, 509.379474, 96.404783], [2019, 194.474873, 649.546273, 126.360959],
    [2020, 203.777863, 654.000000, 153.513406], [2021, 228.265871, 969.388115, 197.441518],
    [2022, 245.065460, 1147.672267, 237.818374], [2023, 261.788054, 1337.271311, 281.018215],
    [2024, 278.423860, 1537.489801, 326.789074], [2025, 311.400000, 1595.400000, 330.239857],
    [2026, 311.395943, 1967.003336, 425.141105], [2027, 327.712636, 2194.907488, 477.295159],
    [2028, 343.903374, 2430.649302, 531.153951], [2029, 359.958367, 2673.533332, 586.543088],
    [2030, 378.000000, 3040.200000, 679.160229], [2031, 391.621946, 3177.946255, 701.160954],
    [2032, 407.210949, 3438.084256, 760.063844], [2033, 422.625039, 3702.582689, 819.816148],
    [2034, 437.854424, 3970.746106, 880.277085], [2035, 452.889312, 4241.879064, 947.307160],
    [2036, 467.719912, 4515.286114, 1002.844241], [2037, 482.336431, 4790.271812, 1064.718473],
    [2038, 496.729079, 5066.140711, 1126.868629], [2039, 510.888062, 5342.197365, 1189.231979],
    [2040, 499.200000, 5665.200000, 1270.356939], [2041, 538.465871, 5892.092154, 1314.377567],
    [2042, 551.865113, 6164.539397, 1377.118694], [2043, 564.991524, 6434.392611, 1439.986601],
    [2044, 577.835313, 6700.956350, 1503.012843], [2045, 590.386687, 6963.535167, 1561.352973],
    [2046, 602.635855, 7221.433617, 1629.833623], [2047, 614.573025, 7473.956253, 1693.843531],
    [2048, 626.188406, 7720.407630, 1758.440240], [2049, 637.472206, 7960.092301, 1823.822675],
    [2050, 657.600000, 8167.800000, 1883.358921], [2051, 659.005894, 8416.379743, 1959.040916],
    [2052, 669.236199, 8631.591621, 2027.012498], [2053, 679.095755, 8837.255009, 2098.064244],
    [2054, 688.574772, 9032.674462, 2171.344027], [2055, 697.663457, 9217.154532, 2247.244231],
    [2056, 706.352018, 9389.999774, 2326.194035], [2057, 714.630664, 9550.514742, 2408.641031],
    [2058, 722.489603, 9698.003990, 2495.073624], [2059, 729.919043, 9831.772071, 2586.001183],
    [2060, 736.909192, 9951.123540, 2681.954064]]

# 'Adoption Data'!X46:Z94 with scenario set to 'PDS-10p2050- Plausible (Book Ed.1)'
adoption_min_max_sd_global_ambitious_list = [['Year', 'Min', 'Max', 'S.D'],
    [2012, 58.200000, 58.200000, 0.000000], [2013, 81.060000, 81.060000, 0.000000],
    [2014, 112.633033, 112.633033, 0.000000], [2015, 94.240258, 218.061459, 35.174253],
    [2016, 115.457997, 272.031352, 45.844976], [2017, 139.360289, 383.309352, 62.586340],
    [2018, 166.022587, 509.379474, 84.134863], [2019, 194.474873, 649.546273, 109.549218],
    [2020, 203.777863, 654.000000, 125.337511], [2021, 228.265871, 969.388115, 169.673017],
    [2022, 245.065460, 1147.672267, 203.632920], [2023, 261.788054, 1337.271311, 239.759105],
    [2024, 278.423860, 1537.489801, 277.795158], [2025, 311.400000, 1595.400000, 280.799153],
    [2026, 311.395943, 1967.003336, 358.721755], [2027, 327.712636, 2194.907488, 401.189948],
    [2028, 343.903374, 2430.649302, 444.695137], [2029, 359.958367, 2673.533332, 489.105963],
    [2030, 378.000000, 3040.200000, 574.192621], [2031, 391.621946, 3177.946255, 579.875063],
    [2032, 407.210949, 3438.084256, 625.968051], [2033, 422.625039, 3702.582689, 672.343203],
    [2034, 437.854424, 3970.746106, 718.897800], [2035, 452.889312, 4241.879064, 776.083776],
    [2036, 467.719912, 4515.286114, 812.306321], [2037, 482.336431, 4790.271812, 859.017705],
    [2038, 496.729079, 5066.140711, 905.720524], [2039, 510.888062, 5342.197365, 952.457465],
    [2040, 499.200000, 5665.200000, 1017.041854], [2041, 538.465871, 5892.092154, 1046.168130],
    [2042, 551.865113, 6164.539397, 1093.357821], [2043, 564.991524, 6434.392611, 1140.995102],
    [2044, 577.835313, 6700.956350, 1189.269831], [2045, 590.386687, 6963.535167, 1223.177580],
    [2046, 602.635855, 7221.433617, 1288.822767], [2047, 614.573025, 7473.956253, 1340.751222],
    [2048, 626.188406, 7720.407630, 1394.600809], [2049, 637.472206, 7960.092301, 1450.849651],
    [2050, 657.600000, 8167.800000, 1500.661540], [2051, 659.005894, 8416.379743, 1582.456655],
    [2052, 669.236199, 8631.591621, 1638.828838], [2053, 679.095755, 8837.255009, 1709.754739],
    [2054, 688.574772, 9032.674462, 1785.785609], [2055, 697.663457, 9217.154532, 1867.531757],
    [2056, 706.352018, 9389.999774, 1955.619309], [2057, 714.630664, 9550.514742, 2050.635977],
    [2058, 722.489603, 9698.003990, 2153.196740], [2059, 729.919043, 9831.772071, 2263.889242],
    [2060, 736.909192, 9951.123540, 2383.280980]]

# 'Adoption Data'!AB46:AD94
adoption_low_med_high_global_list = [['Year', 'Low', 'Medium', 'High'],
    [2012, 58.200000, 58.200000, 58.200000], [2013, 81.060000, 81.060000, 81.060000],
    [2014, 112.633033, 112.633033, 112.633033], [2015, 138.403698, 176.240921, 214.078144],
    [2016, 221.118595, 272.031352, 322.944109], [2017, 312.381791, 383.309352, 454.236913],
    [2018, 412.974691, 509.379474, 605.784256], [2019, 523.185314, 649.546273, 775.907231],
    [2020, 500.486594, 654.000000, 807.513406], [2021, 771.946597, 969.388115, 1166.829634],
    [2022, 909.853893, 1147.672267, 1385.490641], [2023, 1056.253096, 1337.271311, 1618.289526],
    [2024, 1210.700727, 1537.489801, 1864.278876], [2025, 1265.160143, 1595.400000, 1925.639857],
    [2026, 1541.862231, 1967.003336, 2392.144441], [2027, 1717.612329, 2194.907488, 2672.202647],
    [2028, 1899.495352, 2430.649302, 2961.803253], [2029, 2086.990245, 2673.533332, 3260.076420],
    [2030, 2361.039771, 3040.200000, 3719.360229], [2031, 2476.785301, 3177.946255, 3879.107210],
    [2032, 2678.020412, 3438.084256, 4198.148100], [2033, 2882.766540, 3702.582689, 4522.398837],
    [2034, 3090.469022, 3970.746106, 4851.023191], [2035, 3294.571903, 4241.879064, 5189.186224],
    [2036, 3512.441874, 4515.286114, 5518.130355], [2037, 3725.553339, 4790.271812, 5854.990285],
    [2038, 3939.272082, 5066.140711, 6193.009340], [2039, 4152.965387, 5342.197365, 6531.429344],
    [2040, 4394.843061, 5665.200000, 6935.556939], [2041, 4577.714588, 5892.092154, 7206.469721],
    [2042, 4787.420703, 6164.539397, 7541.658092], [2043, 4994.406010, 6434.392611, 7874.379213],
    [2044, 5197.943507, 6700.956350, 8203.969193], [2045, 5402.182194, 6963.535167, 8524.888140],
    [2046, 5591.599994, 7221.433617, 8851.267240], [2047, 5780.112723, 7473.956253, 9167.799784],
    [2048, 5961.967390, 7720.407630, 9478.847871], [2049, 6136.269626, 7960.092301, 9783.914977],
    [2050, 6284.441079, 8167.800000, 10051.158921], [2051, 6457.338827, 8416.379743, 10375.420659],
    [2052, 6604.579123, 8631.591621, 10658.604119], [2053, 6739.190765, 8837.255009, 10935.319253],
    [2054, 6861.330435, 9032.674462, 11204.018488], [2055, 6969.910301, 9217.154532, 11464.398763],
    [2056, 7063.805739, 9389.999774, 11716.193809], [2057, 7141.873711, 9550.514742, 11959.155773],
    [2058, 7202.930366, 9698.003990, 12193.077613], [2059, 7245.770888, 9831.772071, 12417.773254],
    [2060, 7269.169476, 9951.123540, 12633.077604]]

# 'Adoption Data'!AB46:AD94 with Advanced Controls B265 set to ALL SOURCES
adoption_low_med_high_global_all_sources_list = [['Year', 'Low', 'Medium', 'High'],
    [2012, 58.200000, 58.200000, 58.200000], [2013, 81.060000, 81.060000, 81.060000],
    [2014, 112.633033, 112.633033, 112.633033], [2015, 105.603550, 143.440773, 181.277995],
    [2016, 127.118631, 178.031388, 228.944145], [2017, 145.350020, 216.277581, 287.205142],
    [2018, 161.744158, 258.148941, 354.553723], [2019, 177.256713, 303.617671, 429.978630],
    [2020, 233.704628, 387.218033, 540.731439], [2021, 207.789889, 405.231407, 602.672926],
    [2022, 223.508399, 461.326773, 699.145147], [2023, 239.889454, 520.907669, 801.925884],
    [2024, 257.159907, 583.948981, 910.738056], [2025, 306.997867, 637.237725, 967.477582],
    [2026, 295.179590, 720.320695, 1145.461801], [2027, 316.304602, 793.599762, 1270.894921],
    [2028, 339.080224, 870.234174, 1401.388125], [2029, 363.664416, 950.207503, 1536.750591],
    [2030, 345.183977, 1024.344206, 1703.504435], [2031, 418.893521, 1120.054476, 1821.215430],
    [2032, 449.820470, 1209.884314, 1969.948158], [2033, 483.134195, 1302.950343, 2122.766492],
    [2034, 518.953374, 1399.230459, 2279.507544], [2035, 537.792556, 1485.099716, 2432.406876],
    [2036, 598.513116, 1601.357356, 2604.201597], [2037, 642.433505, 1707.151977, 2771.870450],
    [2038, 689.205335, 1816.073964, 2942.942594], [2039, 738.875230, 1928.107209, 3117.339187],
    [2040, 779.316063, 2049.673002, 3320.029942], [2041, 847.028954, 2161.406520, 3475.784087],
    [2042, 905.512113, 2282.630807, 3659.749502], [2043, 966.891116, 2406.877717, 3846.864319],
    [2044, 1031.106475, 2534.119318, 4037.132161], [2045, 1119.474313, 2680.827286, 4242.180259],
    [2046, 1167.661392, 2797.495015, 4427.328638], [2047, 1239.739315, 2933.582846, 4627.426377],
    [2048, 1314.126484, 3072.566724, 4831.006965], [2049, 1390.607087, 3214.429763, 5038.252438],
    [2050, 1473.209246, 3356.568167, 5239.927088], [2051, 1541.533750, 3500.574665, 5459.615581],
    [2052, 1629.989194, 3657.001693, 5684.014191], [2053, 1712.033415, 3810.097659, 5908.161903],
    [2054, 1794.576241, 3965.920268, 6137.264295], [2055, 1877.190347, 4124.434577, 6371.678808],
    [2056, 1959.419848, 4285.613883, 6611.807918], [2057, 2040.782840, 4449.423870, 6858.064901],
    [2058, 2120.769468, 4615.843091, 7110.916715], [2059, 2198.847801, 4784.848984, 7370.850167],
    [2060, 2274.465696, 4956.419760, 7638.373825]]

# 'Adoption Data'!BW50:CA96
linear_trend_global_list = [['Year', 'x', 'constant', 'adoption'],
    [2014, 0.000000, -445.045081, -445.045081], [2015, 232.618862, -445.045081, -212.426218],
    [2016, 465.237725, -445.045081, 20.192644], [2017, 697.856587, -445.045081, 252.811506],
    [2018, 930.475450, -445.045081, 485.430369], [2019, 1163.094312, -445.045081, 718.049231],
    [2020, 1395.713174, -445.045081, 950.668094], [2021, 1628.332037, -445.045081, 1183.286956],
    [2022, 1860.950899, -445.045081, 1415.905818], [2023, 2093.569761, -445.045081, 1648.524681],
    [2024, 2326.188624, -445.045081, 1881.143543], [2025, 2558.807486, -445.045081, 2113.762406],
    [2026, 2791.426349, -445.045081, 2346.381268], [2027, 3024.045211, -445.045081, 2579.000130],
    [2028, 3256.664073, -445.045081, 2811.618993], [2029, 3489.282936, -445.045081, 3044.237855],
    [2030, 3721.901798, -445.045081, 3276.856717], [2031, 3954.520660, -445.045081, 3509.475580],
    [2032, 4187.139523, -445.045081, 3742.094442], [2033, 4419.758385, -445.045081, 3974.713305],
    [2034, 4652.377248, -445.045081, 4207.332167], [2035, 4884.996110, -445.045081, 4439.951029],
    [2036, 5117.614972, -445.045081, 4672.569892], [2037, 5350.233835, -445.045081, 4905.188754],
    [2038, 5582.852697, -445.045081, 5137.807617], [2039, 5815.471560, -445.045081, 5370.426479],
    [2040, 6048.090422, -445.045081, 5603.045341], [2041, 6280.709284, -445.045081, 5835.664204],
    [2042, 6513.328147, -445.045081, 6068.283066], [2043, 6745.947009, -445.045081, 6300.901928],
    [2044, 6978.565871, -445.045081, 6533.520791], [2045, 7211.184734, -445.045081, 6766.139653],
    [2046, 7443.803596, -445.045081, 6998.758516], [2047, 7676.422459, -445.045081, 7231.377378],
    [2048, 7909.041321, -445.045081, 7463.996240], [2049, 8141.660183, -445.045081, 7696.615103],
    [2050, 8374.279046, -445.045081, 7929.233965], [2051, 8606.897908, -445.045081, 8161.852827],
    [2052, 8839.516771, -445.045081, 8394.471690], [2053, 9072.135633, -445.045081, 8627.090552],
    [2054, 9304.754495, -445.045081, 8859.709415], [2055, 9537.373358, -445.045081, 9092.328277],
    [2056, 9769.992220, -445.045081, 9324.947139], [2057, 10002.611082, -445.045081, 9557.566002],
    [2058, 10235.229945, -445.045081, 9790.184864], [2059, 10467.848807, -445.045081, 10022.803727],
    [2060, 10700.467670, -445.045081, 10255.422589]]

# 'Adoption Data'!CF50:CI96
poly_degree2_trend_global_list = [['Year', 'x^2', 'x', 'constant', 'adoption'],
    [2014, 0.000000, 0.000000, -216.892778, -216.892778],
    [2015, 0.803353, 197.271322, -216.892778, -18.818102],
    [2016, 3.213413, 394.542645, -216.892778, 180.863280],
    [2017, 7.230179, 591.813967, -216.892778, 382.151368],
    [2018, 12.853651, 789.085290, -216.892778, 585.046163],
    [2019, 20.083829, 986.356612, -216.892778, 789.547664],
    [2020, 28.920714, 1183.627935, -216.892778, 995.655872],
    [2021, 39.364306, 1380.899257, -216.892778, 1203.370786],
    [2022, 51.414603, 1578.170580, -216.892778, 1412.692406],
    [2023, 65.071608, 1775.441902, -216.892778, 1623.620732],
    [2024, 80.335318, 1972.713225, -216.892778, 1836.155765],
    [2025, 97.205735, 2169.984547, -216.892778, 2050.297504],
    [2026, 115.682858, 2367.255870, -216.892778, 2266.045950],
    [2027, 135.766687, 2564.527192, -216.892778, 2483.401102],
    [2028, 157.457223, 2761.798515, -216.892778, 2702.362960],
    [2029, 180.754465, 2959.069837, -216.892778, 2922.931525],
    [2030, 205.658414, 3156.341160, -216.892778, 3145.106796],
    [2031, 232.169069, 3353.612482, -216.892778, 3368.888773],
    [2032, 260.286430, 3550.883805, -216.892778, 3594.277457],
    [2033, 290.010498, 3748.155127, -216.892778, 3821.272847],
    [2034, 321.341272, 3945.426450, -216.892778, 4049.874944],
    [2035, 354.278752, 4142.697772, -216.892778, 4280.083747],
    [2036, 388.822939, 4339.969095, -216.892778, 4511.899256],
    [2037, 424.973832, 4537.240417, -216.892778, 4745.321471],
    [2038, 462.731431, 4734.511739, -216.892778, 4980.350393],
    [2039, 502.095737, 4931.783062, -216.892778, 5216.986022],
    [2040, 543.066749, 5129.054384, -216.892778, 5455.228356],
    [2041, 585.644468, 5326.325707, -216.892778, 5695.077397],
    [2042, 629.828893, 5523.597029, -216.892778, 5936.533145],
    [2043, 675.620024, 5720.868352, -216.892778, 6179.595598],
    [2044, 723.017862, 5918.139674, -216.892778, 6424.264758],
    [2045, 772.022406, 6115.410997, -216.892778, 6670.540625],
    [2046, 822.633656, 6312.682319, -216.892778, 6918.423198],
    [2047, 874.851613, 6509.953642, -216.892778, 7167.912477],
    [2048, 928.676276, 6707.224964, -216.892778, 7419.008462],
    [2049, 984.107645, 6904.496287, -216.892778, 7671.711154],
    [2050, 1041.145721, 7101.767609, -216.892778, 7926.020552],
    [2051, 1099.790503, 7299.038932, -216.892778, 8181.936657],
    [2052, 1160.041991, 7496.310254, -216.892778, 8439.459468],
    [2053, 1221.900186, 7693.581577, -216.892778, 8698.588985],
    [2054, 1285.365087, 7890.852899, -216.892778, 8959.325209],
    [2055, 1350.436695, 8088.124222, -216.892778, 9221.668139],
    [2056, 1417.115009, 8285.395544, -216.892778, 9485.617775],
    [2057, 1485.400029, 8482.666867, -216.892778, 9751.174118],
    [2058, 1555.291756, 8679.938189, -216.892778, 10018.337167],
    [2059, 1626.790189, 8877.209511, -216.892778, 10287.106923],
    [2060, 1699.895328, 9074.480834, -216.892778, 10557.483384]]

# 'Adoption Data'!CN50:CR96
poly_degree3_trend_global_list = [['Year', 'x^3', 'x^2', 'x', 'constant', 'adoption'],
    [2014, 0.000000, 0.000000, 0.000000, 111.343842, 111.343842],
    [2015, -0.120128, 8.731774, 66.067972, 111.343842, 186.023460],
    [2016, -0.961021, 34.927096, 132.135943, 111.343842, 277.445860],
    [2017, -3.243445, 78.585966, 198.203915, 111.343842, 384.890277],
    [2018, -7.688166, 139.708383, 264.271886, 111.343842, 507.635946],
    [2019, -15.015948, 218.294349, 330.339858, 111.343842, 644.962100],
    [2020, -25.947559, 314.343862, 396.407829, 111.343842, 796.147975],
    [2021, -41.203762, 427.856923, 462.475801, 111.343842, 960.472804],
    [2022, -61.505325, 558.833532, 528.543773, 111.343842, 1137.215822],
    [2023, -87.573011, 707.273690, 594.611744, 111.343842, 1325.656265],
    [2024, -120.127587, 873.177394, 660.679716, 111.343842, 1525.073365],
    [2025, -159.889819, 1056.544647, 726.747687, 111.343842, 1734.746358],
    [2026, -207.580471, 1257.375448, 792.815659, 111.343842, 1953.954478],
    [2027, -263.920309, 1475.669797, 858.883630, 111.343842, 2181.976960],
    [2028, -329.630100, 1711.427693, 924.951602, 111.343842, 2418.093038],
    [2029, -405.430607, 1964.649138, 991.019574, 111.343842, 2661.581946],
    [2030, -492.042598, 2235.334130, 1057.087545, 111.343842, 2911.722919],
    [2031, -590.186837, 2523.482670, 1123.155517, 111.343842, 3167.795192],
    [2032, -700.584089, 2829.094758, 1189.223488, 111.343842, 3429.077999],
    [2033, -823.955122, 3152.170394, 1255.291460, 111.343842, 3694.850574],
    [2034, -961.020699, 3492.709578, 1321.359431, 111.343842, 3964.392153],
    [2035, -1112.501586, 3850.712310, 1387.427403, 111.343842, 4236.981968],
    [2036, -1279.118550, 4226.178589, 1453.495375, 111.343842, 4511.899256],
    [2037, -1461.592355, 4619.108417, 1519.563346, 111.343842, 4788.423250],
    [2038, -1660.643768, 5029.501792, 1585.631318, 111.343842, 5065.833184],
    [2039, -1876.993552, 5457.358715, 1651.699289, 111.343842, 5343.408295],
    [2040, -2111.362475, 5902.679187, 1717.767261, 111.343842, 5620.427814],
    [2041, -2364.471302, 6365.463206, 1783.835233, 111.343842, 5896.170978],
    [2042, -2637.040798, 6845.710773, 1849.903204, 111.343842, 6169.917021],
    [2043, -2929.791728, 7343.421888, 1915.971176, 111.343842, 6440.945177],
    [2044, -3243.444858, 7858.596550, 1982.039147, 111.343842, 6708.534681],
    [2045, -3578.720955, 8391.234761, 2048.107119, 111.343842, 6971.964767],
    [2046, -3936.340782, 8941.336519, 2114.175090, 111.343842, 7230.514670],
    [2047, -4317.025107, 9508.901826, 2180.243062, 111.343842, 7483.463623],
    [2048, -4721.494693, 10093.930680, 2246.311034, 111.343842, 7730.090862],
    [2049, -5150.470308, 10696.423082, 2312.379005, 111.343842, 7969.675622],
    [2050, -5604.672715, 11316.379032, 2378.446977, 111.343842, 8201.497136],
    [2051, -6084.822682, 11953.798530, 2444.514948, 111.343842, 8424.834639],
    [2052, -6591.640973, 12608.681576, 2510.582920, 111.343842, 8638.967365],
    [2053, -7125.848354, 13281.028170, 2576.650891, 111.343842, 8843.174549],
    [2054, -7688.165590, 13970.838312, 2642.718863, 111.343842, 9036.735426],
    [2055, -8279.313448, 14678.112001, 2708.786835, 111.343842, 9218.929230],
    [2056, -8900.012692, 15402.849239, 2774.854806, 111.343842, 9389.035195],
    [2057, -9550.984087, 16145.050024, 2840.922778, 111.343842, 9546.332556],
    [2058, -10232.948401, 16904.714357, 2906.990749, 111.343842, 9690.100548],
    [2059, -10946.626397, 17681.842238, 2973.058721, 111.343842, 9819.618404],
    [2060, -11692.738842, 18476.433667, 3039.126692, 111.343842, 9934.165359]]

# 'Adoption Data'!CW50:CY96
exponential_trend_global_list = [['Year', 'coeff', 'e^x', 'adoption'],
    [2014, 401.463348, 1.000000, 401.463348], [2015, 401.463348, 1.090876, 437.946633],
    [2016, 401.463348, 1.190010, 477.745364], [2017, 401.463348, 1.298153, 521.160835],
    [2018, 401.463348, 1.416124, 568.521719], [2019, 401.463348, 1.544815, 620.186560],
    [2020, 401.463348, 1.685201, 676.546481], [2021, 401.463348, 1.838345, 738.028154],
    [2022, 401.463348, 2.005406, 805.097019], [2023, 401.463348, 2.187649, 878.260819],
    [2024, 401.463348, 2.386453, 958.073433], [2025, 401.463348, 2.603324, 1045.139080],
    [2026, 401.463348, 2.839903, 1140.116883], [2027, 401.463348, 3.097981, 1243.725865],
    [2028, 401.463348, 3.379512, 1356.750392], [2029, 401.463348, 3.686628, 1480.046108],
    [2030, 401.463348, 4.021653, 1614.546416], [2031, 401.463348, 4.387124, 1761.269540],
    [2032, 401.463348, 4.785807, 1921.326239], [2033, 401.463348, 5.220721, 2095.928212],
    [2034, 401.463348, 5.695158, 2286.397270], [2035, 401.463348, 6.212710, 2494.175348],
    [2036, 401.463348, 6.777295, 2720.835416], [2037, 401.463348, 7.393186, 2968.093388],
    [2038, 401.463348, 8.065048, 3237.821116], [2039, 401.463348, 8.797965, 3532.060554],
    [2040, 401.463348, 9.597487, 3853.039223], [2041, 401.463348, 10.469666, 4203.187071],
    [2042, 401.463348, 11.421105, 4585.154869], [2043, 401.463348, 12.459006, 5001.834279],
    [2044, 401.463348, 13.591228, 5456.379745], [2045, 401.463348, 14.826341, 5952.232374],
    [2046, 401.463348, 16.173696, 6493.145984], [2047, 401.463348, 17.643492, 7083.215528],
    [2048, 401.463348, 19.246858, 7726.908086], [2049, 401.463348, 20.995931, 8429.096691],
    [2050, 401.463348, 22.903952, 9195.097216], [2051, 401.463348, 24.985366, 10030.708618],
    [2052, 401.463348, 27.255930, 10942.256836], [2053, 401.463348, 29.732833, 11936.642686],
    [2054, 401.463348, 32.434827, 13021.394101], [2055, 401.463348, 35.382366, 14204.723120],
    [2056, 401.463348, 38.597765, 15495.588057], [2057, 401.463348, 42.105366, 16903.761320],
    [2058, 401.463348, 45.931723, 18439.903391], [2059, 401.463348, 50.105803, 20115.643532],
    [2060, 401.463348, 54.659206, 21943.667824]]
