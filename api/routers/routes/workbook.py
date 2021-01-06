import importlib
import pathlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import urllib
import uuid
import aioredis
import fastapi_plugins
from typing import List

from api.config import get_settings, get_db, AioWrap, get_resource_path
from api.queries.user_queries import get_user
from api.queries.workbook_queries import (
  workbook_by_id,
  workbooks_by_user_id,
  all_workbooks,
  clone_workbook,
  save_workbook,
  workbook_by_commit
)

from api.queries.resource_queries import get_entity_by_name

from api.db.models import (
  User as DBUser,
  Workbook as DBWorkbook,
  Variation as DBVariation,
  VMA as DBVMA
)

from api.routers import schemas
from api.routers.helpers import get_user_from_header
from api.routers.auth import get_current_active_user
from functools import lru_cache
from api.calculate import calculate

from model.advanced_controls import AdvancedControls, get_vma_for_param
from transforms.variable_paths import varProjectionNamesPaths
from transforms.reference_variable_paths import varRefNamesPaths

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
    start_year = workbook.start_year,
    end_year = workbook.end_year,
    variations = workbook.variations
  )

  saved_workbook = save_workbook(db, dbworkbook)
  return saved_workbook

@router.patch("/workbook/{id}", response_model=schemas.WorkbookOut)
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
  db_workbook.version = db_workbook.version + 1
  try:
    saved_db_workbook = save_workbook(db, db_workbook)
    return saved_db_workbook
  except:
    raise HTTPException(status_code=400, detail="Invalid Request")

# @router.get("/calculate/{workbook_commit_id}", response_model=List[schemas.Calculation])
# async def calculate(
#   workbook_commit_id: str,
#   client: AioWrap = Depends(AioWrap),
#   db: Session = Depends(get_db),
#   cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):

#   cached_result = await cache.get(workbook_commit_id)
#   if cached_result is not None:
#     return json.loads(cached_result)

#   workbook = workbook_by_commit(db, workbook_commit_id)
#   if workbook is None:
#     raise HTTPException(status_code=400, detail="Workbook not found")
#   for variation_path in workbook.variations:
#     input_data = await fetch_data(variation_path, client)
#     jsons = build_json(*input_data)
#     [tasks, key_list, json_cached_results] = await setup_calculations(jsons, cache)
#     [json_results, key_list] = await perform_calculations(tasks, cache, key_list)
#     result = json_results + json_cached_results
#     await cache.set(workbook_commit_id, json.dumps(result))
#     return result

@router.get("/calculate", response_model=List[schemas.CalculationPath])
async def get_calculate(
  workbook_id: int,
  workbook_version: int,
  client: AioWrap = Depends(AioWrap),
  db: Session = Depends(get_db),
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  return await calculate(workbook_id, workbook_version, client, db, cache)

@router.get("/resource/projection/{technology_hash}", response_model=schemas.Calculation)
async def get_tech_result(
  technology_hash: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  try:
    return json.loads(await cache.get(technology_hash))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")

@router.get("/vma/mappings/{technology}")
async def get_vma_mappings(technology: str, db: Session = Depends(get_db)):
  ac = AdvancedControls()
  paths = varProjectionNamesPaths + varRefNamesPaths
  importname = 'solution.' + technology
  m = importlib.import_module(importname)
  result = []
  for path in paths:
    vma_titles = get_vma_for_param(path[0])
    for title in vma_titles:
      vma_file = m.VMAs.get(title)
      if vma_file and vma_file.filename:
        db_file = get_entity_by_name(db, f'solution/{technology}/{vma_file.filename.name}', DBVMA)
        if db_file:
          result.append({
            'var': path[0],
            'vma_title': title,
            'vma_filename': vma_file.filename.name,
            'path': db_file.path,
            'file': db_file,
          })

  return result