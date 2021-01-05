import asyncio
import json
import hashlib
from fastapi import HTTPException
from pandas import DataFrame, Series
from model.data_handler import DataHandler

from solution import factory, factory_2

from api.config import AioWrap, get_resource_path
from api.queries.workbook_queries import workbook_by_commit
from api.transform import rehydrate_legacy_json
from api.db.models import Workbook

def to_json(scenario):
    json_data = dict()
    instance_vars = vars(scenario).keys()
    for iv in instance_vars:
        try:
            obj = getattr(scenario, iv)
            if issubclass(type(obj), DataHandler):
                json_data[iv] = obj.to_json()
                for jv in json_data[iv]:
                  if type(json_data[iv][jv]) in [DataFrame, Series]:
                    json_data[iv][jv] = json.loads(json_data[iv][jv].to_json())
        except BaseException:
            json_data[iv] = None
    json_data.pop('tm', None)
    json_data.pop('ae', None)
    return {'name': scenario.name, 'data': json_data}

async def calc(constructor, input, hashed_json_input, technology):
    return [to_json(constructor(input)), hashed_json_input, technology]

async def fetch_data(variation_path, client) -> [dict, dict, dict]:
  variation_data = await client(variation_path)
  if not variation_data:
    raise HTTPException(status_code=400, detail=f"Variation not found: {variation_path}")
  scenario_parent_path = variation_data['data']['scenario_parent_path']
  reference_parent_path = variation_data['data']['reference_parent_path']
  scenario_data = await client(scenario_parent_path)
  if not scenario_data:
    raise HTTPException(status_code=400, detail=f"Scenario not found: {scenario_parent_path}")
  reference_data = await client(reference_parent_path)
  if not reference_data:
    raise HTTPException(status_code=400, detail=f"Reference not found: {reference_parent_path}")
  return [variation_data, scenario_data, reference_data]

def build_json(start_year: int, end_year: int, variation_data: dict, scenario_data: dict, reference_data: dict):
  jsons = list(map(lambda tech: {
    'tech': tech,
    'json': rehydrate_legacy_json(
      start_year,
      end_year,
      tech,
      scenario_data['data'],
      reference_data['data'],
      variation_data['data'])
    }, scenario_data['data']['technologies']))
  return list(filter(lambda json: json['tech'] != 'fossilfuelelectricity', jsons))

async def setup_calculations(jsons, cache):
  tasks = []
  key_list = []
  json_cached_results = []
  constructors = factory_2.all_solutions_scenarios(jsons)

  for constructor in constructors:
    current_json_input: dict = list(filter(lambda json: json['tech'] == constructor, jsons))[0]
    name = current_json_input['json']['name']
    technology = current_json_input['tech']
    copied_json_input = current_json_input.copy()
    # deleting vmas because they're not always serializable (todo?)
    del copied_json_input['json']['vmas']
    hashed_json_input = hashlib.md5(json.dumps(copied_json_input).encode('utf-8')).hexdigest()

    cached_result = await cache.get(hashed_json_input)
    if cached_result is None:
      tasks.append(calc(constructors[constructor][0], name, hashed_json_input, technology))
    else:
      key_list.append([technology, name, hashed_json_input])
      json_cached_results.append(json.loads(cached_result))
  return [tasks, key_list, json_cached_results]

async def perform_calculations(tasks, cache, key_list):
  json_results = []
  if len(tasks) > 0:
    calculated_results = await asyncio.wait(tasks)
    for r in calculated_results[0]:
      [json_result, key_hash, tech] = r._result
      json_results.append(json_result)
      await cache.set(key_hash, json.dumps(json_result))
      key_list.append([tech, json_result['name'], key_hash])
  return [json_results, key_list]

def build_result_paths(key_list):
  return [{
      'path': get_resource_path('projection', key_hash),
      'technology': tech,
      'technology_full': tech_full
    } for [tech, tech_full, key_hash] in key_list]

async def calculate(workbook_commit_id, client, db, cache):
  cached_result = await cache.get(workbook_commit_id)
  if cached_result is not None:
    return json.loads(cached_result)

  workbook: Workbook = workbook_by_commit(db, workbook_commit_id)
  if workbook is None:
    raise HTTPException(status_code=400, detail="Workbook not found")
  result_paths = []
  for variation_path in workbook.variations:
    input_data = await fetch_data(variation_path, client)
    jsons = build_json(workbook.start_year, workbook.end_year, *input_data)
    [tasks, key_list, _] = await setup_calculations(jsons, cache)
    [_, key_list] = await perform_calculations(tasks, cache, key_list)
    result_paths += build_result_paths(key_list)
    await cache.set(workbook_commit_id, json.dumps(result_paths))

  return result_paths