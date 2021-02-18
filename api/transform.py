import json
import csv
import os
import importlib
from typing import List
from os import listdir
from os.path import isfile, join
from api.transforms.variable_paths import varProjectionNamesPaths
from api.transforms.reference_variable_paths import varRefNamesPaths
from api.transforms.metadata import pythonFieldMetadataArray
from model.advanced_controls import AdvancedControls, get_vma_for_param, get_param_for_vma_name

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
  ],
  'plausible-2020': [

    # Electricity Generation
    ["onshorewind","solution/onshorewind/ac/PDS-20p2050-Plausible2020.json"],
    ["offshorewind","solution/offshorewind/ac/PDS-4p2050-Plausible2020.json"],
    ["nuclear","solution/nuclear/ac/PDS-13p2050-Plausible2020.json"],
    ["waveandtidal","solution/waveandtidal/ac/PDS-1p2050-Plausible2020.json"],
    ["solarpvroof","solution/solarpvroof/ac/PDS-14p2050-Plausible2020.json"],
    ["geothermal","solution/geothermal/ac/PDS-3p2050-Plausible2020.json"],
    ["biogas","solution/biogas/ac/PDS-2p2050-Plausible2020.json"],
    ["biomass","solution/biomass/ac/PDS-1p2050-Plausible2020.json"],
    ["solarpvutil","solution/solarpvutil/ac/PDS-20p2050-Plausible2020.json"],
    ["instreamhydro","solution/instreamhydro/ac/PDS-2p2050-Plausible2020.json"],
    ["concentratedsolar","solution/concentratedsolar/ac/PDS-7p2050-Plausible2020.json"],
    ["microwind","solution/microwind/ac/PDS-0p2050-Plausible2020.json"],

    # Food
    ["silvopasture","solution/silvopasture/ac/PDS-88p2050-Plausible-customPDS-low-Jan2020.json"],
    ["biochar","solution/biochar/ac/PDS-8p2050-Plausible-CustomPDS-Avg-Jan2020.json"],
    ["treeintercropping","solution/treeintercropping/ac/PDS-84p2050-Plausible-customPDS-avg-30Jan2020.json"],
    ["tropicaltreestaples","solution/tropicaltreestaples/ac/PDS-18p2050-Plausible-customPDS-low-Jan2020.json"],
    ["conservationagriculture","solution/conservationagriculture/ac/PDS-54p2050-Plausible-customPDS-high-Jan2020.json"],
    ["managedgrazing","solution/managedgrazing/ac/PDS-43p2050-Plausible-customPDS-avg-Jan2020.json"],
    ["improvedrice","solution/improvedrice/ac/PDS-84p2050-Plausible-customPDS-avg-Jan2020.json"],
    ["riceintensification","solution/riceintensification/ac/PDS-77p2050-Plausible-CustomPDS-avg-Jan2020.json"],
    ["farmlandrestoration","solution/farmlandrestoration/ac/PDS-51p2050-Plauisble-customPDS-avg-29Jan2020.json"],
    ["multistrataagroforestry","solution/multistrataagroforestry/ac/PDS-12p2050-Plausible-customPDS-low-Jan2020.json"],
    ["regenerativeagriculture","solution/regenerativeagriculture/ac/PDS-32p2050-Plausible-customPDS-29Jan2020.json"],
    ["nutrientmanagement","solution/nutrientmanagement/ac/PDS-27p2050-Plausible-customPDS-low-Jan2020.json"],

    # Land Use
    ["peatlands","solution/peatlands/ac/PDS-58p2050-Plausible-customPDS-avg-Jan2020.json"],
    ["forestprotection","solution/forestprotection/ac/PDS-85p2050-Plausible-customPDS-avg-Jan2020.json"],
    ["bamboo","solution/bamboo/ac/PDS-28p2050-Plausible-customPDS-avg-Jan2020.json"],
    ["indigenouspeoplesland","solution/indigenouspeoplesland/ac/PDS-86p2050-Plausible-customPDS-avg-Jan2020.json"],
    ["afforestation","solution/afforestation/ac/PDS-57p2050-Plausible-CustomPDS-Avg-Jan2020.json"],
    ["grasslandprotection","solution/grasslandprotection/ac/PDS-74p2050-Plausible-customPDS-avg-Jan2020.json"],
    ["perennialbioenergy","solution/perennialbioenergy/ac/PDS-40p2050-Plausible-customPDS-avg-30Jan2020.json"],
    ["temperateforests","solution/temperateforests/ac/PDS-62p2050-Plausible-customPDS-avg-Jan2020.json"],

    # Buildings and Cities
    ["landfillmethane","solution/landfillmethane/ac/PDS-0p2050-Plausible2020.json"],
  ],
  'optimum-2020': [

    # Electricity Generation
    ["onshorewind","solution/onshorewind/ac/PDS-27p2050-Optimum2020.json"],
    ["offshorewind","solution/offshorewind/ac/PDS-6p2050-Optimum2020.json"],
    ["nuclear","solution/nuclear/ac/PDS-0p2050-Optimum2020.json"],
    ["waveandtidal","solution/waveandtidal/ac/PDS-2p2050-Optimum2020.json"],
    ["solarpvroof","solution/solarpvroof/ac/PDS-14p2050-Optimum2020.json"],
    ["geothermal","solution/geothermal/ac/PDS-6p2050-Optimum2020.json"],
    ["biogas","solution/biogas/ac/PDS-1p2050-Optimum2020.json"],
    ["biomass","solution/biomass/ac/PDS-1p2050-Optimum2020.json"],
    ["solarpvutil","solution/solarpvutil/ac/PDS-25p2050-Optimum2020.json"],
    ["instreamhydro","solution/instreamhydro/ac/PDS-2p2050-Optimum2020.json"],
    ["concentratedsolar","solution/concentratedsolar/ac/PDS-6p2050-Optimum2020.json"],
    ["microwind","solution/microwind/ac/PDS-0p2050-Optimum2020.json"],

    # Food
    ["silvopasture","solution/silvopasture/ac/PDS-100p2050-Optimum-customPDS-high-Jan2020.json"],
    ["biochar","solution/biochar/ac/PDS-20p2050-Optimum-CustomPDS-max-Jan2020.json"],
    ["treeintercropping","solution/treeintercropping/ac/PDS-100p2050-Optimum.json"],
    ["tropicaltreestaples","solution/tropicaltreestaples/ac/PDS-67p2050-Optimum-customPDS-high-Jan2020.json"],
    ["conservationagriculture","solution/conservationagriculture/ac/PDS-31p2050-Optimum-PDSCustom-avg-Nov2019.json"],
    ["managedgrazing","solution/managedgrazing/ac/PDS-62p2050-Optimum-BookVersion1-High2S.json"],
    ["improvedrice","solution/improvedrice/ac/PDS-100p2050-Optimum-PDS_Custom-High_Growth,_Early_Adoption.json"],
    ["riceintensification","solution/riceintensification/ac/PDS-100p2050-Optimum-CustomPDS-highearly-Jan2020.json"],
    ["farmlandrestoration","solution/farmlandrestoration/ac/PDS-87p2050-Optimum-PDScustom-high-BookVersion1.json"],
    ["multistrataagroforestry","solution/multistrataagroforestry/ac/PDS-28p2050-optimum-customPDS-high-Jan2020.json"],
    ["regenerativeagriculture","solution/regenerativeagriculture/ac/PDS-62p2050-Optimum-PDScustom-max-BookVersion1.json"],
    ["nutrientmanagement","solution/nutrientmanagement/ac/PDS-80p2050-Optimum-PDScustom-max-BookVersion1.json"],

    # Land Use
    ["peatlands","solution/peatlands/ac/PDS-95p2050-Optimum-PDSCustom-80%lowdeg-Nov2019.json"],
    ["forestprotection","solution/forestprotection/ac/PDS-99p2050-Optimum-customPDS-100%lowdeg-Jan2020.json"],
    ["bamboo","solution/bamboo/ac/PDS-69p2050-Optimum-PDScustom-high-BookVersion1.json"],
    ["indigenouspeoplesland","solution/indigenouspeoplesland/ac/PDS-91p2050-Optimum-PDScustom-high-BookVersion1.json"],
    ["afforestation","solution/afforestation/ac/PDS-82p2050-Optimum-PDSCustom-high-Nov2019.json"],
    ["grasslandprotection","solution/grasslandprotection/ac/PDS-85p2050-Optimum-PDSCustom-max-Nov2019.json"],
    ["perennialbioenergy","solution/perennialbioenergy/ac/PDS-100p2050-Optimum-PDScustom-high-BookVersion1.json"],
    ["temperateforests","solution/temperateforests/ac/PDS-74p2050-Optimum-PDScustomadoption-max.json"],

    # Buildings and Cities
    ["landfillmethane","solution/landfillmethane/ac/PDS-0p2050-Optimum2020.json"],
  ],
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

