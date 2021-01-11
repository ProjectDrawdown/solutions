from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
import json
from jsonschema import validate
import enum
from api.config import get_resource_path
from uuid import uuid4

from .database import Base
from .json_schemas import workbook_schema

class UserRole(enum.Enum):
  default = 1

class User(Base):
  __tablename__ = "user"

  id = Column(Integer, primary_key=True, index=True)
  login = Column(String, unique=True, index=True)
  email = Column(String, unique=True, index=True)
  provider = Column(String)
  name = Column(String)
  company = Column(String)
  location = Column(String)
  picture = Column(String)
  is_active = Column(Boolean, default=True)
  role = Column(Enum(UserRole), default=UserRole.default)
  workbooks = relationship("Workbook", back_populates="author")

class Workbook(Base):
  __tablename__ = 'workbook'

  id = Column(Integer, primary_key=True, index=True)
  version = Column(Integer, default=0)
  name = Column(String)
  author_id = Column(Integer, ForeignKey('user.id'))
  author = relationship("User", back_populates="workbooks")
  ui = Column(JSONB)
  start_year = Column(Integer)
  end_year = Column(Integer)
  variations = Column(ARRAY(JSONB))

  @validates('data')
  def validate_data(self, key, value):
    my_json = json.loads(value)
    # Validate will raise exception if given json is not
    # what is described in schema.
    validate(instance=my_json, schema=workbook_schema)

class Resource(object):
  __tablename__ = 'resource'

  id = Column(Integer, primary_key=True)
  name = Column(String, index=True)
  data = Column(JSONB)

  @hybrid_property
  def path(self):
    return get_resource_path(self.__tablename__, self.id)

class Scenario(Resource, Base):
  __tablename__ = 'scenario'

class Reference(Resource, Base):
  __tablename__ = 'reference'

class Variation(Resource, Base):
  __tablename__ = 'variation'

class VMA(Resource, Base):
  __tablename__ = 'vma'
