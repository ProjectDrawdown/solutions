from sqlalchemy.orm import Session

from api.db.helpers import clone
from api.db.models import Workbook as DBWorkbook

def workbook_by_id(db: Session, id: int) -> DBWorkbook:
    return db.query(DBWorkbook).get(id)

def workbooks_by_user_id(db: Session, author_id: int) -> DBWorkbook:
    return db.query(DBWorkbook).filter(DBWorkbook.author_id==author_id).all()

def all_workbooks(db: Session):
    return db.query(DBWorkbook).all()

def clone_workbook(db: Session, id: int):
    cloned = clone(db, db.query(DBWorkbook).filter(DBWorkbook.id==id))
    return cloned

def save_workbook(db: Session, workbook: DBWorkbook):
    db.add(workbook)
    db.commit()
    db.refresh(workbook)
    return workbook