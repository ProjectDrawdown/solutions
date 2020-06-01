"""Test for zenodo.json schema conformance. See issue #102 for details."""

import json
import pathlib
import jsonschema

thisdir = pathlib.Path(__file__).parents[0]
parentdir = pathlib.Path(__file__).parents[1]


def test_zenodo_json_schema():
    with open(str(thisdir.joinpath('zenodo_v1.schema.json'))) as s:
        schema = json.loads(s.read())
    with open(str(parentdir.joinpath('.zenodo.json'))) as z:
        instance = json.loads(z.read())
    jsonschema.validate(instance=instance, schema=schema)