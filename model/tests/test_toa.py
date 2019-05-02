import pandas as pd
import pathlib
from model import toa

datadir = pathlib.Path(__file__).parents[0].joinpath('data')


def test_toa_per_region():
    # we use a modified version of the silvopasture TLA data as mock TLA values
    sp_land_dist_all = [331.702828, 181.9634517, 88.98630743, 130.15193962, 201.18287123,
                        0.,  # new ABNJ region
                        933.98739798, 37.60589239, 7.02032552, 43.64118779, 88.61837725]
    index = pd.Index(
        ['OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'ABNJ', 'Global',
         'China', 'India', 'EU', 'USA'])
    ocean_dist = pd.DataFrame(sp_land_dist_all, columns=['All'], index=index)
    expected = pd.read_csv(datadir.joinpath('sp_tla_with_abnj.csv'), index_col=0)
    result = toa.toa_per_region(ocean_dist=ocean_dist)
    pd.testing.assert_frame_equal(expected, result, check_dtype=False)
