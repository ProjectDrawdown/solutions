import os.path
import tempfile

import matplotlib.pyplot as plt
import tools.land_allocation

def test_plots():
    tools.land_allocation.plot_solution_allocation('peatlands', 'matching_tla')
    tools.land_allocation.plot_tla_remaining('matching_tla')
    tmpdir = tempfile.TemporaryDirectory()
    path = os.path.join(tmpdir.name, 'test.svg')
    plt.savefig(path)
    assert os.path.exists(path)