def rehydrate_legacy_json(start_year: int, end_year: int, technology: str, tech_scenario_json, tech_reference_json, overrides):
  rehydrated_json = {}
  override_scenario = flatten_variation(overrides['scenario_vars'])
  override_reference = flatten_variation(overrides['reference_vars'])
  for [existing_name, path, converted_name, label, unit] in varProjectionNamesPaths:
    technologyPath = path.replace('solarpvutil', technology)
    value = get_value_at(tech_scenario_json, technologyPath)
    if technologyPath in override_scenario:
      override = override_scenario[technologyPath]
      if override is not None:
        value = override
    if value is not None:
      rehydrated_json[existing_name] = value
  for [existing_name, path, converted_name, label, unit] in varRefNamesPaths:
    technologyPath = path.replace('solarpvutil', technology)
    value = get_value_at(tech_reference_json, technologyPath)
    if technologyPath in override_reference:
      override = override_reference[technologyPath]
      if override is not None:
        value = override
    if value is not None:
      rehydrated_json[existing_name] = value
  rehydrated_json['report_start_year'] = start_year
  rehydrated_json['report_end_year'] = end_year
  return rehydrated_json

def csv_to_json(csvFilePath: str) -> dict: 
      
  # create a dictionary 
  data = []
    
  # Open a csv reader called DictReader 
  with open(csvFilePath, encoding='utf-8') as csvf: 
      csvReader = csv.DictReader(csvf) 
        
      # Convert each row into a dictionary  
      # and add it to data 
      for row in csvReader: 
            
          # Assuming a column named 'No' to 
          # be the primary key 
          # key = rows['No'] 
          # data[key] = rows 
          data.append(row)

  return {'rows':data}

