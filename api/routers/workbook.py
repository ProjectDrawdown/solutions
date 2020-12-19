import importlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from api.config import get_settings, get_db
from api.queries.user_queries import get_user
from api.queries.workbook_queries import (
    workbook_by_id,
    workbooks_by_user_id,
    all_workbooks,
    clone_workbook,
    save_workbook
)

from db.models import User as DBUser, Workbook as DBWorkbook

from .schemas import Url, User, Token, AuthorizationResponse, Workbook
from .helpers import get_user_from_header
from .auth import get_current_active_user

from api.transform import transform

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

@router.patch("/workbook/{id}")
async def update_workbook(
    id: int,
    workbook_edits: Workbook,
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



