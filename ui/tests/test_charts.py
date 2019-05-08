import ui.charts

def test_JupyterUI():
    ju = ui.charts.JupyterUI()
    _ = ju.get_overview()
    _ = ju.get_detailed_results_tabs()
