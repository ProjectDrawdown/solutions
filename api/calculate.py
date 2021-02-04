from typing import Optional, Dict, Any, List
import asyncio
import json
import re
import hashlib
from fastapi import HTTPException, WebSocket
from pandas import DataFrame, Series
from deepdiff import DeepDiff
import concurrent.futures

from model.data_handler import DataHandler
from solution import factory, factory_2

from api.config import AioWrap, get_projection_path, get_settings
from api.queries.workbook_queries import workbook_by_id
from api.transform import rehydrate_legacy_json
from api.db.models import Workbook

import cProfile
import pstats
import io

import ntpath
import pathlib

settings = get_settings()

def map_to_json(mapping):
  if mapping is None:
    return None
  if isinstance(mapping, pathlib.PosixPath):
    return mapping.name
  elif isinstance(mapping, str):
    return ntpath.basename(mapping)
  elif isinstance(mapping, dict):
    return dict(map(lambda key: (key, map_to_json(mapping[key])), mapping))

def to_json(scenario, regions):
    json_data = dict()
    instance_vars = vars(scenario).keys()
    metadata = {}

    if getattr(scenario, 'ad', None):
      metadata['ad_data_sources'] = map_to_json(getattr(scenario.ad, 'data_sources', None))
    if getattr(scenario, 'tm', None):
      metadata['tam_pds_data_sources'] = map_to_json(getattr(scenario.tm, 'tam_pds_data_sources', None))
      metadata['tam_ref_data_sources'] = map_to_json(getattr(scenario.tm, 'tam_ref_data_sources', None))
    if getattr(scenario, 'pds_ca', None):
      metadata['pds_ca_data_sources'] = map_to_json(getattr(scenario.pds_ca, 'data_sources', None))
    if getattr(scenario, 'ref_ca', None):
      metadata['ref_ca_data_sources'] = map_to_json(getattr(scenario.ref_ca, 'data_sources', None))

    for iv in instance_vars:
      try:
          obj = getattr(scenario, iv)
          if issubclass(type(obj), DataHandler):
              json_data[iv] = obj.to_json(regions)
              for jv in json_data[iv]:
                if type(json_data[iv][jv]) in [DataFrame, Series]:
                  json_data[iv][jv] = json.loads(json_data[iv][jv].to_json())
      except BaseException as e:
            json_data[iv] = None
    if 'c2' in json_data and json_data['c2']:
      year_calculation = 'co2_ppm_calculator'
      if year_calculation in json_data['c2']:
        calculator = json_data['c2'][year_calculation]
        json_data['c2'][year_calculation] = {
            **dict({
                'years': [{'year': key, 'data': calculator[key]} for key in calculator if key.isdigit()],
            }),
            **dict([[key, calculator[key]] for key in calculator if not key.isdigit()])
        }
    return {'name': scenario.name, 'data': json_data, 'metadata': metadata}

# async def calc(input, hashed_json_input, technology, json_input, prev_results, key_list, cache, websocket, do_diffs):
#   constructor = factory_2.one_solution_scenarios(technology, json_input)[0]
#   try:
#     result = to_json(constructor(input))
#   except Exception as e:
#     result = e
#   await process_tech_calc(result, hashed_json_input, prev_results, technology, key_list, cache, websocket, do_diffs)
#   return result

def calc(input, hashed_json_input, technology, regions, json_input, prev_results, key_list, cache, websocket, do_diffs):
  constructor = factory_2.one_solution_scenarios(technology, json_input)[0]
  try:
    result = to_json(constructor(input), regions)
  except Exception as e:
    result = e
  return (result, input, hashed_json_input, technology, json_input, prev_results, key_list, cache, websocket, do_diffs)

def run(corofn, *args):
  loop = asyncio.new_event_loop()
  try:
      coro = corofn(*args)
      asyncio.set_event_loop(loop)
      return loop.run_until_complete(coro)
  finally:
      loop.close()

async def fetch_data(variation, client) -> [dict, dict, dict]:
  scenario_parent_path = variation['scenario_parent_path']
  reference_parent_path = variation['reference_parent_path']
  scenario_data = await client(scenario_parent_path)
  if not scenario_data:
    raise HTTPException(status_code=400, detail=f"Scenario not found: {scenario_parent_path}")
  reference_data = await client(reference_parent_path)
  if not reference_data:
    raise HTTPException(status_code=400, detail=f"Reference not found: {reference_parent_path}")
  return [variation, scenario_data, reference_data]

