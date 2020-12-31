import json
from os import listdir
from os.path import isfile, join
from api.transforms.variable_paths import varProjectionNamesPaths
from api.transforms.reference_variable_paths import varRefNamesPaths
from api.transforms.metadata import pythonFieldMetadataArray

legacyDataFiles = {
  'drawdown-2020': [

    # Electricity Generation
    ["onshorewind","solution/onshorewind/ac/PDS-27p2050-Drawdown2020.json"],
    ["offshorewind","solution/offshorewind/ac/PDS-3p2050-Drawdown2020.json"],
    ["nuclear","solution/nuclear/ac/PDS-9p2050-Drawdown2020.json"],
    ["waveandtidal","solution/waveandtidal/ac/PDS-1p2050-Drawdown2020.json"],
    ["solarpvroof","solution/solarpvroof/ac/PDS-14p2050-Drawdown2020.json"],
    ["geothermal","solution/geothermal/ac/PDS-3p2050-Drawdown2020.json"],
    ["biogas","solution/biogas/ac/PDS-1p2050-Drawdown2020.json"],
    ["biomass","solution/biomass/ac/PDS-1p2050-Drawdown2020.json"],
    ["solarpvutil","solution/solarpvutil/ac/PDS-25p2050-Drawdown2020.json"],
    ["instreamhydro","solution/instreamhydro/ac/PDS-2p2050-Drawdown2020.json"],
    ["concentratedsolar","solution/concentratedsolar/ac/PDS-6p2050-Drawdown2020.json"],
    ["microwind","solution/microwind/ac/PDS-0p2050-Drawdown2020.json"],

    # Food
    ["silvopasture","solution/silvopasture/ac/PDS-94p2050-Drawdown-customPDS-avg-Jan2020.json"],
    ["biochar","solution/biochar/ac/PDS-16p2050-Drawdown-CustomPDS-High-Jan2020.json"],
    ["treeintercropping","solution/treeintercropping/ac/PDS-99p2050-Drawdown-customPDS-high-30Jan2020.json"],
    ["tropicaltreestaples","solution/tropicaltreestaples/ac/PDS-43p2050-Drawdown-customPDS-avg-Jan2020.json"],
    ["conservationagriculture","solution/conservationagriculture/ac/PDS-44p2050-Drawdown-customPDS-highhighearly-Jan2020.json"],
    ["managedgrazing","solution/managedgrazing/ac/PDS-65p2050-Drawdown-customPDS-high-Jan2020.json"],
    ["improvedrice","solution/improvedrice/ac/PDS-100p2050-Drawdown-customPDS-high-Jan2020.json"],
    ["riceintensification","solution/riceintensification/ac/PDS-100p2050-Drawdown-CustomPDS-high-Jan2020.json"],
    ["farmlandrestoration","solution/farmlandrestoration/ac/PDS-80p2050-Drawdown-customPDS-high-29Jan2020.json"],
    ["multistrataagroforestry","solution/multistrataagroforestry/ac/PDS-20p2050-Drawdown-customPDS-avg-Jan2020.json"],
    ["regenerativeagriculture","solution/regenerativeagriculture/ac/PDS-47p2050-Drawdown-customPDS-high-29Jan2020.json"],
    ["nutrientmanagement","solution/nutrientmanagement/ac/PDS-58p2050-Drawdown-customPDS-avg-Jan2020.json"],

    # Land Use
    ["peatlands","solution/peatlands/ac/PDS-97p2050-Drawdown-customPDS-high-Jan2020.json"],
    ["forestprotection","solution/forestprotection/ac/PDS-97p2050-Drawdown-customPDS-high-Jan2020.json"],
    ["bamboo","solution/bamboo/ac/PDS-57p2050-Drawdown-customPDS-high-Jan2020.json"],
    ["indigenouspeoplesland","solution/indigenouspeoplesland/ac/PDS-99p2050-Drawdown-customPDS-high-Jan2020.json"],
    ["afforestation","solution/afforestation/ac/PDS-65p2050-Drawdown-CustomPDS-high05stdv-Jan2020.json"],
    ["grasslandprotection","solution/grasslandprotection/ac/PDS-87p2050-Drawdown-customPDS-high-Jan2020.json"],
    ["perennialbioenergy","solution/perennialbioenergy/ac/PDS-72p2050-Drawdown-customPDS-high-30Jan2020.json"],
    ["temperateforests","solution/temperateforests/ac/PDS-86p2050-Drawdown-customPDS-high-Jan2020.json"],

    # Buildings and Cities
    ["landfillmethane","solution/landfillmethane/ac/PDS-0p2050-Drawdown2020.json"],

  ]
}

