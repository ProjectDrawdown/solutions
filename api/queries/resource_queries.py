import json

from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from api.db import models
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

def get_entities_by_name(db: Session, name: str, table):
    return db.query(table).filter(table.name.like(name)).all()

def get_entity_by_name(db: Session, name: str, table):
    return db.query(table).filter(table.name.like(name)).first()

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
    # would be nice to do in the db but this doesn't work because path is a hybrid property
    # unused_vars = db.query(Variation).join(Workbook, Workbook.variations.contains([Variation.path])).all()

    all_workbooks = db.query(Workbook).all()
    all_variations = db.query(Variation).all()
    for variation in all_variations:
        found = False
        for workbook in all_workbooks:
            if variation.path in workbook.variations:
                found = True
        if not found:
            db.delete(variation)
    db.commit()

def clear_all_tables(db: Session):
    for model in [
        models.VMA,
        models.TAM,
        models.AdoptionData,
        models.CustomAdoptionPDS,
        models.CustomAdoptionRef,
        models.Scenario,
        models.Reference,
        models.Variation,
        models.Workbook,
        models.VMA_CSV
        ]:
            db.query(model).delete()
    db.commit()
