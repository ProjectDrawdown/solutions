from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from model.data_handler import DataHandler
import pathlib
import json
from config import get_settings, get_db
import solution.factory
from api.db.models import (
  Scenario,
  Control,
  Workbook
)
from api.queries.scenario_queries import (
  get_entity,
  save_entity, 
  all_entities,
  all_entity_ids,
)
from api.queries.workbook_queries import (
  save_workbook
)
from api.transform import transform, rehydrate_legacy_json

settings = get_settings()
router = APIRouter()
DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')


@router.get('/projections/{name}')
def get_projection(name: str, scenario: Optional[str] = None):
    sol = solution.factory.one_solution_scenarios(name)
    if sol:
        constructor = sol[0]
        obj = constructor(scenario=scenario)
        return {name: to_json(obj)}
    else:
        return {}


def to_json(scenario):
    json_data = dict()
    instance_vars = vars(scenario).keys()
    for iv in instance_vars:
        try:
            obj = getattr(scenario, iv)
            if issubclass(type(obj), DataHandler):
                json_data[iv] = obj.to_json()
        except BaseException as e:
            json_data[iv] = None
    return {scenario.scenario: json_data}

# @router.get('/solutions/{name}')
# def calculate(name: str, db: Session = Depends(get_db)):
    # directory = DATADIR
    # for filename in glob.glob(str(directory.joinpath('*.json'))):
    #     with open(filename, 'r') as fid:
    #         j = json.loads(fid.read())
    #         js = j.copy()

@router.get('/scenario/{name}')
def get_scenerio_by_name(name: str, db: Session = Depends(get_db)):
  scenario = get_entity(db, name, Scenario)
  return scenario

@router.get('/control/{name}')
def get_control_by_name(name: str, db: Session = Depends(get_db)):
  control = get_entity(db, name, Control)
  return control

@router.get('/scenarios/full/')
def get_all_scenarios(db: Session = Depends(get_db)):
  return all_entities(db, Scenario)

@router.get('/controls/full/')
def get_all_controls(db: Session = Depends(get_db)):
  return all_entities(db, Control)

@router.get('/scenarios/ids/')
def get_all_scenario_ids(db: Session = Depends(get_db)):
  return all_entity_ids(db, Scenario)

@router.get('/controls/ids/')
def get_all_control_ids(db: Session = Depends(get_db)):
  return all_entity_ids(db, Control)

@router.get("/initialize/")
async def initialize(db: Session = Depends(get_db)):
  [scenario_json, controls_json] = transform()

  canonical_scenario = 'drawdown-2020'

  scenario = save_entity(db, canonical_scenario, scenario_json, Scenario)
  control = save_entity(db, canonical_scenario, controls_json, Control)

  start_year = scenario_json['report_start_year']
  end_year = scenario_json['report_end_year']

  workbook = Workbook(
    name = canonical_scenario,
    author_id = None,
    ui = {},
    start_year = start_year,
    end_year = end_year,
    control = control,
    scenario = scenario,
    variation = {},
  )

  saved_workbook = save_workbook(db, workbook)

  return rehydrate_legacy_json(scenario_json, controls_json)
