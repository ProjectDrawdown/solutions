from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from .helpers import get_user_from_header
from api.config import get_db
from api.routers.schemas import User
from api.db.models import User as DBUser
from api.queries.user_queries import get_user


async def get_current_user(
    user: User = Depends(get_user_from_header),
    db: Session = Depends(get_db)):
    db_user = get_user(db, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

async def get_current_active_user(current_user: DBUser = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_workbook(id: int, current_active_user: DBUser = Depends(get_current_active_user)):
    active_user_workbooks = list(filter(lambda w: w.id == id, current_active_user.workbooks))
    if len(active_user_workbooks) == 0:
        raise HTTPException(status_code=400, detail="Workbook not found")
    return active_user_workbooks[0]