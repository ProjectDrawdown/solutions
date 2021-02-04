from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from api.db import models
from api.routers import schemas

def get_user(db: Session, user: models.User):
    return db.query(models.User).filter(models.User.login == user.login).first()

def create_user(db: Session, user: models.User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def all_users(db: Session):
    return db.query(models.User).all()

def save_user(db: Session, user: models.User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
