
import pandas as pd
from seaweedfarming_solution import SeaweedFarmingSolution

def main():
    
    swf = SeaweedFarmingSolution()

    scenario_names = ['PDS-5p2050-Plausible NEW 240 TOA']

    for sc in scenario_names:
        print()
        print(sc)
        swf.load_scenario(sc)
        swf.set_up_tam()

        results = {}
        
        au_inc = swf.get_adoption_unit_increase_pds_vs_ref_final_year('World')
        gu_final = swf.get_adoption_unit_increase_pds_final_year('World')
        gpa_base = swf.get_global_percent_adoption_base_year('World') #returns base year +1?
        gpa_start = swf.get_percent_adoption_start_year('World')
        gpa_end = swf.get_percent_adoption_end_year('World')

        results['Adoption Unit Increase Second Year (PDS vs REF)'] = [au_inc, 13.201921]
        results['Global Units of Adoption in Second Year'] = [gu_final, 13.389328]
        results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 0.07808635 / 100]
        results['Global Percent Adoption in First Year'] = [gpa_start, 0.42188637 / 100]
        results['Global Percent Adoption in Second Year (2050)'] = [gpa_end, 5.57888670 / 100]


        first_cost = swf.get_marginal_first_cost('World')
        results['first_cost'] = [first_cost, 132.137293]

        operating_cost = swf.get_operating_cost('World')
        results['operating_cost'] = [operating_cost, -2559.622236]

        lifetime_operating_savings = swf.get_lifetime_operating_savings('World')
        results['lifetime_operating_savings'] = [lifetime_operating_savings, -4972.980344]
        
        cumulative_first_cost = swf.get_cumulative_first_cost_pds('World')
        results['cumulative_first_cost'] = [cumulative_first_cost, 132.517928]

        lifetime_cashflow_npv_single = swf.get_lifetime_cashflow_npv_single( 'World', purchase_year = 2017)
        results['lifetime_cashflow_npv_single'] = [lifetime_cashflow_npv_single, -97.555759]

        lifetime_cashflow_npv_all = swf.get_lifetime_cashflow_npv_all('World')
        results['lifetime_cashflow_npv_all'] = [lifetime_cashflow_npv_all, -358.572118]


        payback_period_soln_to_conv = swf.get_payback_period_soln_to_conv('World', purchase_year = 2017)
        results['payback_period_soln_to_conv'] = [max(payback_period_soln_to_conv, 0.0), 0.0] # 0.0 = 'Never'

        payback_period_soln_to_conv_npv = swf.get_payback_period_soln_to_conv_npv('World', purchase_year = 2017)
        results['payback_period_soln_to_conv_npv'] = [max(payback_period_soln_to_conv_npv, 0.0), 0.0] # 0.0 = 'Never'

        payback_period_soln_only = swf.get_payback_period_soln_only('World', purchase_year = 2017)
        results['payback_period_soln_only'] = [max(payback_period_soln_only, 0.0), 0.0] # -1 = 'Never'

        payback_period_soln_only_npv = swf.get_payback_period_soln_only_npv('World', purchase_year = 2017)
        results['payback_period_soln_only_npv'] = [max(payback_period_soln_only_npv, 0.0), 0.0] # 0.0 = 'Never'

        abatement_cost = swf.get_abatement_cost('World')
        results['abatement_cost'] = [abatement_cost, 127.776530]

        net_profit_margin = swf.get_net_profit_margin('World')
        results['net_profit_margin'] = [net_profit_margin, 2736.688095]

        lifetime_profit_margin = swf.get_lifetime_profit_margin('World')
        results['lifetime_profit_margin'] = [lifetime_profit_margin, 5316.994012]

        total_co2_seq = swf.get_total_co2_seq('World')
        results['total_co2_seq'] = [total_co2_seq, 2.49773912913679]

        change_in_ppm_equiv = swf.get_change_in_ppm_equiv('World')
        results['change_in_ppm_equiv'] = [change_in_ppm_equiv, 0.21127592]

        change_in_ppm_equiv_final = swf.get_change_in_ppm_equiv_final_year('World')
        results['change_in_ppm_equiv_final'] = [change_in_ppm_equiv_final, 0.0117934173530898]

        max_annual_co2_sequestered = swf.get_max_annual_co2_sequestered('World')
        results['max_annual_co2_sequestered'] = [max_annual_co2_sequestered, 0.152243146918814]

        co2_sequestered_final_year = swf.get_co2_sequestered_final_year('World')
        results['co2_sequestered_final_year'] = [co2_sequestered_final_year, 0.152243146918814]

        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




