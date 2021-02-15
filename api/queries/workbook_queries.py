from sqlalchemy.orm import Session

from api.db.helpers import clone
from api.db.models import Workbook as DBWorkbook

def workbook_by_id(db: Session, id: int) -> DBWorkbook:
    return db.query(DBWorkbook).get(id)

def workbook_by_commit(db: Session, uuid: str) -> DBWorkbook:
    return db.query(DBWorkbook).filter(DBWorkbook.commit==uuid).first()

def workbooks_by_user_id(db: Session, author_id: int) -> DBWorkbook:
    return db.query(DBWorkbook).filter(DBWorkbook.author_id==author_id).all()

def workbooks_by_default_user(db: Session) -> DBWorkbook:
    return db.query(DBWorkbook).filter(DBWorkbook.author_id.is_(None)).all()

def all_workbooks(db: Session, id: int):
    q1 = db.query(DBWorkbook).filter(DBWorkbook.author_id==id)
    q2 = db.query(DBWorkbook).filter(DBWorkbook.author_id.is_(None))
    q3 = q1.union(q2)
    return q3.all()

def clone_workbook(db: Session, id: int):
    cloned = clone(db, db.query(DBWorkbook).filter(DBWorkbook.id==id))
    return cloned

def save_workbook(db: Session, workbook: DBWorkbook):
    db.add(workbook)
    db.commit()
    db.refresh(workbook)
    return workbook
