import json

from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from db.models import Scenario, Control
from routers import schemas

def get_entity(db: Session, name: str, table):
    return db.query(table).filter(table.name == name).first()

def all_entities(db: Session, table):
    return db.query(table).all()

def all_entity_ids(db: Session, table):
    return list(map(lambda r: r[0], db.query(table.id).all()))

def save_entity(db: Session, name: str, scenario, table):
    db_scenario = table(
        name = name,
        json = scenario)

    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario
