
import pandas as pd
from solution.mangroveprotection.mangroveprotection_solution import MangroveProtectionSolution

def main():
    
    maps = MangroveProtectionSolution()

    scenario_names = ['PDS-74p2050-Plausible JULY2021']

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
        # results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 0.00 / 100]
        results['Global Percent Adoption in First Year'] = [gpa_start, 6.2506050207 / 100]
        results['Global Percent Adoption in Second Year (2014)'] = [gpa_end, 74.7012373290 / 100]

        # ### Key Climate Results ###
        # total_emissions_reduction = 0.0
        # results['Total Emissions Reduction'] = [total_emissions_reduction, 0.0] # Equals zero on s/sht. Code not implemented.

        total_co2_seq = maps.get_total_co2_sequestered()
        results['Total Additional CO2-eq Sequestered'] = [total_co2_seq, 3.85598888]

        ### Other Climate Results ###
        change_in_ppm_equiv = maps.get_change_in_ppm_equiv()
        results['Approximate PPM Equivalent Change'] = [change_in_ppm_equiv, 0.339684712828728]

        change_in_ppm_equivalent_final = maps.get_change_in_ppm_equivalent_final_year()
        results['Approximate PPM rate in 2050'] = [change_in_ppm_equivalent_final, 0.027045695545894]

        max_annual_co2_sequestered = maps.get_max_annual_co2_sequestered()
        results['Max Annual CO2 Sequestered'] = [max_annual_co2_sequestered, 0.326041958295943]

        co2_sequestered_final_year = maps.get_co2_sequestered_final_year()
        results['CO2 Sequestered in 2050'] = [co2_sequestered_final_year, 0.326041958295943]

        # total_atmos_co2_reduction = total_emissions_reduction + total_co2_seq
        # results['Total Atmospheric CO2-eq Reduction'] = [total_atmos_co2_reduction, 3.855988881]

        ### Protection Results ###
        # The following three metrics are not output in the scenario results, but are present in the [Advanced Controls] results.
        reduced_area_degradation = maps.get_reduced_area_degradation()
        results['Reduced Land Degradation from 2020-2050'] = [reduced_area_degradation, 104.4085339059]

        # t C storage in Protected Landtype = 4.593456
        carbon_storage = 4.593456294
        co2_to_c_ratio = 3.664
        total_co2_under_protection_at_end =  au_inc * carbon_storage
        results['Total CO2 Under Protection by 2050'] = [total_co2_under_protection_at_end * co2_to_c_ratio/ 1000,4.4600623229]
        
        results['Total Carbon Under Protection by 2050'] = [total_co2_under_protection_at_end / 1000,1.2172659178]
        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




