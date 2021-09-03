
import pytest

from solution.macroalgaerestoration.macroalgaerestoration_solution import MacroalgaeRestorationSolution

solution_name = 'macroalgaerestoration'
scenario_name = 'PDS-16p2050-Optimum 20August2021'
mars = MacroalgaeRestorationSolution()
mars.load_scenario(scenario_name)

def test_adoption_unit_increase_pds_vs_ref_final_year():
    au_inc = mars.get_adoption_unit_increase_pds_vs_ref_final_year()
    assert au_inc == pytest.approx(33.61214819960)
    
def test_adoption_unit_increase_pds_final_year():
    gu_final = mars.get_adoption_unit_increase_pds_final_year()
    assert gu_final == pytest.approx(33.61214819960)
    
def test_global_percent_adoption_base_year():
    gpa_base = mars.get_global_percent_adoption_base_year()
    assert gpa_base == pytest.approx(0.0 / 100)
    
def test_percent_adoption_start_year():
    gpa_start = mars.get_percent_adoption_start_year()
    assert gpa_start == pytest.approx(1.0609895265/ 100)
    
def test_get_percent_adoption_end_year():
    gpa_end = mars.get_percent_adoption_end_year()
    assert gpa_end == pytest.approx(16.9758324240 / 100)

######

def test_total_co2_seq():
    total_co2_seq = mars.get_total_co2_seq()
    assert total_co2_seq == pytest.approx(1.952028234)

def test_change_in_ppm_equivalent():
    change_in_ppm_equivalent = mars.get_change_in_ppm_equivalent()
    assert change_in_ppm_equivalent == pytest.approx(0.1651159440)

def test_change_in_ppm_equivalent_final():
    change_in_ppm_equivalent_final = mars.get_change_in_ppm_equivalent_final_year()
    assert change_in_ppm_equivalent_final == pytest.approx(0.0092167686)

def test_max_annual_co2_sequestered():
    max_annual_co2_sequestered = mars.get_max_annual_co2_sequestered()
    assert max_annual_co2_sequestered == pytest.approx(0.1189807685)

def test_co2_sequestered_final_year():
    co2_sequestered_final_year = mars.get_co2_sequestered_final_year()
    assert co2_sequestered_final_year == pytest.approx(0.1189807685)
