import sys
sys.path.append('c:\\Users\\sunishchal.dev\\Documents\\solutions\\solution\\health_and_education')

import pandas as pd
import numpy as np

from clusters import plastics

test_cluster = plastics.Cluster()
test_dfs = test_cluster.run_cluster()

expected_df = pd.read_csv('expected_plastics.csv', header=None)

def test_plastics():
    
    # Default columns to integers to avoid mismatch between Excel & pandas col names using T.reset_index()
    exp_ref2_tam = expected_df.iloc[28:75, 1:2].T.reset_index(drop=True).T.astype(float)
    exp_ref2_tam.index = expected_df.iloc[28:75, 0].astype(int).values
    test_ref2_tam = test_dfs.ref2_tam.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_ref2_tam, exp_ref2_tam, check_exact=False)

    exp_addl_func_units_mdc = expected_df.iloc[193:240, 4:7].T.reset_index(drop=True).T.astype(float)
    exp_addl_func_units_mdc.index = expected_df.iloc[193:240, 0].astype(int, errors='ignore').values
    test_addl_func_units_mdc = test_dfs.addl_func_units_mdc.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_addl_func_units_mdc, exp_addl_func_units_mdc, check_exact=False, rtol=1e-3)

    exp_emis_diff_mdc = expected_df.iloc[193:240, [15, 16, 17, 18, 20]].T.reset_index(drop=True).T.astype(float)
    exp_emis_diff_mdc.index = expected_df.iloc[193:240, 0].astype(int, errors='ignore').values
    test_emis_diff_mdc = test_dfs.emis_diff_mdc.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_emis_diff_mdc, exp_emis_diff_mdc, check_exact=False, rtol=1e-3)

    exp_emissions_allocations_mdc = expected_df.iloc[193:240, [25, 26, 28, 29, 31, 32, 35, 36]].T.reset_index(drop=True).T.astype(float)
    exp_emissions_allocations_mdc.index = expected_df.iloc[193:240, 24].astype(int, errors='ignore').values
    test_emissions_allocations_mdc = test_dfs.emissions_allocations_mdc.T.reset_index(drop=True).T
    pd.testing.assert_frame_equal(test_emissions_allocations_mdc, exp_emissions_allocations_mdc, check_exact=False, rtol=1e-2)

    # Test the final CO2 reduction output
    exp_emissions_avoided = expected_df.iloc[[4, 7, 11], [13, 14]].reset_index(drop=True).T.reset_index(drop=True).T.astype(float)
    test_emissions_avoided = pd.DataFrame([[test_dfs.emissions_avoided_lldc_period, test_dfs.emissions_avoided_lldc_full],
                                        [test_dfs.emissions_avoided_mdc_period, test_dfs.emissions_avoided_mdc_full],
                                        [test_dfs.emissions_avoided_total_period, test_dfs.emissions_avoided_total_full]])
    pd.testing.assert_frame_equal(test_emissions_avoided, exp_emissions_avoided, check_exact=False, rtol=1e-2)

    print("Test complete: plastics cluster")

test_plastics()