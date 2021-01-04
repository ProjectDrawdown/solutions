from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from api.db import models
from api.config import get_resource_path

class AuthorizationResponse(BaseModel):
  state: str
  code: str

class GithubUser(BaseModel):
  login: str
  name: str = None
  company: str = None
  location: str = None
  email: str = None
  avatar_url: str

class GoogleUser(BaseModel):
  login: str
  name: str
  company: str = None
  location: str = None
  email: str
  picture: str

class User(BaseModel):
  id: Optional[int]
  login: str
  name: Optional[str]
  company: str = None
  location: str = None
  email: str
  picture: str = None
  class Config:
    orm_mode = True

class UserPatch(BaseModel):
  name: Optional[str]
  company: str = None
  location: str = None
  picture: str = None
  class Config:
    orm_mode = True

class Token(BaseModel):
  access_token: str
  token_type: str
  user: User

class Url(BaseModel):
  url: str

class WorkbookNew(BaseModel):
  name: str
  ui: dict
  start_year: int
  end_year: int
  variations: List[str]
  class Config:
    orm_mode = True
    schema_extra = {
      "example": {
        "name": "default",
        "author": {
          "login": "user@example.coop",
          "email": "user@example.coop",
        },
        "ui": {
          "portfolioSolutions": [
            'solarpvutil',
          ],
          "openPanel": "panelId", 
          "quickVariables": [
            'technologies.biogas.fixed_oper_cost_per_iunit',
          ],
        },
        "start_year": 2020,
        "end_year": 2050,
        "variations": [
          get_resource_path('variation', 0)
        ]
      }
    }

class WorkbookPatch(BaseModel):
  name: Optional[str]
  ui: Optional[dict]
  start_year: Optional[int]
  end_year: Optional[int]
  variations: Optional[List[str]]
  class Config:
    orm_mode = True
    schema_extra = {
      "example": {
        "name": "default",
        "ui": {
          "portfolioSolutions": [
            'solarpvutil',
          ],
          "openPanel": "panelId", 
          "quickVariables": [
            'technologies.biogas.fixed_oper_cost_per_iunit',
          ],
        },
        "variations": [
          get_resource_path('variation', 0)
        ]
      }
    }

class WorkbookOut(BaseModel):
  id: int
  author: Optional[User]
  commit: UUID
  name: str
  ui: dict
  start_year: int
  end_year: int
  variations: List[str]
  class Config:
    orm_mode = True
    schema_extra = {
      "example": {
        "id": 1,
        "commit": "2f78ebbb-9b6b-468a-b1cf-6d615d90b3ce",
        "name": "default",
        "ui": {
          "portfolioSolutions": [
            'solarpvutil',
          ],
          "openPanel": "panelId", 
          "quickVariables": [
            'technologies.biogas.fixed_oper_cost_per_iunit',
          ],
        },
        "start_year": 2020,
        "end_year": 2050,
        "variations": [
          get_resource_path('variation', 0)
        ]
      }
    }

class ResourceOut(BaseModel):
  id: Optional[int]
  name: Optional[str]
  data: Dict[Any, Any]
  path: Optional[str]
  class Config:
    orm_mode = True

class VariationOut(ResourceOut):
  class Config:
    schema_extra = {
      "example": {
        "id": 21,
        "name": 'example',
        "data": {
          "scenario_vars": {
            "technologies.biogas.fixed_oper_cost_per_iunit": {
              "value": 10,
              "statistic": ""
            }
          },
          "reference_vars": {
            "technologies.biogas.fixed_oper_cost_per_iunit": {
              "value": 0,
              "statistic": "mean"
            }
          },
          "scenario_parent_path": get_resource_path('scenario', 0),
          "reference_parent_path": get_resource_path('reference', 0)
        },
        "path": get_resource_path('variation', 0)
      }
    }

class ResourceIn(BaseModel):
  name: Optional[str]

class VariationIn(ResourceIn):
  scenario_parent_path: str
  reference_parent_path: str
  scenario_vars: Dict[str, Any]
  reference_vars: Dict[str, Any]
  class Config:
    schema_extra = {
        "example": {
            "scenario_parent_path": get_resource_path('scenario', 0),
            "reference_parent_path": get_resource_path('reference', 0),
            "scenario_vars": {
              "technologies.biogas.fixed_oper_cost_per_iunit": {
                  "value": 10.0,
                  "statistic": ""
              }
            },
            "reference_vars": {
              "technologies.biogas.fixed_oper_cost_per_iunit": {
                  "value": 0.0,
                  "statistic": "mean"
              }
            },
        }
    }

class VariationPatch(ResourceIn):
  scenario_parent_path: Optional[str]
  reference_parent_path: Optional[str]
  scenario_vars: Optional[Dict[str, Any]]
  reference_vars: Optional[Dict[str, Any]]
  class Config:
    schema_extra = {
        "example": {
            "scenario_vars": {
              "technologies.biogas.fixed_oper_cost_per_iunit": {
                  "value": 11.0,
                  "statistic": ""
              }
            }
        }
    }

class Calculation(BaseModel):
  name: str
  data: Dict[Any, Any]

class CalculationPath(BaseModel):
  technology: str
  technology_full: str
  path: str