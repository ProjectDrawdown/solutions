import sys
sys.path.append('c:\\Users\\sunishchal.dev\\Documents\\solutions\\solution\\health_and_education')

import pandas as pd

import electricity_cluster

test_elec = electricity_cluster.Scenario()
exp_elec = pd.read_csv('expected_elec_cluster.csv', header=None)

def test_electricity_cluster():
    exp_ref2_tam = exp_elec.iloc[26:73, 1:11].astype(float)
    exp_ref2_tam.columns = exp_elec.iloc[25, 1:11].values
    exp_ref2_tam.index = exp_elec.iloc[26:73, 0].astype(int).values
    pd.testing.assert_frame_equal(test_elec.ref2_tam, exp_ref2_tam, check_exact=False)

test_electricity_cluster()