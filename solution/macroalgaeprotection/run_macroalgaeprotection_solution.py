
import pandas as pd
from solution.macroalgaeprotection.macroalgaeprotection_solution import MacroalgaeProtectionSolution

def main():
    
    swf = MacroalgaeProtectionSolution()

    scenario_names = ['PDS-53p2050-Optimum']

    for sc in scenario_names:
        print()
        print(sc)
        swf.load_scenario(sc)

        results = {}
        
        # au_inc = swf.get_adoption_unit_increase_final_year('World')
        # gu_final = swf.get_adoption_unit_pds_final_year('World')
        # gpa_base = swf.get_global_percent_adoption_base_year('World') #returns base year +1?
        gpa_start = swf.get_percent_adoption_start_year('World')
        gpa_end = swf.get_percent_adoption_end_year('World')

        # results['Adoption Unit Increase Second Year (PDS vs REF)'] = [au_inc,  199.1299393]
        # results['Global Units of Adoption in Second Year'] = [gu_final, 199.1299393]
        # results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 0.00 / 100]
        results['Global Percent Adoption in First Year'] = [gpa_start, 6.2506050207 / 100]
        results['Global Percent Adoption in Second Year (2014)'] = [gpa_end, 74.7012373290 / 100]

        total_co2_seq = swf.get_total_co2_seq('World')
        results['total_co2_seq'] = [total_co2_seq, 2.49773912913679]

        # change_in_ppm_equiv = swf.get_change_in_ppm_equiv('World')
        # results['change_in_ppm_equiv'] = [change_in_ppm_equiv, 0.21127592]

        # change_in_ppm_equiv_final = swf.get_change_in_ppm_equiv_final_year('World')
        # results['change_in_ppm_equiv_final'] = [change_in_ppm_equiv_final, 0.0117934173530898]

        # max_annual_co2_sequestered = swf.get_max_annual_co2_sequestered('World')
        # results['max_annual_co2_sequestered'] = [max_annual_co2_sequestered, 0.152243146918814]

        # co2_sequestered_final_year = swf.get_co2_sequestered_final_year('World')
        # results['co2_sequestered_final_year'] = [co2_sequestered_final_year, 0.152243146918814]

        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




