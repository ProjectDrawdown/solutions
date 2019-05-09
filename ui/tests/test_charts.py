import ui.charts

def test_JupyterUI():
    ju = ui.charts.JupyterUI()
    # just checking if we get an exception for any reason
    _ = ju.get_overview()
    _ = ju.get_detailed_results_tabs()

def test_get_sector():
    ju = ui.charts.JupyterUI()
    assert ju._get_sector_for_solution('solarpvutil') == 'Electricity Generation'
    assert ju._get_sector_for_solution('trains') == 'Transport'
    assert ju._get_sector_for_solution('solution.trains') == 'Transport'
