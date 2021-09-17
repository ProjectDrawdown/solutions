
import pandas as pd
from solution.seagrassprotection.seagrassprotection_solution import SeagrassProtectionSolution

def main():
    
    sps = SeagrassProtectionSolution()

    scenario_names = ['PDS-69p2050-Maximum JULY2021']

    for sc in scenario_names:
        print()
        print(sc)
        sps.load_scenario(sc)

        results = {}

        emissions_reduction_series = sps.get_emissions_reduction_series()
        emissions_reduction_series.to_json('solution/seagrassprotection/tests/total_emissions_reduction_series.txt')
    
        desired_result = pd.io.json.read_json('solution/seagrassprotection/tests/total_emissions_reduction_series.txt', typ='series')

        carbon_sequestration_series = sps.get_change_in_ppm_equivalent_series()
        carbon_sequestration_series.to_json('solution/seagrassprotection/tests/change_in_ppm_equivalent_series.json')

        change_in_ppm_equivalent_series = sps.get_change_in_ppm_equivalent_series()

        desired_result = pd.io.json.read_json('solution/seagrassprotection/tests/change_in_ppm_equivalent_series.json', typ='series')

        pd.testing.assert_series_equal(change_in_ppm_equivalent_series, desired_result, check_names = False)


        change_in_ppm_equiv = sps.get_change_in_ppm_equivalent()
        results['Approximate PPM Equivalent Change'] = [change_in_ppm_equiv, 0.0558909304494364]

        change_in_ppm_equiv_final = sps.get_change_in_ppm_equivalent_final_year()
        results['Approximate PPM rate in 2050'] = [change_in_ppm_equiv_final,  0.00352600148886495]


        # pd.testing.assert_series_equal(emissions_reduction_series, desired_result, check_names = False)


        
        # au_inc = sps.get_adoption_unit_increase_pds_vs_ref_final_year()
        # results['Adoption Unit Increase in 2050 (PDS vs REF)'] = [au_inc,  11.9209315305]

        # gu_final = sps.get_adoption_unit_increase_pds_final_year()
        # results['Global Units of Adoption in 2050'] = [gu_final, 17.865258686292]

        # gpa_base = sps.get_global_percent_adoption_base_year() #returns base year +1?
        # results['Global Percent Adoption - Base Year (2014)'] = [gpa_base, 23.1025 / 100]
        
        # gpa_start = sps.get_percent_adoption_start_year()
        # results['Global Percent Adoption in First Year'] = [gpa_start, 31.3385777675664 / 100]

        # gpa_end = sps.get_percent_adoption_end_year()
        # results['Global Percent Adoption in Second Year'] = [gpa_end, 69.4329447185686 / 100]

        # total_emissions_reduction = sps.get_total_emissions_reduction()
        # results['Total Emissions Reduction'] = [ total_emissions_reduction, 0.288891735240484]

        # total_co2_seq = sps.get_total_co2_sequestered()
        # results['Total Additional CO2-eq Sequestered'] = [total_co2_seq, 0.359513049174938]
 
        # max_annual_co2_sequestered = sps.get_max_annual_co2_sequestered()
        # results['Max Annual CO2 Sequestered'] = [max_annual_co2_sequestered, 0.0251612427386]

        # emissions_reduction_final_year = sps.get_emissions_reduction_final_year()
        # results['Emissions Reduction in 2050'] = [emissions_reduction_final_year, 0.0194061585293477]

        # co2_sequestered_final_year = sps.get_co2_sequestered_final_year()
        # results['CO2 Sequestered in 2050'] = [co2_sequestered_final_year, 0.0251612427385857]

        # total_atmospheric_co2_eq_reduction = total_emissions_reduction + total_co2_seq
        # results['Total Atmospheric CO2-eq Reduction'] = [total_atmospheric_co2_eq_reduction, 0.648404784415423]

        # reduced_area_degradation = sps.get_reduced_area_degradation()
        # results['Reduced Land Degradation from 2020-2050'] = [reduced_area_degradation, 5.27946407538824]

        # co2_under_protection_final_year = sps.get_co2_under_protection_final_year()
        # results['CO2 Under Protection by 2050'] = [co2_under_protection_final_year, 14.6933270416904]

        # carbon_under_protection_final_year = sps.get_carbon_under_protection_final_year()
        # results['Carbon Under Protection by 2050'] = [carbon_under_protection_final_year, 4.01018751137840]

        # max_annual_emissions_reduction = sps.get_max_annual_emissions_reduction()
        # results['Max Annual Emissions Reduction']  = [max_annual_emissions_reduction, 0.019406158529]

        # annual_emissions_reduction_final_year = sps.get_annual_emissions_reduction_final_year()
        # results['Max Annual Emissions Reduction']  = [annual_emissions_reduction_final_year, 0.019406158529]

        
        df = pd.DataFrame.from_dict(results, orient = 'index', columns = ['calc_value', 'sheet_value'])
        df['% difference'] = (df['calc_value'] - df['sheet_value'])*100/df['calc_value']
        
        print(df)


if __name__ == '__main__':
    main()




