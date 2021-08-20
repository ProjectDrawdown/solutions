
import pandas as pd
from solution.macroalgaeprotection.macroalgaeprotection_solution import MacroalgaeProtectionSolution

def main():
    
    maps = MacroalgaeProtectionSolution()

    scenario_names = ['PDS-53p2050-Optimum']

    for sc in scenario_names:
        print()
        print(sc)
        maps.load_scenario(sc)

        results = {}
        
        au_inc = maps.get_adoption_unit_increase_pds_vs_ref_final_year()
        gu_final = maps.get_adoption_unit_increase_pds_final_year()
        gpa_base = maps.get_global_percent_adoption_base_year() #returns base year +1?
        gpa_start = maps.get_percent_adoption_start_year()
        gpa_end = maps.get_percent_adoption_end_year()

        results['Adoption Unit Increase in 2050 (PDS vs REF)'] = [au_inc,  265.0]
        results['Global Units of Adoption in 2050'] = [gu_final, 265.0]
        results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 0.00 / 100]
        results['Global Percent Adoption in First Year'] = [gpa_start, 6.2506050207 / 100]
        results['Global Percent Adoption in Second Year (2014)'] = [gpa_end, 74.7012373290 / 100]

        total_co2_seq = maps.get_total_co2_seq()
        results['Total Additional CO2-eq Sequestered'] = [total_co2_seq, 3.85598888]

        change_in_ppm_equiv = maps.get_change_in_ppm_equiv(delay_period=1)
        results['change_in_ppm_equiv'] = [change_in_ppm_equiv, 0.339684712828728]

        change_in_ppm_equiv_final = maps.get_change_in_ppm_equiv_final_year(delay_period= 1)
        results['change_in_ppm_equiv_final'] = [change_in_ppm_equiv_final, 0.027045695545894]

        max_annual_co2_sequestered = maps.get_max_annual_co2_sequestered(delay_period= 1)
        results['max_annual_co2_sequestered'] = [max_annual_co2_sequestered, 0.326041958295943]

        co2_sequestered_final_year = maps.get_co2_sequestered_final_year(delay_period= 1)
        results['co2_sequestered_final_year'] = [co2_sequestered_final_year, 0.326041958295943]

        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




