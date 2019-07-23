import ui.charts

def test_JupyterUI():
    j = ui.charts.JupyterUI()
    # just checking if we get an exception for any reason
    _ = j.get_skeleton_ui()
    j.render_overview()

def test_get_sector():
    j = ui.charts.JupyterUI()
    assert j._get_sector_for_solution('solarpvutil') == 'Electricity Generation'
    assert j._get_sector_for_solution('trains') == 'Transport'
    assert j._get_sector_for_solution('solution.trains') == 'Transport'
