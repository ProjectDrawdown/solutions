import importlib
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.config import get_settings, get_db
from api.routers.schemas import Url, User, Token, AuthorizationResponse
from api.routers.helpers import get_refresh_token_from_header

settings = get_settings()
router = APIRouter()
default_provider = settings.default_provider

@router.get('/authredirect', response_class=RedirectResponse)
def for_dev_only_will_remove():
    return RedirectResponse(get_login_url_default().url)

@router.get('/auth/{provider}')
async def for_dev_only_will_remove2(code: str, provider: str, db: Session = Depends(get_db)):
    body = AuthorizationResponse(code=code, state=0)
    return await verify_authorization(body, provider, db)

@router.get('/login',
        summary="Get login url from default provider"
        )
def get_login_url_default() -> Url:
    return get_login_url(default_provider)

@router.get('/login/{provider}',
        summary="Get login url from given provider"
        )
def get_login_url(provider: str) -> Url:
    importname = 'api.routers.providers.' + provider
    provider_module = importlib.import_module(importname)
    return provider_module.login_url()

@router.post('/authorize/{provider}',
        summary="Get jwt for a given provider",
        description="""
The client must provide the auth code from the oauth provider.
        """
        )
async def verify_authorization(body: AuthorizationResponse, provider: str, db: Session = Depends(get_db)) -> Token:
    importname = 'api.routers.providers.' + provider
    provider_module = importlib.import_module(importname)
    return await provider_module.exchange_code(body, db)

@router.post("/refresh-token/{provider}",
        summary="Creates a new jwt using the refresh oauth api."
        )
async def refresh_token(provider: str, refresh_token: str = Depends(get_refresh_token_from_header), db: Session = Depends(get_db)):
    importname = 'api.routers.providers.' + provider
    provider_module = importlib.import_module(importname)
    return await provider_module.refresh_code(refresh_token, db)
