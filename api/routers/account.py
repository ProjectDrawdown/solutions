import importlib
from fastapi import APIRouter
from api.config import Settings
from .schemas import Url, User, Token, AuthorizationResponse

settings = Settings()
importname = 'api.routers.providers.' + settings.default_provider
provider_module = importlib.import_module(importname)
provider = settings.provider[settings.default_provider]

router = APIRouter()

@router.get("/login")
def get_login_url() -> Url:
    return provider_module.login_url()

@router.post("/authorize")
async def verify_authorization(
 body: AuthorizationResponse
) -> Token:
    return await provider_module.exchange_code(body)
