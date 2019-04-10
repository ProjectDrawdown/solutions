import ui.charts
from solution import solarpvutil

def test_get_overview():
    _ = ui.charts.get_overview()

def test_tabs():
    s = solarpvutil.SolarPVUtil()
    _ = ui.charts.get_detailed_results_tabs([s])
