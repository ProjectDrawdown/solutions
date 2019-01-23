import pytest
from model import aez


def test_populate_solution_la():
    trr_aez = aez.AEZ('Tropical Forest Restoration')
    assert trr_aez.perc_la_df.loc['Tropical-Humid', 'AEZ3: Forest, good, moderate'] == pytest.approx(0.245464949942429)
    zero_rows = sum([trr_aez.perc_la_df.iloc[i].sum() for i in [1, 3, 4, 5]])  # these should be all 0
    assert zero_rows == pytest.approx(0)