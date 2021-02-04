from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.routers.helpers import get_user_from_header
from api.config import get_db
from api.queries.user_queries import get_user, all_users, save_user
from api.routers.auth import get_current_active_user
from api.routers import schemas
from api.db import models

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_profile(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return user

@router.patch("/me", response_model=schemas.User)
def patch_user(
    patch: schemas.UserPatch,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user.name = patch.name
    user.company = patch.company
    user.location = patch.location
    user.picture = patch.picture
    user.meta = patch.meta
    return save_user(db, user)

@router.get("/users", response_model=List[schemas.User])
def get_all(db: Session = Depends(get_db)):
    return all_users(db)
