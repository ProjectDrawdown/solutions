
import pytest

from solution.seaweedfarming.seaweedfarming_solution import SeaweedFarmingSolution

solution_name = 'seaweedfarming'
scenario_name = 'PDS-5p2050-Plausible NEW 240 TOA'
swf = SeaweedFarmingSolution()
swf.load_scenario(scenario_name)

def test_adoption_unit_increase_final_year():
    au_inc = swf.get_adoption_unit_increase_final_year('World')
    assert au_inc == pytest.approx(13.201921)
    
def test_adoption_unit_pds_final_year():
    gu_final = swf.get_adoption_unit_pds_final_year('World')
    assert gu_final == pytest.approx(13.389328)
    
def test_global_percent_adoption_base_year():
    gpa_base = swf.get_global_percent_adoption_base_year('World')
    assert gpa_base == pytest.approx(0.07808635 / 100)
    
def test_percent_adoption_start_year():
    gpa_start = swf.get_percent_adoption_start_year('World')
    assert gpa_start == pytest.approx(0.42188637 / 100)
    
def test_get_percent_adoption_end_year():
    gpa_end = swf.get_percent_adoption_end_year('World')
    assert gpa_end == pytest.approx(5.57888670 / 100)


def test_marginal_first_cost():
    first_cost = swf.get_marginal_first_cost('World')
    assert first_cost == pytest.approx(132.137293)

def test_operating_cost():
    operating_cost = swf.get_operating_cost('World')
    assert operating_cost == pytest.approx(-2559.622236)

def test_lifetime_operating_savings():
    lifetime_operating_savings = swf.get_lifetime_operating_savings('World')
    assert lifetime_operating_savings == pytest.approx(-4972.980344)

def test_cumulative_first_cost():
    cumulative_first_cost = swf.get_cumulative_first_cost_pds('World')
    assert cumulative_first_cost == pytest.approx(132.517928)

def test_lifetime_cashflow_npv_single():
    lifetime_cashflow_npv_single = swf.get_lifetime_cashflow_npv_single( 'World', purchase_year = 2017)
    assert lifetime_cashflow_npv_single == pytest.approx(-97.555759)

def test_lifetime_cashflow_npv_all():
    lifetime_cashflow_npv_all = swf.get_lifetime_cashflow_npv_all('World')
    assert lifetime_cashflow_npv_all == pytest.approx(-358.572118)

def test_payback_period_soln_to_conv():
    payback_period_soln_to_conv = swf.get_payback_period_soln_to_conv('World', purchase_year = 2017)
    payback_period_soln_to_conv = max(payback_period_soln_to_conv, 0.0)
    assert payback_period_soln_to_conv == 0.0 # 0.0 = 'Never'

def test_payback_period_soln_to_conv_npv():
    payback_period_soln_to_conv_npv = swf.get_payback_period_soln_to_conv_npv('World', purchase_year = 2017)
    payback_period_soln_to_conv_npv = max(payback_period_soln_to_conv_npv, 0.0)
    assert payback_period_soln_to_conv_npv == 0.0 # 0.0 = 'Never'

def test_payback_period_soln_only():
    payback_period_soln_only = swf.get_payback_period_soln_only('World', purchase_year = 2017)
    payback_period_soln_only = max(payback_period_soln_only, 0.0)
    assert payback_period_soln_only == 0.0 # -1 = 'Never'

def test_payback_period_soln_only_npv():
    payback_period_soln_only_npv = swf.get_payback_period_soln_only_npv('World', purchase_year = 2017)
    payback_period_soln_only_npv = max(payback_period_soln_only_npv, 0.0)
    assert payback_period_soln_only_npv == 0.0 # 0.0 = 'Never'

def test_abatement_cost():
    abatement_cost = swf.get_abatement_cost('World')
    assert abatement_cost == pytest.approx(127.776530)

def test_net_profit_margin():
    net_profit_margin = swf.get_net_profit_margin('World')    
    assert net_profit_margin == pytest.approx(2736.688095)

def test_lifetime_profit_margin():
    lifetime_profit_margin = swf.get_lifetime_profit_margin('World')
    assert lifetime_profit_margin == pytest.approx(5316.994012)

def test_total_co2_seq():
    total_co2_seq = swf.get_total_co2_seq('World')
    assert total_co2_seq == pytest.approx(2.49773912913679)

def test_change_in_ppm_equiv():
    change_in_ppm_equiv = swf.get_change_in_ppm_equiv('World')
    assert change_in_ppm_equiv == pytest.approx(0.21127592)

def test_change_in_ppm_equiv_final():
    change_in_ppm_equiv_final = swf.get_change_in_ppm_equiv_final_year('World')
    assert change_in_ppm_equiv_final == pytest.approx(0.0117934173530898)

def test_max_annual_co2_sequestered():
    max_annual_co2_sequestered = swf.get_max_annual_co2_sequestered('World')
    assert max_annual_co2_sequestered == pytest.approx(0.152243146918814)

def test_co2_sequestered_final_year():
    co2_sequestered_final_year = swf.get_co2_sequestered_final_year('World')
    assert co2_sequestered_final_year == pytest.approx(0.152243146918814)
