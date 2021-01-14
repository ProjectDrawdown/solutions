from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
from api.db import models
from api.config import get_resource_path
from api.transforms.validate_variation import validate_ref_vars, validate_scenario_vars

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

  @validator('scenario_vars')
  def validate_scenario(cls, v):
    res = validate_scenario_vars(v)
    if not res[0]:
      raise ValueError(res[1])
    return v

  @validator('reference_vars')
  def validate_reference(cls, v):
    res = validate_ref_vars(v)
    if not res[0]:
      raise ValueError(res[1])
    return v

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

class PublishVariation(BaseModel):
  name: str

class WorkbookNew(BaseModel):
  name: str
  ui: dict
  start_year: int
  end_year: int
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
        "end_year": 2050
      }
    }

class WorkbookPatch(BaseModel):
  name: Optional[str]
  ui: Optional[dict]
  start_year: Optional[int]
  end_year: Optional[int]
  variations: List[Dict[Any, Any]]
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
      }
    }

class WorkbookOut(BaseModel):
  id: int
  author: Optional[User]
  version: int
  name: str
  ui: dict
  start_year: int
  end_year: int
  variations: List[Dict[Any, Any]]
  class Config:
    orm_mode = True
    schema_extra = {
      "example": {
        "id": 1,
        "version": "2",
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
          {
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
        ]
      }
    }


class Calculation(BaseModel):
  name: str
  data: Dict[Any, Any]

class TechCalculation(BaseModel):
  path: str
  hash: str
  technology: str
  technology_full: str
  diff_path: Optional[str]

class CalculationMeta(BaseModel):
  previous_run_path: Optional[str]
  version: int
  path: str
  variation_data: VariationIn
  summary_path: str

class CalculationResults(BaseModel):
  meta: CalculationMeta
  results: List[TechCalculation]

class CalculationDiffs(BaseModel):
  tech: str
  diff: Dict[Any, Any]
