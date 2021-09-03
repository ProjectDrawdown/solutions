
import pytest

from solution.seafloorprotection.seafloorprotection_solution import SeafloorProtectionSolution

solution_name = 'seafloorprotection'
scenario_name = 'PDS-48p2050-Optimum'
sps = SeafloorProtectionSolution()
sps.load_scenario(scenario_name)

def test_adoption_unit_increase_pds_vs_ref_final_year():
    au_inc = sps.get_adoption_unit_increase_pds_vs_ref_final_year()
    assert au_inc == pytest.approx(441.00)
    
def test_adoption_unit_increase_pds_final_year():
    gu_final = sps.get_adoption_unit_increase_pds_final_year()
    assert gu_final == pytest.approx(441.00)
    
def test_global_percent_adoption_base_year():
    gpa_base = sps.get_global_percent_adoption_base_year()
    assert gpa_base == pytest.approx(0.0 / 100)
    
def test_percent_adoption_start_year():
    gpa_start = sps.get_percent_adoption_start_year()
    assert gpa_start == pytest.approx(5.625/ 100)
    
def test_get_percent_adoption_end_year():
    gpa_end = sps.get_percent_adoption_end_year()
    assert gpa_end == pytest.approx(90.00 / 100)

######

def test_total_emissions_reduction():
    total_emissions_reduction = sps.get_total_emissions_reduction()
    assert total_emissions_reduction == pytest.approx(5.91011393970)

def test_total_co2_seq():
    total_co2_seq = sps.get_total_co2_seq()
    assert total_co2_seq == 0.0

def test_reduced_area_degradation():
    reduced_area_degradation = sps.get_reduced_area_degradation()
    assert reduced_area_degradation == 427.21875000

def test_max_annual_emissions_reduction():
    max_annual_emissions_reduction = sps.get_max_annual_emissions_reduction()
    assert max_annual_emissions_reduction == pytest.approx(0.19064883676)

def test_emissions_reduction_final_year():
    emissions_reduction_final_year = sps.get_emissions_reduction_final_year()
    assert emissions_reduction_final_year == pytest.approx(0.19064883676)
    
@pytest.mark.skip(reason="currently fails, under investigation")
def test_change_in_ppm_equivalent():
    change_in_ppm_equivalent = sps.get_change_in_ppm_equivalent()
    assert change_in_ppm_equivalent == pytest.approx(0.4607453935)

def test_change_in_ppm_equivalent_final():
    change_in_ppm_equivalent_final = sps.get_change_in_ppm_equivalent_final_year()
    assert change_in_ppm_equivalent_final == pytest.approx(0.01195646244)

def test_max_annual_co2_sequestered():
    max_annual_co2_sequestered = sps.get_max_annual_co2_sequestered()
    assert max_annual_co2_sequestered == 0.0

def test_co2_sequestered_final_year():
    co2_sequestered_final_year = sps.get_co2_sequestered_final_year()
    assert co2_sequestered_final_year == 0.0


