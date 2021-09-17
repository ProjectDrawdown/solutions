
import pandas as pd
from seaweedfarming_solution import SeaweedFarmingSolution

def main():
    
    swf = SeaweedFarmingSolution()

    scenario_names = ['PDS-10p2050-Drawdown New 240 TOA']

    for sc in scenario_names:
        print()
        print(sc)
        swf.load_scenario(sc)

        results = {}

        
        # au_inc = swf.get_adoption_unit_increase_pds_vs_ref_final_year()
        # results['Adoption Unit Increase Second Year (PDS vs REF)'] = [au_inc, 13.201921]

        # gu_final = swf.get_adoption_unit_increase_pds_final_year()
        # results['Global Units of Adoption in Second Year'] = [gu_final, 13.389328]

        # gpa_base = swf.get_global_percent_adoption_base_year() #returns base year +1?
        # results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 0.07808635 / 100]

        # gpa_start = swf.get_percent_adoption_start_year()
        # results['Global Percent Adoption in First Year'] = [gpa_start, 0.42188637 / 100]

        # gpa_end = swf.get_percent_adoption_end_year()
        # results['Global Percent Adoption in Second Year (2050)'] = [gpa_end, 5.57888670 / 100]

        first_cost = swf.get_marginal_first_cost()
        results['Marginal First Cost 2015-2050'] = [first_cost, 132.137293]

        # operating_cost = swf.get_operating_cost()
        # results['Net Operating Savings 2020-2050'] = [operating_cost, -2559.622236]

        # lifetime_operating_savings = swf.get_lifetime_operating_savings()
        # results['Lifetime Operating Savings 2020-2050'] = [lifetime_operating_savings, -4972.980344]
        
        # cumulative_first_cost = swf.get_cumulative_first_cost_pds()
        # results['Cumulative First Cost 2015 -2050'] = [cumulative_first_cost, 132.517928]

        # lifetime_cashflow_npv_single = swf.get_lifetime_cashflow_npv_single(purchase_year = 2017)
        # results['Lifetime Cashflow NPV of a Single Implementation Unit (PDS compared to REF Scenario)'] = [lifetime_cashflow_npv_single, -97.555759]

        # lifetime_cashflow_npv_all = swf.get_lifetime_cashflow_npv_all()
        # results['Lifetime Cashflow NPV of All Implementation Units (PDS compared to REF Scenario)'] = [lifetime_cashflow_npv_all, -358.572118]


        # payback_period_soln_to_conv = swf.get_payback_period_soln_to_conv(purchase_year = 2017)
        # results['Payback Period Solution Relative to Conventional'] = [max(payback_period_soln_to_conv, 0.0), 0.0] # 0.0 = 'Never'

        # payback_period_soln_to_conv_npv = swf.get_payback_period_soln_to_conv_npv(purchase_year = 2017)
        # results['Discounted Payback Period Solution Relative to Conventional'] = [max(payback_period_soln_to_conv_npv, 0.0), 0.0] # 0.0 = 'Never'

        # payback_period_soln_only = swf.get_payback_period_soln_only(purchase_year = 2017)
        # results['Payback Period Solution Alone'] = [max(payback_period_soln_only, 0.0), 0.0] # -1 = 'Never'

        # payback_period_soln_only_npv = swf.get_payback_period_soln_only_npv(purchase_year = 2017)
        # results['Discounted Payback Period Solution Alone'] = [max(payback_period_soln_only_npv, 0.0), 0.0] # 0.0 = 'Never'

        # abatement_cost = swf.get_abatement_cost()
        # results['Average Abatement Cost 2020-2050'] = [abatement_cost, 127.776530]

        # net_profit_margin = swf.get_net_profit_margin()
        # results['Net Profit Margin 2020-2050'] = [net_profit_margin, 2736.688095]

        # lifetime_profit_margin = swf.get_lifetime_profit_margin()
        # results['Lifetime Profit Margin'] = [lifetime_profit_margin, 5316.994012]

        # total_co2_seq = swf.get_total_co2_sequestered()
        # results['Total Additional CO2-eq Sequestered'] = [total_co2_seq, 2.49773912913679]

        # change_in_ppm_equivalent = swf.get_change_in_ppm_equivalent()
        # results['Approximate PPM Equivalent Change'] = [change_in_ppm_equivalent, 0.21127592]

        # change_in_ppm_equivalent_final = swf.get_change_in_ppm_equivalent_final_year()
        # results['Approximate PPM rate in 2050'] = [change_in_ppm_equivalent_final, 0.0117934173530898]

        # max_annual_co2_sequestered = swf.get_max_annual_co2_sequestered()
        # results['Max Annual CO2 Sequestered'] = [max_annual_co2_sequestered, 0.152243146918814]

        # co2_sequestered_final_year = swf.get_co2_sequestered_final_year()
        # results['CO2 Sequestered in 2050'] = [co2_sequestered_final_year, 0.152243146918814]

        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




