import pytest
import ui.charts

@pytest.mark.slow
def test_JupyterUI():
    j = ui.charts.JupyterUI()
    # just checking if we get an exception for any reason
    _ = j.get_skeleton_ui()
    j.render_overview()
    first_soln = list(j.checkboxes.keys())[0]
    j.checkboxes[first_soln].value = True
    j.get_detailed_results_tabs()


def test_get_sector():
    j = ui.charts.JupyterUI()
    assert j._get_sector_for_solution('solarpvutil') == 'Electricity Generation'
    assert j._get_sector_for_solution('trains') == 'Transport'
    assert j._get_sector_for_solution('solution.trains') == 'Transport'
