from pydantic import BaseModel

class AuthorizationResponse(BaseModel):
    state: str
    code: str

class GithubUser(BaseModel):
    login: str
    name: str
    company: str
    location: str
    email: str
    avatar_url: str

class User(BaseModel):
    id: int
    login: str
    name: str
    company: str
    location: str
    email: str
    picture: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Url(BaseModel):
    url: str
