
import pandas as pd
from solution.macroalgaerestoration.macroalgaerestoration_solution import MacroalgaeRestorationSolution

def main():
    
    mars = MacroalgaeRestorationSolution()

    scenario_names = ['PDS-16p2050-Optimum 20August2021']

    for sc in scenario_names:
        print()
        print(sc)
        mars.load_scenario(sc)

        results = {}
        
        au_inc = mars.get_adoption_unit_increase_pds_vs_ref_final_year()
        gu_final = mars.get_adoption_unit_increase_pds_final_year()
        gpa_base = mars.get_global_percent_adoption_base_year() #returns base year +1?
        gpa_start = mars.get_percent_adoption_start_year()
        gpa_end = mars.get_percent_adoption_end_year()

        results['Adoption Unit Increase in 2050 (PDS vs REF)'] = [au_inc, 33.61214819960]
        results['Global Units of Adoption in 2050'] = [gu_final, 33.61214819960]
        results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 0.00 / 100]
        results['Global Percent Adoption in First Year'] = [gpa_start, 1.0609895265/ 100]
        results['Global Percent Adoption in Second Year'] = [gpa_end, 16.9758324240/ 100]

        total_co2_seq = mars.get_total_co2_seq()
        results['Total Additional CO2-eq Sequestered'] = [total_co2_seq, 1.952028234]

        change_in_ppm_equiv = mars.get_change_in_ppm_equiv()
        results['Approximate PPM Equivalent Change'] = [change_in_ppm_equiv, 0.1651159440]

        change_in_ppm_equiv_final = mars.get_change_in_ppm_equiv_final_year()
        results['Approximate PPM rate in 2050'] = [change_in_ppm_equiv_final,  0.0092167686]

        max_annual_co2_sequestered = mars.get_max_annual_co2_sequestered()
        results['Max Annual CO2 Sequestered'] = [max_annual_co2_sequestered, 0.1189807685]

        co2_sequestered_final_year = mars.get_co2_sequestered_final_year()
        results['CO2 Sequestered in 2050'] = [co2_sequestered_final_year, 0.1189807685]

        total_atmospheric_co2_eq_reduction = total_co2_seq
        results['Total Atmospheric CO2-eq Reduction'] = [total_atmospheric_co2_eq_reduction, 1.952028234]

        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