def csv_to_binary(csvFilePath: str) -> bytes:
   with open(csvFilePath, 'rb') as f:
    return f.read()

def populate(resource: str):
  # resource can be one of the following:
  #   vma_data, tam, ca_pds_data, ca_ref_data

  directory = 'solution'
  converted_list = []

  for subdir, _, _ in os.walk(directory):
    for subdir_vma, _, files in os.walk(f'{subdir}/{resource}'):
      for file in files:
        path = os.path.join(subdir_vma, file)
        converted = {
         'data': csv_to_json(path),
         'technology': subdir,
         'filename': file
        }
        converted_list.append(converted)
        
  return converted_list

def convert_to_new_path(legacy_name: str, technology: str) -> str:
  paths = varProjectionNamesPaths + varRefNamesPaths
  for [existing_name, path, converted_name, label, unit] in paths:
    technologyPath = path.replace('solarpvutil', technology)
    if legacy_name == existing_name:
      return technologyPath

def convert_vmas_to_binary() -> List[dict]:
  directory = 'solution'
  converted_list = []
  get_param_for_vma_name('s')
  for subdir, _, _ in os.walk(directory):

    for subdir_vma, _, files in os.walk(f'{subdir}/vma_data'):
      technology = subdir.split('/')[1]
      importname = 'solution.' + technology
      m = importlib.import_module(importname)
      for file in files:
        mappings = dict(map(lambda v: (str(m.VMAs[v].filename).split('/')[-1], v), filter(lambda v: m.VMAs[v].filename, m.VMAs)))
        if file in mappings:
          path = os.path.join(subdir_vma, file)
          vma_name = mappings[file]
          legacy_var_name = get_param_for_vma_name(vma_name)
          if legacy_var_name:
            updated_path = convert_to_new_path(legacy_var_name, technology)
            vma = {
            'data': csv_to_binary(path),
            'technology': technology,
            'filename': file,
            'path': updated_path,
            'legacy_variable': legacy_var_name,
            }
            converted_list.append(vma)
        
  return converted_list

def flatten_variation(obj):
  def inner(obj, path): 
    paths = []
    if isinstance(obj, dict) and ('value' not in obj) and ('World' not in obj) and ('EU' not in obj) and ('USA' not in obj) and ('China' not in obj) and ('India' not in obj) and ('OECD90' not in obj) and ('Latin America' not in obj) and ('Eastern Europe' not in obj) and ('Asia (Sans Japan)' not in obj) and ('Middle East and Africa' not in obj):
      for key in obj:
        result = inner(obj[key], f'{path}.{key}' if path else key)
        if isinstance(result, list):
          paths = paths + [*result]
        else:
          paths.append(result)
      return paths
    else:
      return {path: obj}
  transformed = inner(obj, None)
  result = {}
  for path in transformed:
    result = {**result, **path}
  return result
