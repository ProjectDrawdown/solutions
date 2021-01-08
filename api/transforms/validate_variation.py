import json
import pickle
from api.transforms.variable_paths import varProjectionNamesPaths
from api.transforms.reference_variable_paths import varRefNamesPaths
from api.transform import legacyDataFiles
from api.transforms.ref_var_schema import ref_var_schema
from api.transforms.scenario_var_schema import scenario_var_schema

def drill(d: dict) -> str:
  result = {}
  for key in d:
    if isinstance(d[key], dict):
      result[key] = drill(d[key])
    else:
      if isinstance(d[key], int):
        result[key] = f'{type(0.0)}'
      else:
        result[key] = f'{type(d[key])}'
  return result

def build_schema():
  schema = {}
  for [technology, filepath] in legacyDataFiles['drawdown-2020']:
    with open(filepath) as f:
      scenarioData = json.load(f)
      for [existing_name, path, converted_name, label, unit] in varRefNamesPaths:#varProjectionNamesPaths
        technologyPath = path.replace('solarpvutil', technology)
        if existing_name in scenarioData:
          if technologyPath not in schema:
            schema[technologyPath] = []
          if isinstance(scenarioData[existing_name], dict):
            drilled = drill(scenarioData[existing_name])
            if drilled not in schema[technologyPath]:
              schema[technologyPath].append(drilled)
          else:
            type_of_field = f'{type(scenarioData[existing_name])}'
            if type_of_field not in schema[technologyPath]:
              schema[technologyPath].append(type_of_field)
  # schema = dict([[field, list(schema[field])] for field in schema])
  with open('./schema.json', 'w') as f:
    f.write(json.dumps(schema))


def validate_scenario_vars(variation: dict):
  return validate(variation, scenario_var_schema, 'scenario')

def validate_ref_vars(variation: dict):
  return validate(variation, ref_var_schema, 'reference')

def validate(variation: dict, schema_dict: dict, name: str):
  for key in variation:
    schema = schema_dict[key]
    if isinstance(variation[key], dict):
      drilled = drill(variation[key])
      if drilled not in schema:
        found = False
        for option in schema:
          if option == drilled:
            found = True
        if not found:
          return [False, f'{key}: {variation[key]} not valid schema for {name}. Must be one of the following types: {schema}']
    elif f'{type(variation[key])}' not in schema:
      if isinstance(variation[key], int):
        if f'{type(0.0)}' not in schema:
          return [False, f'{key}: {variation[key]} not valid schema for {name}. Must be one of the following types: {schema}']
  return [True, '']

