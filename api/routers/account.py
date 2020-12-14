import importlib
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.config import get_settings, get_db
from .schemas import Url, User, Token, AuthorizationResponse

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get('/login')
def get_login_url_default() -> Url:
    return get_login_url(default_provider)

@router.post('/authorize')
async def verify_authorization_default(body: AuthorizationResponse) -> Token:
    return await verify_authorization(body, default_provider)

@router.get('/login/{provider}')
def get_login_url(provider: str) -> Url:
    importname = 'api.routers.providers.' + provider
    provider_module = importlib.import_module(importname)
    return provider_module.login_url()

@router.post('/authorize/{provider}')
async def verify_authorization( body: AuthorizationResponse, provider: str, db: Session = Depends(get_db)) -> Token:
    importname = 'api.routers.providers.' + provider
    provider_module = importlib.import_module(importname)
    return await provider_module.exchange_code(body, db)
