from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import fastapi_plugins
import aioredis
import json
import importlib

from api.config import get_settings, get_db, AioWrap, get_resource_path
from api.transforms.variable_paths import varProjectionNamesPaths
from api.transforms.reference_variable_paths import varRefNamesPaths
from model.advanced_controls import AdvancedControls, get_vma_for_param

from api.queries.resource_queries import get_entity_by_name
from api.db.models import VMA

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get("/vma/mappings/{technology}")
async def get_vma_mappings(technology: str, db: Session = Depends(get_db)):
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


@router.get("/vma/aggregate/{technology}")
async def get_vma_agg(technology: str, db: Session = Depends(get_db)):
  # if vma_info exists extract data from that
  vma_info = db.query(VMA).filter(VMA.name==f'solution/{technology}/VMA_info.csv').first()
  if vma_info and len(vma_info.data['rows']) > 0:
    return vma_info
  else:
    mappings = await get_vma_mappings(technology, db)
    info = []
    for mapping in mappings:
      file = mapping['file']
      var = mapping['var']
      min = None
      max = None
      sum = 0
      count = len(file.data['rows'])
      for row in file.data['rows']:
        value = float(row['Raw Data Input'])
        sum = sum + value
        if not min or min > value:
          min = value
        if not max or max < value:
          max = value
      avg = sum / count
      info.append({
        "Fixed Low": str(min),
        "Fixed High": str(max),
        "Fixed Mean": str(avg),
        "Title on xls": mapping['vma_title']
      })
    return info
      
