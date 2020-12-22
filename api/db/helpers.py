from sqlalchemy.orm import Session
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import make_transient

def clone(db: Session, query: Query):
  source_obj = query.all()[0]

  db.expunge(source_obj)  # expunge the object from session
  make_transient(source_obj)  # http://docs.sqlalchemy.org/en/rel_1_1/orm/session_api.html#sqlalchemy.orm.session.make_transient
  delattr(source_obj, 'id')
  return source_obj

