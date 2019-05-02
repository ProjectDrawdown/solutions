import pathlib
import pandas as pd
from model import dez

datadir = pathlib.Path(__file__).parents[0].joinpath('data')


def test_populate_solution_land_distribution():
    expected = pd.read_csv(datadir.joinpath('lbt_ocean_dist.csv'), index_col=0)
    de = dez.DEZ('Limiting bottom trawling')

    # We freeze applicable zones as solution_dez_matrix.csv is likely to change
    de.applicable_zones = ['DEZ1: Epipelagic, EEZ', 'DEZ2: Epipelagic, ABNJ']
    de._populate_world_ocean_allocation()
    de._populate_solution_ocean_distribution()

    pd.testing.assert_frame_equal(de.get_ocean_distribution(), expected, check_dtype=False)