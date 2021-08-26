import pytest
from model import aez


@pytest.mark.slow
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
    trr_aez = aez.AEZ('Tropical Forest Restoration', max_tla=True)
    res = trr_aez.soln_land_dist_df
    assert res[res == 1].all().all()


def test_tropical_tree_staples():
    ae = aez.AEZ('Tropical Tree Staples')
    result = ae.soln_land_dist_df
    assert result is not None
