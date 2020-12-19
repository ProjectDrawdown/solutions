from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import User
from .helpers import get_user_from_header
from api.config import get_db
from api.queries.user_queries import get_user

router = APIRouter()

@router.get("/me", response_model=User)
def read_profile(
    user: User = Depends(get_user_from_header),
    db: Session = Depends(get_db)
):
    db_user = get_user(db, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
