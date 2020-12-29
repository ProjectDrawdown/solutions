import asyncio
import importlib
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import urllib
import uuid
import aioredis
import fastapi_plugins
from pandas import DataFrame, Series

from api.config import get_settings, get_db, AioWrap
from api.queries.user_queries import get_user
from api.queries.workbook_queries import (
  workbook_by_id,
  workbooks_by_user_id,
  all_workbooks,
  clone_workbook,
  save_workbook,
  workbook_by_commit
)

from api.db.models import (
  User as DBUser,
  Workbook as DBWorkbook,
  Variation as DBVariation
)

from api.routers import schemas
from api.routers.helpers import get_user_from_header
from api.routers.auth import get_current_active_user

from api.transform import rehydrate_legacy_json

from model.data_handler import DataHandler

from solution import factory, factory_2

from functools import lru_cache

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get("/workbook/{id}")
async def get_workbook_by_id(id: int, db: Session = Depends(get_db)):
  return workbook_by_id(db, id)

@router.get("/workbooks/{user_id}")
async def get_all_workbooks_by_user(user_id: int, db: Session = Depends(get_db)):
  return workbooks_by_user_id(db, user_id)

@router.get("/workbooks/")
async def get_all_workbooks(db: Session = Depends(get_db)):
  return all_workbooks(db)

@router.post("/workbook/{id}")
async def fork_workbook(
    id: int,
    db_active_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)):

    cloned_workbook = clone_workbook(db, id)
    cloned_workbook.author_id = db_active_user.id
    saved_workbook = save_workbook(db, cloned_workbook)
    return saved_workbook.id

@router.post("/workbook/")
async def create_workbook(
  workbook: schemas.WorkbookNew,
  db_active_user: DBUser = Depends(get_current_active_user),
  db: Session = Depends(get_db)):

  dbworkbook = DBWorkbook(
    name = workbook.name,
    author_id = db_active_user.id,
    ui = workbook.ui,
    start_year = workbook.start_year,
    end_year = workbook.end_year,
    variations = workbook.variations
  )

  saved_workbook = save_workbook(db, dbworkbook)
  return saved_workbook.id

@router.patch("/workbook/{id}")
async def update_workbook(
  id: int,
  workbook_edits: schemas.WorkbookPatch,
  db_active_user: DBUser = Depends(get_current_active_user),
  db: Session = Depends(get_db)):

  active_user_workbooks = list(filter(lambda w: w.id == id, db_active_user.workbooks))
  if len(active_user_workbooks) == 0:
    raise HTTPException(status_code=400, detail="Workbook not found")

  db_workbook = active_user_workbooks[0]
  workbook_edits_dict = dict(workbook_edits)
  for key in workbook_edits_dict:
    value = workbook_edits_dict[key]
    if value is not None:
      db_workbook.__setattr__(key, value)
  try:
    saved_db_workbook = save_workbook(db, db_workbook)
    return saved_db_workbook
  except:
    raise HTTPException(status_code=400, detail="Invalid Request")

async def calc(constructor, input, hashed_json_input):
    return [to_json(constructor(input)), hashed_json_input]

@lru_cache()
@router.get("/calculate/{workbook_commit_id}")
async def calculate(
  workbook_commit_id: str, 
  client: AioWrap = Depends(AioWrap), 
  db: Session = Depends(get_db),
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):

  cached_result = await cache.get(workbook_commit_id)
  if cached_result is not None:
    return json.loads(cached_result)

  workbook = workbook_by_commit(db, workbook_commit_id)
  if workbook is None:
    raise HTTPException(status_code=400, detail="Workbook not found")
  for variation_path in workbook.variations:
    variation_data = await client(variation_path)
    scenario_parent_path = variation_data['data']['scenario_parent_path']
    reference_parent_path = variation_data['data']['reference_parent_path']
    scenario_data = await client(scenario_parent_path)
    reference_data = await client(reference_parent_path)
    jsons = list(map(lambda tech: {
        'tech': tech,
        'json': rehydrate_legacy_json(
          tech,
          scenario_data['data'],
          reference_data['data'],
          variation_data['data'])
        }
      , scenario_data['data']['technologies']))
    jsons = list(filter(lambda json: json['tech'] != 'fossilfuelelectricity', jsons))
    constructors = factory_2.all_solutions_scenarios(jsons)
    tasks = []
    json_cached_results = []
    for constructor in constructors:
        current_json_input: dict = list(filter(lambda json: json['tech'] == constructor, jsons))[0]
        name = current_json_input['json']['name']
        hashed_json_input = hashlib.md5(json.dumps(current_json_input).encode('utf-8')).hexdigest()
        
        cached_result = await cache.get(hashed_json_input)
        if cached_result is not None:
          json_cached_results.append(json.loads(cached_result))
        else:
          tasks.append(calc(constructors[constructor][0], name, hashed_json_input))

    json_results = []

    if len(tasks) > 0:
      calculated_results = await asyncio.wait(tasks)
      for r in calculated_results[0]:
        json_results.append(r._result[0])
        await cache.set(r._result[1], json.dumps(r._result[0]))

    result = json_results + json_cached_results
    await cache.set(workbook_commit_id, json.dumps(result))
    return result


def to_json(scenario):
    json_data = dict()
    json_data['name'] = scenario.name
    instance_vars = vars(scenario).keys()
    for iv in instance_vars:
        try:
            obj = getattr(scenario, iv)
            if issubclass(type(obj), DataHandler):
                json_data[iv] = obj.to_json()
                for jv in json_data[iv]:
                  if type(json_data[iv][jv]) in [DataFrame, Series]:
                    json_data[iv][jv] = json.loads(json_data[iv][jv].to_json())
        except BaseException as e:
            json_data[iv] = None
    return json_data
