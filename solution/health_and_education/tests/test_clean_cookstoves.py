import sys
sys.path.append('c:\\Users\\sunishchal.dev\\Documents\\solutions\\solution\\health_and_education')

import pandas as pd
import numpy as np

from clusters import clean_cookstoves

test_cluster = clean_cookstoves.Cluster()
test_dfs = test_cluster.run_cluster()

expected_df = pd.read_csv('expected_clean_cookstoves.csv', header=None)

def test_clean_cookstoves():
    
    # Default columns to integers to avoid mismatch between Excel & pandas col names using T.reset_index()
    exp_ref2_tam = expected_df.iloc[28:75, 1:11].T.reset_index(drop=True).T.astype(float)
    exp_ref2_tam.index = expected_df.iloc[28:75, 0].astype(int).values
    test_ref2_tam = test_dfs.ref2_tam.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_ref2_tam, exp_ref2_tam, check_exact=False)

    exp_ref1_tam_low_edu = expected_df.iloc[28:75, 13:23].T.reset_index(drop=True).T.astype(float)
    exp_ref1_tam_low_edu.index = expected_df.iloc[28:75, 12].astype(int).values
    test_ref1_tam_low_edu = test_dfs.ref1_tam_low_edu.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_ref1_tam_low_edu, exp_ref1_tam_low_edu, check_exact=False)

    exp_ref1_tam_high_edu = expected_df.iloc[28:75, 25:35].T.reset_index(drop=True).T.astype(float)
    exp_ref1_tam_high_edu.index = expected_df.iloc[28:75, 24].astype(int).values
    test_ref1_tam_high_edu = test_dfs.ref1_tam_high_edu.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_ref1_tam_high_edu, exp_ref1_tam_high_edu, check_exact=False)

    exp_ref1_tam_all_regions = expected_df.iloc[28:75, 37:47].T.reset_index(drop=True).T.astype(float)
    exp_ref1_tam_all_regions.index = expected_df.iloc[28:75, 36].astype(int).values
    test_ref1_tam_all_regions = test_dfs.ref1_tam_all_regions.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_ref1_tam_all_regions, exp_ref1_tam_all_regions, check_exact=False)

    exp_ref2_demand = expected_df.iloc[79:126, 1:6].T.reset_index(drop=True).T.astype(float)
    exp_ref2_demand.index = expected_df.iloc[79:126, 0].astype(int).values
    test_ref2_demand = test_dfs.ref2_demand.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_ref2_demand, exp_ref2_demand, check_exact=False, rtol=1e-3)

    exp_ref1_demand = expected_df.iloc[79:126, [8,9,10,11,12,14,15,16,17,18,19]].T.reset_index(drop=True).T.astype(float)
    exp_ref1_demand.index = expected_df.iloc[79:126, 7].astype(int).values
    test_ref1_demand = test_dfs.ref1_demand.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_ref1_demand, exp_ref1_demand, check_exact=False, rtol=1e-3)

    exp_change_demand = expected_df.iloc[79:126, 22:30].T.reset_index(drop=True).T.astype(float)
    exp_change_demand.index = expected_df.iloc[79:126, 7].astype(int).values
    test_change_demand = test_dfs.change_demand.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_change_demand, exp_change_demand, check_exact=False, rtol=1e-3)

    exp_addl_func_units_highed = expected_df.iloc[134:181, 4:7].T.reset_index(drop=True).T.astype(float)
    exp_addl_func_units_highed.index = expected_df.iloc[134:181, 0].astype(int, errors='ignore').values
    test_addl_func_units_highed = test_dfs.addl_func_units_highed.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_addl_func_units_highed, exp_addl_func_units_highed, check_exact=False, rtol=1e-3)

    exp_addl_func_units_lowed = expected_df.iloc[134:181, 12:15].T.reset_index(drop=True).T.astype(float)
    exp_addl_func_units_lowed.index = expected_df.iloc[134:181, 0].astype(int, errors='ignore').values
    test_addl_func_units_lowed = test_dfs.addl_func_units_lowed.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_addl_func_units_lowed, exp_addl_func_units_lowed, check_exact=False, rtol=1e-3)

    exp_emis_diff_highed = expected_df.iloc[134:181, [22, 23, 24, 25, 27]].T.reset_index(drop=True).T.astype(float)
    exp_emis_diff_highed.index = expected_df.iloc[134:181, 0].astype(int, errors='ignore').values
    test_emis_diff_highed = test_dfs.emis_diff_highed.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_emis_diff_highed, exp_emis_diff_highed, check_exact=False, rtol=1e-3)

    exp_emis_diff_lowed = expected_df.iloc[134:181, [35, 36, 37, 38, 40]].T.reset_index(drop=True).T.astype(float)
    exp_emis_diff_lowed.index = expected_df.iloc[134:181, 0].astype(int, errors='ignore').values
    test_emis_diff_lowed = test_dfs.emis_diff_lowed.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_emis_diff_lowed, exp_emis_diff_lowed, check_exact=False, rtol=1e-3)

    exp_emissions_allocations_lldc = expected_df.iloc[134:181, [46, 47, 49, 50, 52, 53, 56, 57]].T.reset_index(drop=True).T.astype(float)
    exp_emissions_allocations_lldc.index = expected_df.iloc[134:181, 45].astype(int, errors='ignore').values
    test_emissions_allocations_lldc = test_dfs.emissions_allocations_lldc.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_emissions_allocations_lldc, exp_emissions_allocations_lldc, check_exact=False, rtol=1e-2)

    # Test the final CO2 reduction output
    exp_emissions_avoided = expected_df.iloc[[4, 7, 11], [13, 14]].reset_index(drop=True).T.reset_index(drop=True).T.astype(float)
    test_emissions_avoided = pd.DataFrame([[test_dfs.emissions_avoided_lldc_period, test_dfs.emissions_avoided_lldc_full],
                                        [test_dfs.emissions_avoided_mdc_period, test_dfs.emissions_avoided_mdc_full],
                                        [test_dfs.emissions_avoided_total_period, test_dfs.emissions_avoided_total_full]])
    pd.testing.assert_frame_equal(test_emissions_avoided, exp_emissions_avoided, check_exact=False, rtol=1e-2)

    print("Test complete: clean cookstoves cluster")

test_clean_cookstoves()