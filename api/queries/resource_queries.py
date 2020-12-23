import json

from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from api.db.models import Scenario, Reference, Variation, Workbook
from api.db.helpers import clone
from api.routers import schemas

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d

def get_entity(db: Session, id: int, table):
    return db.query(table).filter(table.id == id).first()

def all_entities(db: Session, table):
    return db.query(table).all()

def all_entity_paths(db: Session, entity, table):
    return list(map(lambda r: r.path, db.query(table).all()))

def clone_variation(db: Session, id: int):
    cloned = clone(db, db.query(Variation).filter(Variation.id==id))
    return cloned

def save_variation(db: Session, variation: Variation):
    db.add(variation)
    db.commit()
    db.refresh(variation)
    return variation

def save_entity(db: Session, name: str, obj, table):
    db_obj = table(
        name = name,
        data = obj)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_unused_variations(db: Session):
    unused_vars = db.query(Variation).join(Workbook, Variation.path not in Workbook.variations).all()
    return unused_vars