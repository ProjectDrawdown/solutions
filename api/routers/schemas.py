from typing import Optional, List, Dict, Any
from pydantic import BaseModel

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
  login: str
  name: str
  company: str = None
  location: str = None
  email: str
  picture: str = None

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

class WorkbookPatch(BaseModel):
  name: Optional[str]
  ui: Optional[dict]
  start_year: Optional[int]
  end_year: Optional[int]
  variations: Optional[List[str]]

class ResourceOut(BaseModel):
  id: Optional[int]
  name: Optional[str]
  data: Dict[Any, Any]
  path: Optional[str]
  class Config:
    orm_mode = True

class VariationOut(ResourceOut):
  pass

class ResourceIn(BaseModel):
  name: Optional[str]
  data: Dict[Any, Any]

class VariationIn(ResourceIn):
  scenario_parent_path: str
  reference_parent_path: str
