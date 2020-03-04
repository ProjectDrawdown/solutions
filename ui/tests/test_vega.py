"""Tests for ui/vega.py, functions to generate Vega charts in Jupyter notebooks."""

import json
import pathlib

import jsonschema
import pandas as pd
import ui.vega

thisdir = pathlib.Path(__file__).parents[0]
datadir = pathlib.Path(__file__).parents[2].joinpath('data')


def test_vega_json_schema():
    schema = json.load(open(str(thisdir.joinpath('vega_v4.schema.json'))))
    solutions = pd.read_csv(str(datadir.joinpath('overview', 'solutions.csv')),
        index_col=False, skipinitialspace=True, header=0, skip_blank_lines=True, comment='#')
    soln_results = pd.read_csv(str(datadir.joinpath('overview', 'soln_results.csv')),
        index_col=False, skipinitialspace=True, header=0, skip_blank_lines=True, comment='#')
    solutions = solutions.merge(soln_results, on='Solution', how='left')
    instance = ui.vega.solution_treemap(
        solutions=solutions, width=400, height=800)
    # jsonschema.validate will raise an exception on failure
    jsonschema.validate(instance=instance, schema=schema)
    instance = ui.vega.solution_donut_chart(
        solutions=solutions, width=400, height=400)
    jsonschema.validate(instance=instance, schema=schema)
