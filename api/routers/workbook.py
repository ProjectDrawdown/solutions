import importlib
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from api.config import get_settings, get_db
from api.queries import get_user

from db.models import User as DBUser, Workbook as DBWorkbook

from .schemas import Url, User, Token, AuthorizationResponse, Workbook
from .helpers import get_user_from_header
from .auth import get_current_active_user

from api.transform import transform

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get("/workbooks/")
async def get_workbooks(db_active_user: DBUser = Depends(get_current_active_user)):
    return db_active_user.workbooks

@router.post("/workbooks/{id}")
async def add_workbook(name: str, workbook: Workbook, db_active_user: DBUser = Depends(get_current_active_user)):
    validated_workbook = workbook.dict()
    validated_workbook['author'] = db_active_user.login
    json_workbook = json.dumps(validated_workbook)

    db_active_user.workbooks.append(DBWorkbook(data=json_workbook))
    session.query(DBWorkbook).filter(DBWorkbook.data=='child2')
    return db_active_user.workbooks

@router.get("/transform/")
async def get_transform():
    return transform()