#from urllib.parse import urlencode
#from urllib.parse import parse_qsl

import importlib
from fastapi import APIRouter
from api.config import Settings

from .schemas import Url, User, Token, AuthorizationResponse
#from .helpers import generate_token, create_access_token
#from typing import Dict
#import httpx

settings = Settings()
importname = 'api.routers.providers.' + settings.default_provider

provider_module = importlib.import_module(importname)

provider = settings.provider[settings.default_provider]
#LOGIN_URL = f"https://{provider['domain']}/login/oauth/authorize"

#LOGIN_URL = f"https://{provider['domain']}/signin/oauth/authorize"
#TOKEN_URL = f"https://{provider['domain']}/login/oauth/access_token"

#REDIRECT_URL = f"{settings.api_url}/auth/{settings.default_provider}"

router = APIRouter()

@router.get("/login")
def get_login_url() -> Url:
    return provider_module.login_url()

@router.post("/authorize")
async def verify_authorization(
 body: AuthorizationResponse
) -> Token:
    return await provider_module.exchange_code(body)
