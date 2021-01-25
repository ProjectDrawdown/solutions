import importlib
import pathlib
from fastapi import APIRouter, Depends, HTTPException, WebSocket, FastAPI
from sqlalchemy.orm import Session
import json
import urllib
import uuid
import aioredis
import fastapi_plugins
from typing import List, Optional, Any

from api.config import get_settings, get_db, AioWrap, get_resource_path, get_app
from api.queries.user_queries import get_user
from api.queries.workbook_queries import (
  workbook_by_id,
  workbooks_by_user_id,
  all_workbooks,
  clone_workbook,
  save_workbook,
  workbook_by_commit
)

from api.queries.resource_queries import (
  get_entity_by_name,
  save_variation
)

from api.db.models import (
  User as DBUser,
  Workbook as DBWorkbook,
  Variation as DBVariation,
  VMA as DBVMA
)

from api.routers import schemas
from api.routers.helpers import get_user_from_header
from api.routers.auth import get_current_active_user, get_current_workbook
from functools import lru_cache
from api.calculate import calculate

from model.advanced_controls import AdvancedControls, get_vma_for_param
from api.transforms.variable_paths import varProjectionNamesPaths
from api.transforms.reference_variable_paths import varRefNamesPaths
from api.transforms.validate_variation import validate_full_schema

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get("/workbook/{id}", response_model=schemas.WorkbookOut)
async def get_workbook_by_id(id: int, db: Session = Depends(get_db)):
  workbook = workbook_by_id(db, id)
  if not workbook:
    raise HTTPException(status_code=400, detail="Workbook not found")
  return workbook

@router.get("/workbooks/{user_id}", response_model=List[schemas.WorkbookOut])
async def get_all_workbooks_by_user(user_id: int, db: Session = Depends(get_db)):
  return workbooks_by_user_id(db, user_id)

@router.get("/workbooks/", response_model=List[schemas.WorkbookOut])
async def get_all_workbooks(db: Session = Depends(get_db)):
  return all_workbooks(db)

@router.post("/workbook/{id}", response_model=schemas.WorkbookOut)
async def fork_workbook(
    id: int,
    db_active_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)):
  try:
    cloned_workbook = clone_workbook(db, id)
  except:
    raise HTTPException(status_code=400, detail="Workbook not found")
  cloned_workbook.author_id = db_active_user.id
  saved_workbook = save_workbook(db, cloned_workbook)
  return saved_workbook

@router.post("/workbook/", response_model=schemas.WorkbookOut)
async def create_workbook(
  workbook: schemas.WorkbookNew,
  db_active_user: DBUser = Depends(get_current_active_user),
  db: Session = Depends(get_db)):

  dbworkbook = DBWorkbook(
    name = workbook.name,
    author_id = db_active_user.id,
    ui = workbook.ui,
    regions = workbook.regions,
    start_year = workbook.start_year,
    end_year = workbook.end_year,
    variations = []
  )

  saved_workbook = save_workbook(db, dbworkbook)
  return saved_workbook

@router.patch("/workbook/{id}", response_model=schemas.WorkbookOut)
async def update_workbook(
  id: int,
  workbook_edits: schemas.WorkbookPatch,
  db_workbook: DBWorkbook = Depends(get_current_workbook),
  db: Session = Depends(get_db),
  client: AioWrap = Depends(AioWrap)):

  workbook_edits_dict = dict(workbook_edits)
  for key in workbook_edits_dict:
    value = workbook_edits_dict[key]
    if value is not None:
      db_workbook.__setattr__(key, value)

  db_workbook.version = db_workbook.version + 1
  saved_db_workbook = save_workbook(db, db_workbook)
  return saved_db_workbook

def replace(arr: List[Any], index: int, item: Any):
  return arr[:index] + [item] + arr[index+1:]

