from enum import Enum
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import pathlib
import json
from api.config import get_settings, get_db, get_resource_path
import solution.factory
from api.db.models import (
  Scenario as DBScenario,
  Reference as DBReference,
  Workbook as DBWorkbook,
  Variation as DBVariation,
  VMA as DBVMA
)
from api.routers import schemas

from api.queries.resource_queries import (
  get_entity,
  get_entities_by_name,
  save_entity, 
  all_entities,
  all_entity_paths,
  clone_variation,
  save_variation,
  delete_unused_variations
)
from api.queries.workbook_queries import (
  save_workbook
)
from api.transform import transform, rehydrate_legacy_json, populate_vmas
from api.transforms.validate_variation import build_schema

settings = get_settings()
router = APIRouter()
DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')

entity_mapping = {
  'scenario': DBScenario,
  'reference': DBReference,
  'variation': DBVariation,
  'vma': DBVMA,
}

class EntityName(str, Enum):
    scenario = "scenario"
    reference = "reference"
    variation = "variation"
    vma = "vma"

@router.get('/resource/vma/info/{technology}')
async def get_vma_info(technology: str, db: Session = Depends(get_db)):
  return get_entities_by_name(db, f'solution/{technology}/VMA_info.csv', DBVMA)

@router.get('/resource/vma/all/{technology}')
async def get_vma_all(technology: str, db: Session = Depends(get_db)):
  return get_entities_by_name(db, f'solution/{technology}/%.csv', DBVMA)

@router.get('/resource/{entity}/{id}', response_model=schemas.ResourceOut)
async def get_by_id(entity: EntityName, id: int, db: Session = Depends(get_db)):
  return get_entity(db, id, entity_mapping[entity])

@router.get('/resource/{entity}', response_model=List[schemas.ResourceOut])
async def get_by_name(entity: EntityName, name: str, db: Session = Depends(get_db)):
  return get_entities_by_name(db, name, entity_mapping[entity])

@router.get('/resource/{entity}s/full/', response_model=List[schemas.ResourceOut])
async def get_all(entity: EntityName, db: Session = Depends(get_db)):
  return all_entities(db, entity_mapping[entity])

@router.get('/resource/{entity}s/paths/', response_model=List[str])
async def get_all_paths(entity: EntityName, db: Session = Depends(get_db)):
  return all_entity_paths(db, entity, entity_mapping[entity])

@router.post('/variation/fork/{id}', response_model=schemas.VariationOut)
async def fork_variation(id: int, patch: schemas.VariationPatch, db: Session = Depends(get_db)):
  try:
    cloned_variation = clone_variation(db, id)
  except:
    raise HTTPException(status_code=400, detail="Variation not found")

  if patch.scenario_parent_path is not None:
    cloned_variation.data['scenario_parent_path'] = patch.scenario_parent_path
  if patch.scenario_parent_path is not None:
    cloned_variation.data['reference_parent_path'] = patch.reference_parent_path
  if patch.scenario_vars is not None:  
    cloned_variation.data['scenario_vars'] = patch.scenario_vars
  if patch.reference_vars is not None:
    cloned_variation.data['reference_vars'] = patch.reference_vars

  return save_variation(db, cloned_variation)

@router.post('/variation/', response_model=schemas.VariationOut)
async def post_variation(variation: schemas.VariationIn, db: Session = Depends(get_db)):
  new_variation = DBVariation(
    name = variation.name,
    data = {},
  )
  new_variation.data['scenario_parent_path'] = variation.scenario_parent_path
  new_variation.data['reference_parent_path'] = variation.reference_parent_path
  new_variation.data['scenario_vars'] = variation.scenario_vars
  new_variation.data['reference_vars'] = variation.reference_vars
  return save_variation(db, new_variation)

@router.get("/initialize/")
async def initialize(db: Session = Depends(get_db)):
  [scenario_json, references_json] = transform()

  canonical_scenario = 'drawdown-2020'

  scenario = save_entity(db, canonical_scenario, scenario_json, DBScenario)
  reference = save_entity(db, canonical_scenario, references_json, DBReference)

  variation = DBVariation(
    name = 'default',
    data = {
      "scenario_parent_path": scenario.path,
      "reference_parent_path": reference.path,
      "scenario_vars": {},
      "reference_vars": {},
    }
  )
  db_variation = save_variation(db, variation)

  variation_dict = variation.__dict__['data']

  workbook = DBWorkbook(
    name = 'default',
    ui = {},
    start_year = 2020,
    end_year = 2050,
    variations = [
      variation_dict
    ]
  )

  db_workbook = save_workbook(db, workbook)

  vmas = populate_vmas()
  for vma in vmas:
    name = f"{vma['technology']}/{vma['filename']}"
    save_entity(db, name, vma['data'], DBVMA)

  return db_workbook
  # return rehydrate_legacy_json(scenario_json, references_json)

@router.get('/vma/aggregates/{technology}')
async def get_vma_agg(variable_path: str, db: Session = Depends(get_db)):
  # if there's a vma_info object just use that
  pass

@router.get("/garbage_collect")
async def garbage_collect(db: Session = Depends(get_db)):
  delete_unused_variations(db)