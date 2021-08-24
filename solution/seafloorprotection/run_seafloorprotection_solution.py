
import pandas as pd
from solution.seafloorprotection.seafloorprotection_solution import SeafloorProtectionSolution

def main():
    
    sps = SeafloorProtectionSolution()

    scenario_names = ['PDS-48p2050-Optimum']

    for sc in scenario_names:
        print()
        print(sc)
        sps.load_scenario(sc)

        results = {}
        
        au_inc = sps.get_adoption_unit_increase_pds_vs_ref_final_year()
        gu_final = sps.get_adoption_unit_increase_pds_final_year()
        gpa_base = sps.get_global_percent_adoption_base_year() #returns base year +1?
        gpa_start = sps.get_percent_adoption_start_year()
        gpa_end = sps.get_percent_adoption_end_year()

        results['Adoption Unit Increase in 2050 (PDS vs REF)'] = [au_inc, 441.00]
        results['Global Units of Adoption in 2050'] = [gu_final, 441.00]
        results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 0.00 / 100]
        results['Global Percent Adoption in First Year'] = [gpa_start, 5.625/ 100]
        results['Global Percent Adoption in Second Year'] = [gpa_end, 90.00/ 100]

        # total_emissions_reduction = sps.get_total_emissions_reduction()
        # results['Total Emissions Reduction'] = 5.9101139397

        total_co2_seq = sps.get_total_co2_seq()
        results['Total Additional CO2-eq Sequestered'] = [total_co2_seq, 0.00000]

        change_in_ppm_equiv = sps.get_change_in_ppm_equiv()
        results['Approximate PPM Equivalent Change'] = [change_in_ppm_equiv, 0.4607453935]

        change_in_ppm_equiv_final = sps.get_change_in_ppm_equiv_final_year()
        results['Approximate PPM rate in 2050'] = [change_in_ppm_equiv_final,  0.01195646244]

        max_annual_co2_sequestered = sps.get_max_annual_co2_sequestered()
        results['Max Annual CO2 Sequestered'] = [max_annual_co2_sequestered, 0.000]

        co2_sequestered_final_year = sps.get_co2_sequestered_final_year()
        results['CO2 Sequestered in 2050'] = [co2_sequestered_final_year, 0.000]

        # total_atmospheric_co2_eq_reduction = total_emissions_reduction + total_co2_seq
        # results['Total Atmospheric CO2-eq Reduction'] = [total_atmospheric_co2_eq_reduction, ]

        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




