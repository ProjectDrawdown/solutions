from enum import Enum
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import pathlib
import json
from api.config import get_settings, get_db, get_resource_path
import solution.factory
from api.db import models
from api.routers import schemas

from api.queries.resource_queries import (
  get_entity,
  get_entities_by_name,
  save_entity,
  all_entities,
  all_entity_paths,
  clone_variation,
  save_variation,
  delete_unused_variations,
  clear_all_tables
)
from api.queries.workbook_queries import (
  save_workbook
)
from api.transform import (
  transform,
  rehydrate_legacy_json,
  populate,
  convert_vmas_to_binary
)
from api.transforms.validate_variation import build_schema

settings = get_settings()
router = APIRouter()
DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')

entity_mapping = {
  'scenario': models.Scenario,
  'reference': models.Reference,
  'variation': models.Variation,
  'vma': models.VMA,
  'adoption_data': models.AdoptionData,
  'tam': models.TAM,
  'ca_pds': models.CustomAdoptionPDS,
  'ca_ref': models.CustomAdoptionRef
}

class EntityName(str, Enum):
    scenario = "scenario"
    reference = "reference"
    variation = "variation"
    vma = "vma"
    ad = "adoption_data"
    tam = "tam"
    ca_pds = "ca_pds"
    ca_ref = "ca_ref"


@router.get('/resource/vma/info/{technology}',
        summary="Get the VMA info for a given technology",
        description="VMA info exists when VMA sources cannot be viewed. Note that there may not be existing VMA info for every technology."
        )
async def get_vma_info(technology: str, db: Session = Depends(get_db)):
  return get_entities_by_name(db, f'solution/{technology}/VMA_info.csv', models.VMA)

@router.get('/resource/vma/all/{technology}',
        summary="Get all the VMA data for a given technology",
        description="Returns all VMA data for a technology"
        )
async def get_vma_all(technology: str, db: Session = Depends(get_db)):
  return get_entities_by_name(db, f'solution/{technology}/%.csv', models.VMA)

@router.get('/resource/{entity}/{id}', response_model=schemas.ResourceOut,
        summary="Get resource entity by id"
        )
async def get_by_id(entity: EntityName, id: int, db: Session = Depends(get_db)):
  return get_entity(db, id, entity_mapping[entity])

@router.get('/resource/{entity}', response_model=List[schemas.ResourceOut],
        summary="Get resource entity by name"
        )
async def get_by_name(entity: EntityName, name: str, db: Session = Depends(get_db)):
  return get_entities_by_name(db, name, entity_mapping[entity])

@router.get('/resource/{entity}s/full/', response_model=List[schemas.ResourceOut],
        summary="Get the full resource (all data) of an entity by name"
        )
async def get_all(entity: EntityName, db: Session = Depends(get_db)):
  return all_entities(db, entity_mapping[entity])

@router.get('/resource/{entity}s/paths/', response_model=List[str],
        summary="Get the resource paths (no data) of an entity by name"
        )
async def get_all_paths(entity: EntityName, db: Session = Depends(get_db)):
  return all_entity_paths(db, entity, entity_mapping[entity])

@router.post('/variation/fork/{id}', response_model=schemas.VariationOut,
        summary="Fork a variation with given id"
        )
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

@router.post('/variation/', response_model=schemas.VariationOut,
        summary="Create a new variation",
        description="Note: the variation is not automatically added to the workbook. Use `POST /workbook/{id}/variation` to add a variation to a workbook."
        )
async def post_variation(variation: schemas.VariationIn, db: Session = Depends(get_db)):
  new_variation = models.Variation(
    name = variation.name,
    data = {},
  )
  new_variation.data['scenario_parent_path'] = variation.scenario_parent_path
  new_variation.data['reference_parent_path'] = variation.reference_parent_path
  new_variation.data['scenario_vars'] = variation.scenario_vars
  new_variation.data['reference_vars'] = variation.reference_vars
  return save_variation(db, new_variation)

@router.get("/initialize/",
        summary="Initialize the database with data",
        description="Puts default scenario, reference, VMA, etd data into the database. Creates corresponding workbook for each scenario. In production, initialization is only allowed once."
        )
async def initialize(db: Session = Depends(get_db)):
  if db.query(models.VMA).count() > 0:
    if settings.is_production:
      raise HTTPException(status_code=400, detail="Database already initialized")
    else:
      clear_all_tables(db)

  [scenario_json, references_json] = transform()

  canonical_scenarios = ['drawdown-2020', 'plausible-2020', 'optimum-2020']
  for canonical_scenario in canonical_scenarios:
    scenario = save_entity(db, canonical_scenario, scenario_json, models.Scenario)
    reference = save_entity(db, canonical_scenario, references_json, models.Reference)
    variation = models.Variation(
      name = 'default',
      data = {
        "scenario_parent_path": scenario.path,
        "reference_parent_path": reference.path,
        "scenario_vars": {},
        "reference_vars": {},
      }
    )
    save_variation(db, variation)
    variation_dict = variation.__dict__['data']
    workbook = models.Workbook(
      name = canonical_scenario,
      ui = {},
      regions = ['World'],
      start_year = 2020,
      end_year = 2050,
      variations = [
        variation_dict
      ],
      vma_sources = {}
    )
    db_workbook = save_workbook(db, workbook)

  # populate resource tables:
  resource_models = [
    ('vma_data', models.VMA),
    ('tam', models.TAM),
    ('ad', models.AdoptionData),
    ('ca_pds_data', models.CustomAdoptionPDS),
    ('ca_ref_data', models.CustomAdoptionRef)
  ]
  for (directory, model) in resource_models:
    resources = populate(directory)
    for res in resources:
      name = f"{res['technology']}/{res['filename']}"
      save_entity(db, name, res['data'], model)

  vmas = convert_vmas_to_binary()
  for vma in vmas:
    vma_csv = models.VMA_CSV(
      name=vma['filename'],
      technology=vma['technology'],
      variable=vma['path'],
      legacy_variable=vma['legacy_variable'],
      original_filename=vma['filename'],
      data=vma['data']
    )
    db.add(vma_csv)
  db.commit()

@router.get("/technology/meta_info/{technology}",
        summary=""
        )
async def technology_meta_info(technology: str):
  paths = varProjectionNamesPaths + varRefNamesPaths
  importname = 'solution.' + technology
  m = importlib.import_module(importname)
  result = []
  for path in paths:
    vma_titles = get_vma_for_param(path[0])
    for title in vma_titles:
      vma_file = m.VMAs.get(title)
      if vma_file and vma_file.filename:
        db_file = get_entity_by_name(db, f'solution/{technology}/{vma_file.filename.name}', VMA)
        if db_file:
          result.append({
            'var': path[0],
            'vma_title': title,
            'vma_filename': vma_file.filename.name,
            'path': db_file.path,
            'file': db_file,
          })
  return result
