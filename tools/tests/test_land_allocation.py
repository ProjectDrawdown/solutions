import os.path
import pathlib
import tempfile

import matplotlib.pyplot as plt
import pytest
import tools.land_allocation
import tools.world_data_xls_extract

@pytest.mark.slow
def test_plots():
    tools.land_allocation.plot_solution_allocation('peatlands', 'matching_tla')
    tools.land_allocation.plot_tla_remaining('matching_tla')
    tmpdir = tempfile.TemporaryDirectory()
    path = os.path.join(tmpdir.name, 'test.svg')
    plt.savefig(path)
    assert os.path.exists(path)

@pytest.mark.slow
def test_ranked_land_allocation():
    tmpdir = tempfile.TemporaryDirectory()
    path = pathlib.Path(tmpdir.name).joinpath('land/world')
    path.mkdir(parents=True, exist_ok=False)
    r = tools.world_data_xls_extract.WorldDataReader(key='land', outputdir=str(path))
    r.read_world_data_xls()
    r.make_csvs()
    tools.land_allocation.datadir = pathlib.Path(tmpdir.name)
    tools.land_allocation.datadir.joinpath('land/allocation2018/ranked').mkdir(parents=True)
    tools.land_allocation.ranked_land_allocation(csv_dirname='csv')
    rankedpath = os.path.join(tmpdir.name, 'land', 'allocation2018', 'ranked', 'csv')
    assert os.path.exists(os.path.join(rankedpath, 'solution_order.csv'))
    assert len(list(os.listdir(rankedpath))) >= 2
