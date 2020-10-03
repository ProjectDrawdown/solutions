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


    print("Test complete: electricity cluster")

test_electricity_cluster()