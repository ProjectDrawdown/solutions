import pytest
import pandas as pd
from model import aez


def test_populate_solution_land_allocation():
    trr_aez = aez.AEZ('Tropical Forest Restoration')
    assert trr_aez.soln_land_alloc_df.loc['Tropical-Humid',
            'AEZ3: Forest, good, moderate'] == pytest.approx(0.245464949942429)
    zero_rows = trr_aez.soln_land_alloc_df.iloc[[1, 3, 4, 5]].sum().sum()  # these should be all 0
    assert zero_rows == 0
    trr_aez = aez.AEZ('Peatland Protection', cohort=2019)
    assert trr_aez.soln_land_alloc_df.loc['Tropical-Humid',
            'AEZ3: Forest, good, moderate'] == pytest.approx(0.10591729011599778)


def test_applicable_zones():
    trr_aez = aez.AEZ('Tropical Forest Restoration')
    assert len(trr_aez.applicable_zones) == 18
    assert 'AEZ27: Rainfed Cropland, marginal, moderate' in trr_aez.applicable_zones


def test_populate_world_land_allocation():
    trr_aez = aez.AEZ('Tropical Forest Restoration')
    tsa_df = trr_aez.world_land_alloc_dict['Tropical-Semi-Arid']
    assert tsa_df.loc['China',
            'AEZ5: Forest, marginal, minimal'] == pytest.approx(0.6833171383331640)
    trr_aez = aez.AEZ('Tropical Forest Restoration', cohort=2019)
    tsa_df = trr_aez.world_land_alloc_dict['Tropical-Semi-Arid']
    assert tsa_df.loc['China',
            'AEZ5: Forest, marginal, minimal'] == pytest.approx(0.7322819187332402)


def test_populate_solution_land_distribution():
    trr_aez = aez.AEZ('Tropical Forest Restoration')
    assert trr_aez.soln_land_dist_df.loc['Global', 'All'] == pytest.approx(303.9980581327790)
    result = trr_aez.soln_land_dist_df.loc['Latin America', 'Tropical-Humid']
    assert result == pytest.approx(129.598434)
    result = trr_aez.soln_land_dist_df.loc['Eastern Europe', 'Tropical-Semi-Arid']
    assert result == pytest.approx(21.689457)


def test_ignore_allocation():
    trr_aez = aez.AEZ('Tropical Forest Restoration', ignore_allocation=True)
    res = trr_aez.soln_land_dist_df
    assert res[res == 1].all().all()


def test_tropical_tree_staples():
    ae = aez.AEZ('Tropical Tree Staples')
    expected = pd.DataFrame(tropical_tree_staples_land_distribution_list[1:],
            columns=tropical_tree_staples_land_distribution_list[0]).set_index('Region')
    result = ae.soln_land_dist_df
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


tropical_tree_staples_land_distribution_list = [
    ['Region',  'Tropical-Humid',  'Temperate/Boreal-Humid',  'Tropical-Semi-Arid',
        'Temperate/Boreal-Semi-Arid',  'Global Arid',  'Global Arctic',  'All'],
    ['OECD90', 0.640372342699809, 0.0, 46.751476270145100, 0.0, 0.0, 0.0, 47.391848612844900],
    ['Eastern Europe', 0.0, 0.0, 18.710751455339500, 0.0, 0.0, 0.0, 18.710751455339500],
    ['Asia (Sans Japan)', 5.598240017676890, 0.0, 17.698427206190200, 0.0, 0.0, 0.0, 23.296667223867100],
    ['Middle East and Africa', 8.329095464315030, 0.0, 51.520771066650400, 0.0, 0.0, 0.0, 59.849866530965400],
    ['Latin America', 6.425392926793170, 0.0, 13.698945374320400, 0.0, 0.0, 0.0, 20.124338301113500],
    ['Global', 20.993100751484900, 0.0, 148.380371372645000, 0.0, 0.0, 0.0, 169.373472124130000],
    ['China', 0.048858346708482, 0.0, 12.817757263604300, 0.0, 0.0, 0.0, 12.866615610312800],
    ['India', 0.460440693306190, 0.0, 1.288334211130060, 0.0, 0.0, 0.0, 1.748774904436250],
    ['EU', 0.0, 0.0, 0.319082989592622, 0.0, 0.0, 0.0, 0.319082989592622],
    ['USA', 0.004993461567685, 0.0, 14.102350311549400, 0.0, 0.0, 0.0, 14.107343773117100],
    ]