def build_json(start_year: int, end_year: int, variation_data: dict, scenario_data: dict, reference_data: dict):
  jsons = list(map(lambda tech: {
    'tech': tech,
    'json': rehydrate_legacy_json(
      start_year,
      end_year,
      tech,
      scenario_data['data'],
      reference_data['data'],
      variation_data)
    }, scenario_data['data']['technologies']))
  return list(filter(lambda json: json['tech'] != 'fossilfuelelectricity', jsons))

async def setup_calculations(jsons, regions, prev_data, cache, websocket: WebSocket, do_diffs: bool):
  tasks = []
  key_list = []
  json_cached_results = []

  for current_json_input in jsons:
    # current_json_input: dict = list(filter(lambda json: json['tech'] == constructor, pruned_jsons))[0]
    name = current_json_input['json']['name']
    technology = current_json_input['tech']
    copied_json_input = current_json_input.copy()
    # deleting vmas because they're not always serializable (todo?)
    del copied_json_input['json']['vmas']
    hashed_json_input = hashlib.md5(json.dumps(copied_json_input).encode('utf-8')).hexdigest()

    cached_result = await cache.get(hashed_json_input)
    if cached_result is None:
      # Inputs have changed for technology
      # tasks.append(asyncio.create_task(calc(
      #   name,
      #   hashed_json_input,
      #   technology,
      #   current_json_input['json'],
      #   prev_data,
      #   key_list,
      #   cache,
      #   websocket,
      #   do_diffs)))
      tasks.append((
        name,
        hashed_json_input,
        technology,
        regions,
        current_json_input['json'],
        prev_data,
        key_list,
        cache,
        websocket,
        do_diffs))
    else:
      # Inputs have not changed for technology
      key_list.append([technology, name, hashed_json_input, False])
      str_cached_result = json.loads(cached_result)
      json_cached_results.append(str_cached_result)
      if websocket:
        await websocket.send_text(str_cached_result)
  return [tasks, key_list, json_cached_results]

async def find_diffs(prev_result_list, tech, json_result, key_hash, key_list, cache, websocket):
  prev_tech_result = [result for result in prev_result_list if result['technology'] == tech][0]
  prev_cached_json_result = json.loads(await cache.get(prev_tech_result['hash']))
  # do diff
  diff = DeepDiff(json_result, prev_cached_json_result, ignore_order=True)
  if diff:
    # diffs found
    cache_diff_str = json.dumps({
      'tech': tech,
      'diff': diff
    })
    await cache.set(f'diff-{key_hash}', cache_diff_str)
    if websocket:
      await websocket.send_text(cache_diff_str)
    key_list.append([tech, json_result['name'], key_hash, True])
  else:
    # no diff in tech from previous run
    key_list.append([tech, json_result['name'], key_hash, False])

async def process_tech_calc(json_result, key_hash, prev_results, tech, key_list, cache, websocket, do_diffs: bool):
  str_json_result = json.dumps(json_result)
  if websocket:
    await websocket.send_text(str_json_result)
  await cache.set(key_hash, str_json_result)
  if prev_results and do_diffs:
    await find_diffs(prev_results['results'], tech, json_result, key_hash, key_list, cache, websocket)
  else:
    key_list.append([tech, json_result['name'], key_hash, False])

async def perform_calculations_async(tasks):
  json_results = []
  # if len(tasks) > 0:
  #   calculated_results = await asyncio.wait(tasks)
  #   for r in calculated_results[0]:
  #     json_result = r._result
  #     json_results.append(json_result)

  if len(tasks) > 0:
    with concurrent.futures.ThreadPoolExecutor(max_workers=settings.max_workers) as pool:

      # futures = {pool.submit(run, calc, *task) for task in tasks}
      loop = asyncio.get_event_loop()
      futures = [loop.run_in_executor(pool, calc, *task) for task in tasks]

      # for future in concurrent.futures.as_completed(futures):
      #   data = future.result()
      #   json_results.append(data)
      results = await asyncio.gather(*futures)
      for r in results:
        (result, input, hashed_json_input, technology, json_input, prev_results, key_list, cache, websocket, do_diffs) = r
        await process_tech_calc(result, hashed_json_input, prev_results, technology, key_list, cache, websocket, do_diffs)
        json_results.append(result)

  return json_results

