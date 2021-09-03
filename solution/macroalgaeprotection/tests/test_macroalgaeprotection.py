
import pytest

from solution.macroalgaeprotection.macroalgaeprotection_solution import MacroalgaeProtectionSolution

solution_name = 'macroalgaeprotection'
scenario_name = 'PDS-53p2050-Optimum'
maps = MacroalgaeProtectionSolution()
maps.load_scenario(scenario_name)

def test_adoption_unit_increase_pds_vs_ref_final_year():
    au_inc = maps.get_adoption_unit_increase_pds_vs_ref_final_year()
    assert au_inc == pytest.approx(265.0)
    
def test_adoption_unit_increase_pds_final_year():
    gu_final = maps.get_adoption_unit_increase_pds_final_year()
    assert gu_final == pytest.approx(265.0)
    
def test_global_percent_adoption_base_year():
    gpa_base = maps.get_global_percent_adoption_base_year()
    assert gpa_base == pytest.approx(0.00)
    
def test_percent_adoption_start_year():
    gpa_start = maps.get_percent_adoption_start_year()
    assert gpa_start == pytest.approx(6.2506050207 / 100, 1e-04)
    
def test_get_percent_adoption_end_year():
    gpa_end = maps.get_percent_adoption_end_year()
    assert gpa_end == pytest.approx(74.7012373290 / 100, 1e-04)

######

def test_total_co2_seq():
    total_co2_seq = maps.get_total_co2_seq()
    assert total_co2_seq == pytest.approx(3.85598888)

def test_change_in_ppm_equivalent():
    change_in_ppm_equivalent = maps.get_change_in_ppm_equivalent()
    assert change_in_ppm_equivalent == pytest.approx(0.339684712828728)

@pytest.mark.skip(reason="currently fails, under investigation")
def test_change_in_ppm_equivalent_final():
    change_in_ppm_equivalent_final = maps.get_change_in_ppm_equivalent_final_year()
    assert change_in_ppm_equivalent_final == pytest.approx(0.027045695545894)

def test_max_annual_co2_sequestered():
    max_annual_co2_sequestered = maps.get_max_annual_co2_sequestered()
    assert max_annual_co2_sequestered == pytest.approx(0.326041958295943)

def test_co2_sequestered_final_year():
    co2_sequestered_final_year = maps.get_co2_sequestered_final_year()
    assert co2_sequestered_final_year == pytest.approx(0.326041958295943)
