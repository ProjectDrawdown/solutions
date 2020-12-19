from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship, validates
import json
from jsonschema import validate
import enum

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
    name = Column(String)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship("User", back_populates="workbooks")
    ui = Column(JSONB)
    start_year = Column(Integer)
    end_year = Column(Integer)
    control_id = Column(Integer, ForeignKey('control.id'))
    control = relationship("Control")
    scenario_id = Column(Integer, ForeignKey('scenario.id'))
    scenario = relationship("Scenario")

    variation = Column(JSONB)

    @validates('data')
    def validate_data(self, key, value):
        my_json = json.loads(value)
        # Validate will raise exception if given json is not
        # what is described in schema.
        validate(instance=my_json, schema=workbook_schema)

class Scenario(Base):
    __tablename__ = 'scenario'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    json = Column(JSONB)

class Control(Base):
    __tablename__ = 'control'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    json = Column(JSONB)

# class Technology(Base):
#     __tablename__ = 'technology'

#     id = Column(Integer, primary_key=True)
#     schema = Column(JSONB)

# class ProjectionSchema(Base):
#     __tablename__ = 'projection_schema'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     schema = Column(JSONB)
