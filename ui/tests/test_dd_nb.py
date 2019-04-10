"""Tests for dd_nb.py, functions to support Drawdown models in Jupyter notebooks."""

import ui.dd_nb as dd

def test_scenario_sort_key():
  unsorted = [
      'concentratedsolar:PDS-8p2050-Drawdown Optimum Scenario (Revision Case)',
      'solarpvutil:PDS3-16p2050-Optimum (Updated)',
      'concentratedsolar:PDS-8p2050-Drawdown Scenario (Revision Case)',
      'solarpvutil:PDS2-15p2050-Drawdown (Updated)',
      'concentratedsolar:PDS-4p2050-Drawdown Plausible (Revison Case)',
      'solarpvutil:PDS1-10p2050-Plausible (Updated)',
      ]
  # sort order should be by solution name first, followed by Plausible, Drawdown,
  # and finally Optimum scenarios.
  expected = [
      'concentratedsolar:PDS-4p2050-Drawdown Plausible (Revison Case)',
      'concentratedsolar:PDS-8p2050-Drawdown Scenario (Revision Case)',
      'concentratedsolar:PDS-8p2050-Drawdown Optimum Scenario (Revision Case)',
      'solarpvutil:PDS1-10p2050-Plausible (Updated)',
      'solarpvutil:PDS2-15p2050-Drawdown (Updated)',
      'solarpvutil:PDS3-16p2050-Optimum (Updated)',
      ]
  result = sorted(unsorted, key=dd.scenario_sort_key)
  assert result == expected
