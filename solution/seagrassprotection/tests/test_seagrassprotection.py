import pytest
import pandas as pd

from solution.seagrassprotection.seagrassprotection_solution import SeagrassProtectionSolution

solution_name = 'seagrassprotection'
scenario_name = 'PDS-69p2050-Maximum JULY2021'
sps = SeagrassProtectionSolution()
sps.load_scenario(scenario_name)


def test_adoption_unit_increase_pds_vs_ref_final_year():
    au_inc = sps.get_adoption_unit_increase_pds_vs_ref_final_year()
    assert au_inc == pytest.approx(11.9209315305)
    
def test_adoption_unit_increase_pds_final_year():
    gu_final = sps.get_adoption_unit_increase_pds_final_year()
    assert gu_final == pytest.approx(17.865258686292)
    
def test_global_percent_adoption_base_year():
    gpa_base = sps.get_global_percent_adoption_base_year()
    assert gpa_base == pytest.approx(23.1025 / 100)
    
def test_percent_adoption_start_year():
    gpa_start = sps.get_percent_adoption_start_year()
    assert gpa_start == pytest.approx(31.3385777675664 / 100)
    
def test_get_percent_adoption_end_year():
    gpa_end = sps.get_percent_adoption_end_year()
    assert gpa_end == pytest.approx(69.4329447185686 / 100)

######


### Start - Test CO2 Calcs ###

## Start Emissions Reduction tests ##

def test_emissions_reduction_series():

    desired_result = pd.io.json.read_json('solution/seagrassprotection/tests/emissions_reduction_series.json', typ='series')

    emissions_reduction_series = sps.get_emissions_reduction_series()

    pd.testing.assert_series_equal(emissions_reduction_series, desired_result, check_names = False)

# if test_co2_eq_MMT_reduced() above passes then this section will too.

def test_total_emissions_reduction():
    total_emissions_reduction = sps.get_total_emissions_reduction()
    assert  total_emissions_reduction == pytest.approx( 0.288891735240484)
    
def test_max_annual_emissions_reduction():
    max_annual_emissions_reduction = sps.get_max_annual_emissions_reduction()
    assert max_annual_emissions_reduction == pytest.approx( 0.019406158529)

def test_emissions_reduction_final_year():
    emissions_reduction_final_year = sps.get_emissions_reduction_final_year()
    assert emissions_reduction_final_year == pytest.approx( 0.0194061585293477)


## End Emissions Reduction tests ##


## Start Carbon Sequestration tests ##
    
def test_carbon_sequestration_series():
    
    desired_result = pd.io.json.read_json('solution/seagrassprotection/tests/carbon_sequestration_series.json', typ='series')

    carbon_sequestration_series = sps.get_carbon_sequestration_series()

    pd.testing.assert_series_equal(carbon_sequestration_series, desired_result, check_names = False)

# if test_carbon_sequestration_series() above passes then this section will too.

def test_total_co2_sequestered():
    total_co2_seq = sps.get_total_co2_sequestered()
    assert total_co2_seq == pytest.approx( 0.359513049174938)

def test_max_annual_co2_sequestered():
    max_annual_co2_sequestered = sps.get_max_annual_co2_sequestered()
    assert max_annual_co2_sequestered == pytest.approx( 0.0251612427386)

def test_co2_sequestered_final_year():
    co2_sequestered_final_year = sps.get_co2_sequestered_final_year()
    assert co2_sequestered_final_year == pytest.approx( 0.0251612427385857)

## End Carbon Sequestration tests ##

## Start PPM Equivalent tests ##

def test_change_in_ppm_equivalent_series():
    
    desired_result = pd.io.json.read_json('solution/seagrassprotection/tests/change_in_ppm_equivalent_series.json', typ='series')

    change_in_ppm_equivalent_series = sps.get_change_in_ppm_equivalent_series()

    pd.testing.assert_series_equal(change_in_ppm_equivalent_series, desired_result, check_names = False)


# @pytest.mark.skip(reason="currently fails, under investigation")
def test_change_in_ppm_equivalent():
    change_in_ppm_equivalent = sps.get_change_in_ppm_equivalent()
    assert change_in_ppm_equivalent == pytest.approx( 0.0558909304494364)

# @pytest.mark.skip(reason="currently fails, under investigation")
def test_change_in_ppm_equivalent_final():
    change_in_ppm_equiv_final = sps.get_change_in_ppm_equivalent_final_year()
    assert change_in_ppm_equiv_final == pytest.approx(  0.00352600148886495)

## End PPM Equivalent tests ##

## Start Unit Area tests ##

def test_reduced_area_degradation():
    reduced_area_degradation = sps.get_reduced_area_degradation()
    assert reduced_area_degradation == pytest.approx( 5.27946407538824)

def test_co2_under_protection_final_year():
    co2_under_protection_final_year = sps.get_co2_under_protection_final_year()
    assert co2_under_protection_final_year == pytest.approx( 14.6933270416904)

def test_carbon_under_protection_final_year():
    carbon_under_protection_final_year = sps.get_carbon_under_protection_final_year()
    assert carbon_under_protection_final_year == pytest.approx( 4.01018751137840)

## End Unit Area tests ##

### End CO2 Calcs ###
