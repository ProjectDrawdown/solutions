"""Tests for dd_nb.py, functions to support Drawdown models in Jupyter notebooks."""

import json
import pathlib

import jsonschema
import pandas as pd
import ui.dd_nb as dd

thisdir = pathlib.Path(__file__).parents[0]
datadir = pathlib.Path(__file__).parents[2].joinpath('data')

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

def test_vega_json_schema():
  schema = json.load(open(str(thisdir.joinpath('vega_v4.schema.json'))))
  solutions = pd.read_csv(str(datadir.joinpath('overview', 'solutions.csv')),
      index_col=False, skipinitialspace=True, header=0, skip_blank_lines=True, comment='#')
  soln_results = pd.read_csv(str(datadir.joinpath('overview', 'soln_results.csv')),
      index_col=False, skipinitialspace=True, header=0, skip_blank_lines=True, comment='#')
  solutions = solutions.merge(soln_results, on='Solution', how='left')
  instance = dd.solution_treemap(solutions=solutions, width=400, height=800)
  # jsonschema.validate will raise an exception on failure
  jsonschema.validate(instance=instance, schema=schema)
  instance = dd.solution_donut_chart(solutions=solutions, width=400, height=400)
  jsonschema.validate(instance=instance, schema=schema)
