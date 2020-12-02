from fastapi import APIRouter, Depends, HTTPException
#from sqlalchemy.orm import Session

#from app.database import get_db

#from .crud import get_user
from .schemas import User
#from .models import User as DbUser
from .helpers import get_user_from_header

router = APIRouter()

@router.get("/me", response_model=User)
def read_profile(
    user: User = Depends(get_user_from_header)
    #db: Session = Depends(get_db),
):
    #db_user = get_user(db, user.id)
    db_user = {}
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    #return db_user