async def perform_calculations_sync(tasks):
  json_results = []
  for task in tasks:
    json_result = await task
    json_results.append(json_result)
  return json_results

def build_result_paths(key_list):
  return [{
      'path': get_projection_path('technology', key_hash),
      'hash': key_hash,
      'technology': tech,
      'technology_full': tech_full,
      'diff_path':  get_projection_path('diffs', key_hash) if has_delta else None
    } for [tech, tech_full, key_hash, has_delta] in key_list]

def compound_key(workbook_id: int, workbook_version: int):
  return f'workbook-{workbook_id}-{workbook_version}'

async def get_prev_calc(workbook_id: int, workbook_version: int, cache) -> [int, Dict[Any, Any]]:
  keys = await cache.keys(f'workbook-{workbook_id}-*')
  if len(keys) > 0:
    versions = [int(re.search(r'(\d+)[^-]*$', key.decode("utf-8")).group(0)) for key in keys]
    versions.sort()
    prev_version = versions[-1]
    cache_key = compound_key(workbook_id, prev_version)
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
      return [prev_version, compound_key(workbook_id, prev_version), json.loads(cached_result)]
  return [None, None, {}]

def build_result(prev_key: str, prev_version: str, workbook_version: str, cache_key: str, variation, result_paths):
  return {
    'meta': {
      'previous_run_path': get_projection_path('calculation', prev_key) if prev_version else None,
      'version': workbook_version,
      'path': get_projection_path('calculation', cache_key),
      'variation_data': variation,
      'summary_path': get_projection_path('summary', cache_key)
    },
    'results': result_paths
  }

async def websocket_send_cached(str_cached_result: str, cached_result: dict, websocket: WebSocket, cache):
  # for technology in cached_result['results']:
  #  cached_tech = await cache.get(technology['hash'])
  #  await websocket.send_text(str(cached_tech))
  #  if technology['diff_path']:
  #    cached_diff = await cache.get(f'diff-{technology["hash"]}')
  #    await websocket.send_text(cached_diff)
  await websocket.send_text(str_cached_result)

async def calculate(
  workbook_id: int,
  workbook_version: Optional[int],
  variation_index: int,
  client,
  db,
  cache,
  run_async: bool,
  do_diffs: bool,
  websocket: WebSocket = None):

  workbook: Workbook = workbook_by_id(db, workbook_id)
  if not workbook:
    raise HTTPException(400, 'Workbook not found')
  regions = workbook.regions
  if workbook_version is None:
    workbook_version = workbook.version

  cache_key = compound_key(workbook_id, workbook_version)
  cached_result = await cache.get(cache_key)
  if cached_result is not None:
    if websocket:
      await websocket_send_cached(str(cached_result), json.loads(cached_result), websocket, cache)
      return
    return json.loads(cached_result)

  [prev_version, prev_key, prev_data] = await get_prev_calc(workbook_id, workbook_version, cache)

  # with cProfile.Profile() as pr:
  if workbook is None:
    raise HTTPException(status_code=400, detail="Workbook not found")
  result_paths = []
  variation = workbook.variations[variation_index]
  input_data = await fetch_data(variation, client)
  jsons = build_json(workbook.start_year, workbook.end_year, *input_data)
  [tasks, key_list, _] = await setup_calculations(jsons, regions, prev_data, cache, websocket, do_diffs)
  perform_func = perform_calculations_async if run_async else perform_calculations_sync
  await perform_func(tasks)
  result_paths += build_result_paths(key_list)
  result = build_result(prev_key, prev_version, workbook_version, cache_key, variation, result_paths)
  str_result = json.dumps(result)
  await cache.set(cache_key, str_result)
  if websocket:
    await websocket.send_text(str_result)

  workbook.has_run = True
  db.add(workbook)
  db.commit()
  # pr.print_stats()
  # pr.dump_stats('calc.prof')
  # s = io.StringIO()
  # ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
  # ps.print_stats()


  return result