@router.patch("/workbook/{id}/variation/{variation_index}", response_model=schemas.WorkbookOut)
async def update_workbook_variation(
  id: int,
  variation_index: int,
  variation_patch: schemas.VariationIn,
  db_workbook: DBWorkbook = Depends(get_current_workbook),
  db: Session = Depends(get_db),
  client: AioWrap = Depends(AioWrap)):

  validation = await validate_full_schema(variation_patch, client)
  if not validation['valid']:
    raise HTTPException(status_code=422, detail=validation['reason'])
  warnings = validation.get('warnings')

  db_workbook.variations = replace(db_workbook.variations, variation_index, variation_patch.__dict__)
  db_workbook.version = db_workbook.version + 1
  saved_db_workbook = save_workbook(db, db_workbook)
  response = schemas.WorkbookOut.from_orm(saved_db_workbook)
  response.warnings = warnings
  return response

@router.post("/workbook/{id}/variation", response_model=schemas.WorkbookOut)
async def add_workbook_variation(
  id: int,
  variation_path: Optional[str] = None,
  variation_patch: Optional[schemas.VariationIn] = None,
  db_workbook: DBWorkbook = Depends(get_current_workbook),
  db: Session = Depends(get_db),
  client: AioWrap = Depends(AioWrap)):

  if variation_patch:
    variation = {
      'scenario_vars': variation_patch.scenario_vars,
      'reference_vars': variation_patch.reference_vars,
      'scenario_parent_path': variation_patch.scenario_parent_path,
      'reference_parent_path': variation_patch.reference_parent_path
    }
  if variation_path:
    variation = (await client(variation_path))['data']
    variation.pop('name')

  validation = await validate_full_schema(variation, client)
  if not validation['valid']:
    raise HTTPException(status_code=422, detail=validation['reason'])
  warnings = validation.get('warnings')

  db_workbook.variations = db_workbook.variations + [variation]
  db_workbook.version = db_workbook.version + 1
  saved_db_workbook = save_workbook(db, db_workbook)
  response = schemas.WorkbookOut.from_orm(saved_db_workbook)
  response.warnings = warnings
  return response

def without(arr: List[Any], index: int):
  return arr[:index] + arr[index+1:]

@router.delete("/workbook/{id}/variation/{variation_index}", response_model=schemas.WorkbookOut)
async def delete_workbook_variation(
  id: int,
  variation_index: int,
  db_workbook: DBWorkbook = Depends(get_current_workbook),
  db: Session = Depends(get_db)):

  db_workbook.variations = without(db_workbook.variations, variation_index)
  db_workbook.version = db_workbook.version + 1
  saved_db_workbook = save_workbook(db, db_workbook)
  return saved_db_workbook

@router.post("/workbook/{id}/variation/{variation_index}", response_model=schemas.VariationOut)
async def publish_variation(
  id: int,
  variation_index: int,
  info: schemas.PublishVariation,
  db_workbook: DBWorkbook = Depends(get_current_workbook),
  db: Session = Depends(get_db)):

  variation = db_workbook.variations[variation_index]
  new_variation = DBVariation(
    name = info.name,
    data = variation,
  )
  # new_variation.data['scenario_parent_path'] = variation.scenario_parent_path
  # new_variation.data['reference_parent_path'] = variation.reference_parent_path
  # new_variation.data['scenario_vars'] = variation.scenario_vars
  # new_variation.data['reference_vars'] = variation.reference_vars
  return save_variation(db, new_variation)

@router.get("/calculate", response_model=schemas.CalculationResults)
async def get_calculate(
  workbook_id: int,
  variation_index: int,
  do_diffs: Optional[bool] = False,
  run_async: Optional[bool] = True,
  workbook_version: Optional[int] = None,
  client: AioWrap = Depends(AioWrap),
  db: Session = Depends(get_db),
  cache: aioredis.Redis = Depends(fastapi_plugins.depends_redis)):
  return await calculate(workbook_id, workbook_version, variation_index, client, db, cache, run_async, do_diffs)

@router.websocket("/calculate/ws")
async def get_calculat_ws(
  workbook_id: int,
  variation_index: int,
  websocket: WebSocket,
  do_diffs: Optional[bool] = False,
  run_async: Optional[bool] = True,
  workbook_version: Optional[int] = None,
  client: AioWrap = Depends(AioWrap),
  db: Session = Depends(get_db)):
  app = get_app()
  cache = app.state.REDIS.redis
  await websocket.accept()
  await calculate(workbook_id, workbook_version, variation_index, client, db, cache, run_async, do_diffs, websocket)

