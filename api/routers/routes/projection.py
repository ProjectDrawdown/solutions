from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import fastapi_plugins
import aioredis
import json

from api.config import get_settings, get_db, AioWrap, get_resource_path
from api.routers import schemas
from api.db import models

from api.calculate import calculate_ref_emissions, calculate_emissions_reduction, sum_ref_emissions

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get("/projection/technology/{technology_hash}", response_model=schemas.Calculation,
        summary="Return the result of a calculation for the given technology hash"
        )
async def get_tech_result(
  technology_hash: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  try:
    return json.loads(await cache.get(technology_hash))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")

@router.get("/projection/diffs/{technology_hash}", response_model=schemas.CalculationDiffs,
        summary="Return the diff of a calculation for the given technology hash and the previous calculation."
        )
async def get_delta(
  technology_hash: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  try:
    return json.loads(await cache.get(f'diff-{technology_hash}'))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")

@router.get("/projection/calculation/{key}", response_model=schemas.CalculationResults,
        summary="Returns a previously run result of the `GET /calculate` endpoint."
        )
async def get_projection_run(
  key: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  try:
    return json.loads(await cache.get(key))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")

@router.get("/projection/summary/{key}",
        summary="Returns the co2_mmt_reduced for a previous run of the `GET /calculate` endpoint for all technologies."
        )
async def get_projection_summary(
  key: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):

  try:
    results = json.loads(await cache.get(key))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")

  summary = {}
  summary['sectors'] = {}
  conversion_factor = 0.001

  buildings_cities_tech = ['landfillmethane']
  land_use_tech = ['bamboo', 'forestprotection', 'peatlands', 'indigenouspeoplesland', 'perennialbioenergy', 'grasslandprotection', 'temperateforests', 'afforestation']
  electric_gen_tech = ['biogas', 'biomass', 'nuclear', 'microwind', 'geothermal', 'onshorewind', 'solarpvroof', 'solarpvutil', 'offshorewind', 'waveandtidal', 'instreamhydro', 'concentratedsolar', ]
  food_tech = ['biochar', 'improvedrice', 'silvopasture', 'managedgrazing', 'treeintercropping', 'nutrientmanagement', 'farmlandrestoration', 'riceintensification', 'tropicaltreestaples', 'conservationagriculture', 'multistrataagroforestry', 'regenerativeagriculture']

  for tech in results['results']:
    hash = tech['hash']
    tech_results = json.loads(await cache.get(hash))
    summary[tech['technology']] = {}

    if tech_results.get('data'):

      if tech_results['data']['c2'] and tech_results['data']['c2']['co2_mmt_reduced']:
        summary[tech['technology']]['co2_mmt_reduced'] = tech_results['data']['c2']['co2_mmt_reduced']
      if tech_results['data']['soln_ref_funits_adopted']:
        summary[tech['technology']]['soln_ref_funits_adopted'] = tech_results['data']['soln_ref_funits_adopted']
      if tech_results['data']['soln_pds_funits_adopted']:
        summary[tech['technology']]['soln_pds_funits_adopted'] = tech_results['data']['soln_pds_funits_adopted']

      if tech_results['data']['ref_tam_per_region'] and tech_results['data']['ef'] and tech_results['data']['soln_ref_funits_adopted']:
        summary[tech['technology']]['emissions_reduction'] = { 'World': [] }
        summary[tech['technology']]['emissions_reduction']['World'] = calculate_emissions_reduction(tech_results['data']['soln_ref_funits_adopted']['World'], tech_results['data']['soln_pds_funits_adopted']['World'], tech_results['data']['ef']['conv_ref_grid_CO2_per_KWh']['World'], conversion_factor)


      if tech['technology'] in buildings_cities_tech and 'Buildings and Cities' not in summary['sectors']:
        summary['sectors']['Buildings and Cities'] = {}
        summary['sectors']['Buildings and Cities']['reference_emissions'] = { 'World': [] }
        summary['sectors']['Buildings and Cities']['reference_emissions']['World'] = calculate_ref_emissions(tech_results['data']['ref_tam_per_region']['World'], tech_results['data']['ef']['conv_ref_grid_CO2_per_KWh']['World'], conversion_factor)

      if tech['technology'] in electric_gen_tech and 'Electricity Generation' not in summary['sectors']:
        summary['sectors']['Electricity Generation'] = {}
        summary['sectors']['Electricity Generation']['reference_emissions'] = { 'World': [] }
        summary['sectors']['Electricity Generation']['reference_emissions']['World'] = calculate_ref_emissions(tech_results['data']['ref_tam_per_region']['World'], tech_results['data']['ef']['conv_ref_grid_CO2_per_KWh']['World'], conversion_factor)

      if tech['technology'] in food_tech and 'Food' not in summary['sectors']:
        summary['sectors']['Food'] = {}
        summary['sectors']['Food']['reference_emissions'] = { 'World': [] }
        summary['sectors']['Food']['reference_emissions']['World'] = calculate_ref_emissions(tech_results['data']['ref_tam_per_region']['World'], tech_results['data']['ef']['conv_ref_grid_CO2_per_KWh']['World'], conversion_factor)

      if tech['technology'] in land_use_tech and 'Land Use' not in summary['sectors']:
        summary['sectors']['Land Use'] = {}
        summary['sectors']['Land Use']['reference_emissions'] = { 'World': [] }
        summary['sectors']['Land Use']['reference_emissions']['World'] = calculate_ref_emissions(tech_results['data']['ref_tam_per_region']['World'], tech_results['data']['ef']['conv_ref_grid_CO2_per_KWh']['World'], conversion_factor)


      if tech['technology'] in buildings_cities_tech:
        if 'emissions_reduction' not in summary['sectors']['Buildings and Cities']:
          summary['sectors']['Buildings and Cities']['emissions_reduction'] = { 'World': [] }
        summary['sectors']['Buildings and Cities']['emissions_reduction']['World'] = sum_ref_emissions(summary['sectors']['Buildings and Cities']['emissions_reduction']['World'], summary[tech['technology']]['emissions_reduction']['World'])

      if tech['technology'] in electric_gen_tech:
        if 'emissions_reduction' not in summary['sectors']['Electricity Generation']:
          summary['sectors']['Electricity Generation']['emissions_reduction'] = { 'World': [] }
        summary['sectors']['Electricity Generation']['emissions_reduction']['World'] = sum_ref_emissions(summary['sectors']['Electricity Generation']['emissions_reduction']['World'], summary[tech['technology']]['emissions_reduction']['World'])

      if tech['technology'] in food_tech:
        if 'emissions_reduction' not in summary['sectors']['Food']:
          summary['sectors']['Food']['emissions_reduction'] = { 'World': [] }
        summary['sectors']['Food']['emissions_reduction']['World'] = sum_ref_emissions(summary['sectors']['Food']['emissions_reduction']['World'], summary[tech['technology']]['emissions_reduction']['World'])

      if tech['technology'] in land_use_tech:
        if 'emissions_reduction' not in summary['sectors']['Land Use']:
          summary['sectors']['Land Use']['emissions_reduction'] = { 'World': [] }
        summary['sectors']['Land Use']['emissions_reduction']['World'] = sum_ref_emissions(summary['sectors']['Land Use']['emissions_reduction']['World'], summary[tech['technology']]['emissions_reduction']['World'])

  return summary

@router.get("/technology/meta_info/{technology}",
        summary="Returns the metadata for technology: ad_data_sources, tam_pds_data_sources, pds_ca_data_sources, ref_ca_data_sources."
        )
async def technology_meta_info(
  technology: str,
  db: Session = Depends(get_db),
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):

  workbook = db.query(models.Workbook).filter(models.Workbook.has_run==True).first()
  cache_key = f'workbook-{workbook.id}-{workbook.version}'

  cached_run = json.loads(await cache.get(cache_key))

  tech_result = next(filter(lambda r: r['technology']==technology, cached_run['results']))

  tech_json = json.loads(await cache.get(tech_result['hash']))

  return tech_json['metadata']