pythonFieldMetadataObj = {}
for field in pythonFieldMetadataArray:
  pythonFieldMetadataObj[field[0]] = field[1]
  pythonFieldMetadataObj[field[0]]['type'] = field[2]

def set_value_at(obj, path: str, value):
  path_keys = path.split('.')
  current_obj = obj
  for i in range(len(path_keys)):
    key = path_keys[i]
    if key not in current_obj.keys():
      current_obj[key] = {}
    if i == len(path_keys) - 1:
      current_obj[key] = value
    current_obj = current_obj[key]

def get_value_at(obj, path: str):
  path_keys = path.split('.')
  current_obj = obj
  for i in range(len(path_keys)):
    key = path_keys[i]
    if key not in current_obj.keys():
      return None
    else:
        current_obj = current_obj[key]
    if i == len(path_keys) - 1:
      return current_obj

def transform():
  # # with open('solution/solarpvutil/ac/PDS-25p2050-Drawdown2020.json') as f:

  # #   data = json.load(f)

  # projection_schema = {}
  # # variation_schema = {}

  # for [existing_name, path, converted_name, label, unit] in varProjectionNamesPaths:
  #   obj = {
  #     'name': converted_name,
  #     'label': label,
  #     'fieldType': unit
  #   }
  #   if existing_name in pythonFieldMetadataObj:
  #     obj['pythonMetadata'] = pythonFieldMetadataObj[existing_name]
  #   add(projection_schema, path, obj)

  # variation_schema = projection_schema.copy()

  jsonProjectionData = {
    # 'start_year': 2014
  }
  jsonRefData = {}

  for [technology, filenameData] in legacyDataFiles['drawdown-2020']:
    with open(filenameData) as f:
      sampleScenarioData = json.load(f)
      for [existing_name, path, converted_name, label, unit] in varProjectionNamesPaths:
        technologyPath = path.replace('solarpvutil', technology)
        if existing_name in sampleScenarioData:
          value = sampleScenarioData[existing_name]
          if value == value:
            #nan != nan
            #edge case scenario
            set_value_at(jsonProjectionData, technologyPath, value)

      for [existing_name, path, converted_name, label, unit] in varRefNamesPaths:
        technologyPath = path.replace('solarpvutil', technology)
        if existing_name in sampleScenarioData:
          value = sampleScenarioData[existing_name]
          if value == value:
            #nan != nan
            #edge case scenario
            set_value_at(jsonRefData, technologyPath, value)


  return [jsonProjectionData, jsonRefData]

def get_solution_file_paths(solution_name):
    path = f'solution/{solution_name}/ac/'
    onlyfiles = [f'{path}{f}' for f in listdir(path) if isfile(join(path, f))]
    return onlyfiles

def transform_technology_scenario(technology, path):
    jsonProjectionData = {}
    with open(path) as f:
      scenarioData = json.load(f)
      for [existing_name, path, converted_name, label, unit] in varProjectionNamesPaths:
        # hacky
        technologyPath = path.replace('solarpvutil', technology)
        if existing_name in scenarioData:
          set_value_at(jsonProjectionData, technologyPath, scenarioData[existing_name])
    return jsonProjectionData

def transform_technology_reference(technology, path):
  jsonReferenceData = {}
  with open(path) as f:
    scenarioData = json.load(f)
    for [existing_name, path, converted_name, label, unit] in varRefNamesPaths:
      # hacky
      technologyPath = path.replace('solarpvutil', technology)
      if existing_name in scenarioData:
        set_value_at(jsonReferenceData, technologyPath, scenarioData[existing_name])
  return jsonReferenceData

def rehydrate_legacy_json(technology, tech_scenario_json, tech_reference_json, overrides):
  rehydrated_json = {}
  for [existing_name, path, converted_name, label, unit] in varProjectionNamesPaths:
    technologyPath = path.replace('solarpvutil', technology)
    value = get_value_at(tech_scenario_json, technologyPath)
    if technologyPath in overrides['scenario_vars']:
      override = overrides['scenario_vars'][technologyPath]
      if override is not None:
        value = override
    if value is not None:
      rehydrated_json[existing_name] = value
  for [existing_name, path, converted_name, label, unit] in varRefNamesPaths:
    technologyPath = path.replace('solarpvutil', technology)
    value = get_value_at(tech_reference_json, technologyPath)
    if technologyPath in overrides['reference_vars']:
      override = overrides['reference_vars'][technologyPath]
      if override is not None:
        value = override
    if value is not None:
      rehydrated_json[existing_name] = value
  return rehydrated_json

