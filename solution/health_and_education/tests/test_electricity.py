import sys
sys.path.append('c:\\Users\\sunishchal.dev\\Documents\\solutions\\solution\\health_and_education')

import pandas as pd
import numpy as np

import clusters.electricity_cluster as electricity_cluster

test_elec = electricity_cluster.Scenario()
exp_elec = pd.read_csv('expected_elec_cluster.csv', header=None)

def test_electricity_cluster():
    exp_ref2_tam = exp_elec.iloc[26:73, 1:11].astype(float)
    exp_ref2_tam.columns = exp_elec.iloc[25, 1:11].values
    exp_ref2_tam.index = exp_elec.iloc[26:73, 0].astype(int).values
    pd.testing.assert_frame_equal(test_elec.ref2_tam, exp_ref2_tam, check_exact=False)

    exp_ref1_tam_low_edu = exp_elec.iloc[26:73, 13:23].astype(float)
    exp_ref1_tam_low_edu.columns = exp_elec.iloc[25, 13:23].values
    exp_ref1_tam_low_edu.index = exp_elec.iloc[26:73, 12].astype(int).values
    pd.testing.assert_frame_equal(test_elec.ref1_tam_low_edu, exp_ref1_tam_low_edu, check_exact=False)

    exp_ref1_tam_high_edu = exp_elec.iloc[26:73, 25:35].astype(float)
    exp_ref1_tam_high_edu.columns = exp_elec.iloc[25, 25:35].values
    exp_ref1_tam_high_edu.index = exp_elec.iloc[26:73, 24].astype(int).values
    pd.testing.assert_frame_equal(test_elec.ref1_tam_high_edu, exp_ref1_tam_high_edu, check_exact=False)

    exp_ref1_tam_all_regions = exp_elec.iloc[26:73, 37:47].astype(float)
    exp_ref1_tam_all_regions.columns = exp_elec.iloc[25, 37:47].values
    exp_ref1_tam_all_regions.index = exp_elec.iloc[26:73, 36].astype(int).values
    pd.testing.assert_frame_equal(test_elec.ref1_tam_all_regions, exp_ref1_tam_all_regions, check_exact=False)

    exp_ref2_elec_gen = exp_elec.iloc[77:124, 1:6].astype(float)
    exp_ref2_elec_gen.columns = exp_elec.iloc[76, 1:6].values
    exp_ref2_elec_gen.index = exp_elec.iloc[77:124, 0].astype(int).values
    pd.testing.assert_frame_equal(test_elec.ref2_elec_gen, exp_ref2_elec_gen, check_exact=False, rtol=1e-3)

    exp_ref1_elec_gen = exp_elec.iloc[77:124, 8:19].astype(float)
    exp_ref1_elec_gen.columns = exp_elec.iloc[76, 8:19].values
    exp_ref1_elec_gen.index = exp_elec.iloc[77:124, 7].astype(int).values
    pd.testing.assert_frame_equal(test_elec.ref1_elec_gen, exp_ref1_elec_gen, check_exact=False, rtol=1e-3)

    exp_change_elec_gen = exp_elec.iloc[77:124, 22:30].astype(float)
    exp_change_elec_gen.columns = exp_elec.iloc[76, 22:30].values
    exp_change_elec_gen.index = exp_elec.iloc[77:124, 7].astype(int).values
    pd.testing.assert_frame_equal(test_elec.change_elec_gen, exp_change_elec_gen, check_exact=False, rtol=1e-3)

    exp_addl_func_units_highed = exp_elec.iloc[132:179, 4:7].astype(float)
    exp_addl_func_units_highed.columns = exp_elec.iloc[130, 4:7].values
    exp_addl_func_units_highed.index = exp_elec.iloc[132:179, 0].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.addl_func_units_highed, exp_addl_func_units_highed, check_exact=False, rtol=1e-3)

    exp_addl_func_units_lowed = exp_elec.iloc[132:179, 12:15].astype(float)
    exp_addl_func_units_lowed.columns = exp_elec.iloc[130, 12:15].values
    exp_addl_func_units_lowed.index = exp_elec.iloc[132:179, 0].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.addl_func_units_lowed, exp_addl_func_units_lowed, check_exact=False, rtol=1e-3)

    exp_emis_diff_highed = exp_elec.iloc[132:179, 21:26].astype(float)
    exp_emis_diff_highed.columns = range(exp_emis_diff_highed.shape[1]) # Default columns to integers to avoid mismatch between Excel & pandas col names
    test_elec.emis_diff_highed.columns = range(test_elec.emis_diff_highed.shape[1])
    exp_emis_diff_highed.index = exp_elec.iloc[132:179, 0].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.emis_diff_highed, exp_emis_diff_highed, check_exact=False, rtol=1e-3)

    exp_emis_diff_lowed = exp_elec.iloc[132:179, 34:39].astype(float)
    exp_emis_diff_lowed.columns = range(exp_emis_diff_lowed.shape[1])
    test_elec.emis_diff_lowed.columns = range(test_elec.emis_diff_lowed.shape[1])
    exp_emis_diff_lowed.index = exp_elec.iloc[132:179, 0].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.emis_diff_lowed, exp_emis_diff_lowed, check_exact=False, rtol=1e-3)

    exp_emissions_allocations_lldc = exp_elec.iloc[132:179, [44, 45, 47, 48, 50, 51, 54, 55]].astype(float)
    exp_emissions_allocations_lldc.columns = range(exp_emissions_allocations_lldc.shape[1])
    test_elec.emissions_allocations_lldc.columns = range(test_elec.emissions_allocations_lldc.shape[1])
    exp_emissions_allocations_lldc.index = exp_elec.iloc[132:179, 43].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.emissions_allocations_lldc, exp_emissions_allocations_lldc, check_exact=False, rtol=1e-2)

    exp_addl_func_units_mdc = exp_elec.iloc[191:238, 4:7].astype(float)
    exp_addl_func_units_mdc.columns = exp_elec.iloc[189, 4:7].values
    exp_addl_func_units_mdc.index = exp_elec.iloc[191:238, 0].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.addl_func_units_mdc, exp_addl_func_units_mdc, check_exact=False, rtol=1e-3)

    exp_emis_diff_mdc = exp_elec.iloc[191:238, 14:19].astype(float)
    exp_emis_diff_mdc.columns = range(exp_emis_diff_mdc.shape[1])
    test_elec.emis_diff_mdc.columns = range(test_elec.emis_diff_mdc.shape[1])
    exp_emis_diff_mdc.index = exp_elec.iloc[191:238, 0].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.emis_diff_mdc, exp_emis_diff_mdc, check_exact=False, rtol=1e-3)

    exp_emissions_allocations_mdc = exp_elec.iloc[191:238, [23, 24, 26, 27, 29, 30, 33, 34]].astype(float)
    exp_emissions_allocations_mdc.columns = range(exp_emissions_allocations_mdc.shape[1])
    test_elec.emissions_allocations_mdc.columns = range(test_elec.emissions_allocations_mdc.shape[1])
    exp_emissions_allocations_mdc.index = exp_elec.iloc[191:238, 22].astype(int, errors='ignore').values
    pd.testing.assert_frame_equal(test_elec.emissions_allocations_mdc, exp_emissions_allocations_mdc, check_exact=False, rtol=1e-2)

    # Test the final CO2 reduction output (columns/indices are dropped since it's not a real table)
    exp_emissions_avoided = exp_elec.iloc[[4, 7, 11], [13, 14]].reset_index(drop=True).T.reset_index(drop=True).T.astype(float)
    test_emissions_avoided = pd.DataFrame([[test_elec.emissions_avoided_lldc_period, test_elec.emissions_avoided_lldc_full],
                                        [test_elec.emissions_avoided_mdc_period, test_elec.emissions_avoided_mdc_full],
                                        [test_elec.emissions_avoided_total_period, test_elec.emissions_avoided_total_full]])
    pd.testing.assert_frame_equal(test_emissions_avoided, exp_emissions_avoided, check_exact=False, rtol=1e-2)

    print("Test complete: electricity cluster")

test_electricity_cluster()