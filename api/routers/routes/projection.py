from fastapi import APIRouter, Depends, HTTPException
import fastapi_plugins
import aioredis
import json

from api.config import get_settings, get_db, AioWrap, get_resource_path
from api.routers import schemas

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get("/projection/technology/{technology_hash}", response_model=schemas.Calculation)
async def get_tech_result(
  technology_hash: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  try:
    return json.loads(await cache.get(technology_hash))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")

@router.get("/projection/diffs/{technology_hash}", response_model=schemas.CalculationDiffs)
async def get_delta(
  technology_hash: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  try:
    return json.loads(await cache.get(f'diff-{technology_hash}'))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")

@router.get("/projection/calculation/{key}", response_model=schemas.CalculationResults)
async def get_projection_run(
  key: str,
  cache: aioredis.Redis=Depends(fastapi_plugins.depends_redis)):
  try:
    return json.loads(await cache.get(key))
  except:
    raise HTTPException(status_code=400, detail=f"Cached results not found: GET /calculate/... to fill cache and get new projection url paths")
