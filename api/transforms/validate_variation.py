import json
import re
import pickle
from api.transforms.variable_paths import varProjectionNamesPaths
from api.transforms.reference_variable_paths import varRefNamesPaths
from api.transform import legacyDataFiles
from api.transforms.ref_var_schema import ref_var_schema
from api.transforms.scenario_var_schema import scenario_var_schema
from api.calculate import fetch_data, build_json

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

pds_validation_matrix = {
  'Linear': {
    'fields': [
      {
        'key': 'technologies.*.adoption_base_adoption',
        'required': True
      }
    ]
  },
  'Existing Adoption Prognostications': {
    'fields': [
      {
        'key': 'technologies.*.adoption_prognostication_growth',
        'required': True,
        'values': ['Low', 'Medium', 'High'],
      },
      {
        'key': 'technologies.*.adoption_prognostication_trend',
        'required': True,
        'values': ['3rd Poly'],
      },
      {
        'key': 'technologies.*.adoption_prognostication_source',
        'required': True,
      }
    ]
  },
  'Fully Customized PDS': {
    'fields': [
        {
        'key': 'technologies.*.adoption_prognostication_growth',
        'required': False,
        'values': ['Low', 'Medium', 'High'],
        'warning': True
      },
    ]
  },
  'Bass Diffusion S-Curve': {
    'fields': [
      {
        'key': 'technologies.*.adoption_base_adoption',
        'required': True
      },
      {
        'key': 'technologies.*.adoption_prognostication_growth',
        'required': False,
        'values': ['Low', 'Medium', 'High'],
        'warning': True
      }
    ]
  },
  'Logistic S-Curve': {
    'fields': [
      {
        'key': 'technologies.*.adoption_base_adoption',
        'required': True
      },
      {
        'key': 'technologies.*.adoption_prognostication_growth',
        'required': False,
        'values': ['Low', 'Medium', 'High'],
        'warning': True
      }
    ]
  },
  'Customized S-Curve Adoption': {
    'fields': [
      {
        'key': 'technologies.*.adoption_base_adoption',
        'required': True
      },
      {
        'key': 'technologies.*.adoption_prognostication_growth',
        'required': False,
        'values': ['Low', 'Medium', 'High'],
        'warning': True
      }
    ]
  }
}

ref_validation_matrix = {
  'Default': {
    'fields': [
      {
        'key': 'technologies.*.adoption_base',
        'required': True
      },
      {
        'key': 'categories.electricity_generation.tam_source_post_start_year',
        'required': True
      }
    ]
  },
  'Custom': {
    'fields': [
      {
        'key': 'technologies.*.adoption_regional_data',
        'required': True
      }
    ]
  }
}

def validate(variation: dict, schema_dict: dict, name: str):
  for key in variation:
    schema = schema_dict.get(key)
    if not schema:
      tech = re.search(r'technologies\.([a-z]+)\.*', key).group(1)
      schema = schema_dict.get(key.replace(tech, '*'))
    if not schema:
      return [False, f'{key}: does not exist in schema']
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

  # if variation['adoption_basis']:
  #   pds_value = pds_validation_matrix.get(variation['adoption_basis'])
  #   if pds_value:
  #     for field in pds_value['fields']:
    
  return [True, '']

def field_name_to_legacy(new_path: str, technology: str) -> str:
  new_path = new_path.replace('*', technology)
  paths = varProjectionNamesPaths + varRefNamesPaths
  for [existing_name, path, converted_name, label, unit] in paths:
    technologyPath = path.replace('solarpvutil', technology)
    if new_path == technologyPath:
      return existing_name

async def validate_full_schema(variation: dict, client):
  warnings = []
  input_data = await fetch_data(variation.__dict__, client)
  jsons = build_json(2015, 2020, *input_data)
  for j in jsons:
    pds_basis = j['json']["soln_pds_adoption_basis"]
    ref_basis = j['json']['soln_ref_adoption_basis']
    rules = [
      pds_validation_matrix.get(pds_basis), 
      ref_validation_matrix.get(ref_basis)
    ]
    for rule in rules:
      if rule:
        for field in rule['fields']:
          legacy_field_name = field_name_to_legacy(field['key'], j['tech'])
          value = j['json'].get(legacy_field_name)
          field_key = field['key']

          input_field_key = field_key.replace("*", j["tech"])

          if value and field.get("warning"):
            warnings.append(f'{input_field_key} will be overidden')
          if field['required']:
            if value is None:
              return { 
                'valid': False,
                'reason': f'{input_field_key} missing'
              }
            values = field.get("values")
            if values and value not in values:
              return {
                'valid': False,
                'reason': f'{input_field_key} is not one of the following {values}'
              }

  return {
    'valid': True,
    'warnings': warnings
  }

