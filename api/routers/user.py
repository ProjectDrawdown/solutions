from fastapi import APIRouter, Depends, HTTPException
from .schemas import User
from .helpers import get_user_from_header

router = APIRouter()

@router.get("/me", response_model=User)
def read_profile(
    user: User = Depends(get_user_from_header)
):
    db_user = user
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
