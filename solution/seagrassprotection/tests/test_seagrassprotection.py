
import pytest

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

def test_total_emissions_reduction():
    total_emissions_reduction = sps.get_total_emissions_reduction()
    assert  total_emissions_reduction == pytest.approx( 0.288891735240484)

def test_total_co2_seq():
    total_co2_seq = sps.get_total_co2_seq()
    assert total_co2_seq == pytest.approx( 0.359513049174938)

def test_max_annual_co2_sequestered():
    max_annual_co2_sequestered = sps.get_max_annual_co2_sequestered()
    assert max_annual_co2_sequestered == pytest.approx( 0.0251612427386)

def test_emissions_reduction_final_year():
    emissions_reduction_final_year = sps.get_emissions_reduction_final_year()
    assert emissions_reduction_final_year == pytest.approx( 0.0194061585293477)

@pytest.mark.skip(reason="currently fails, under investigation")
def test_change_in_ppm_equivalent():
    change_in_ppm_equivalent = sps.get_change_in_ppm_equivalent()
    assert change_in_ppm_equivalent == pytest.approx( 0.0558909304494364)

@pytest.mark.skip(reason="currently fails, under investigation")
def test_change_in_ppm_equivalent_final():
    change_in_ppm_equiv_final = sps.get_change_in_ppm_equivalent_final_year()
    assert change_in_ppm_equiv_final == pytest.approx(  0.00352600148886495)

def test_co2_sequestered_final_year():
    co2_sequestered_final_year = sps.get_co2_sequestered_final_year()
    assert co2_sequestered_final_year == pytest.approx( 0.0251612427385857)

def test_reduced_area_degradation():
    reduced_area_degradation = sps.get_reduced_area_degradation()
    assert reduced_area_degradation == pytest.approx( 5.27946407538824)

def test_co2_under_protection_final_year():
    co2_under_protection_final_year = sps.get_co2_under_protection_final_year()
    assert co2_under_protection_final_year == pytest.approx( 14.6933270416904)

def test_carbon_under_protection_final_year():
    carbon_under_protection_final_year = sps.get_carbon_under_protection_final_year()
    assert carbon_under_protection_final_year == pytest.approx( 4.01018751137840)

def test_max_annual_emissions_reduction():
    max_annual_emissions_reduction = sps.get_max_annual_emissions_reduction()
    assert max_annual_emissions_reduction == pytest.approx( 0.019406158529)

def test_annual_emissions_reduction_final_year():
    annual_emissions_reduction_final_year = sps.get_annual_emissions_reduction_final_year()
    assert annual_emissions_reduction_final_year == pytest.approx( 0.019406158529)
