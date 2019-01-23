import pytest
from model import aez

trr_aez = aez.AEZ('Tropical Forest Restoration')

def test_populate_solution_land_allocation():
    assert trr_aez.soln_land_alloc_df.loc['Tropical-Humid', 'AEZ3: Forest, good, moderate'] == pytest.approx(0.245464949942429)
    zero_rows = sum([trr_aez.soln_land_alloc_df.iloc[i].sum() for i in [1, 3, 4, 5]])  # these should be all 0
    assert zero_rows == pytest.approx(0)


def test_applicable_zones():
    assert len(trr_aez.applicable_zones) == 18
    assert 'AEZ27: Rainfed Cropland, marginal, moderate' in trr_aez.applicable_zones


def test_populate_world_land_allocation():
    tsa_df = trr_aez.world_land_alloc_dict['Tropical-Semi-Arid']
    assert tsa_df.loc['China', 'AEZ5: Forest, marginal, minimal'] == pytest.approx(0.6833171383331640)


def test_populate_solution_land_distribution():
    assert trr_aez.soln_land_dist_df.loc['Global', 'All'] == pytest.approx(303.9980581327790)
