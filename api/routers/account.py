from urllib.parse import urlencode
from urllib.parse import parse_qsl

import importlib

from fastapi import APIRouter, Depends

from api.config import Settings
from .schemas import Url, AuthorizationResponse, GithubUser, User, Token
from .helpers import generate_token, create_access_token
from api.db import get_user_by_login, create_user
from typing import Dict
import httpx

settings = Settings()
importname = 'api.routers.providers.' + settings.default_provider

provider_module = importlib.import_module(importname)

provider = settings.provider[settings.default_provider]
LOGIN_URL = f"https://{provider['domain']}/login/oauth/authorize"
TOKEN_URL = f"https://{provider['domain']}/login/oauth/access_token"

REDIRECT_URL = f"{settings.api_url}/auth/{settings.default_provider}"

router = APIRouter()


@router.get("/login")
def get_login_url() -> Url:
    params = {
        "client_id": provider['client_id'],
        "redirect_uri": REDIRECT_URL,
        "state": generate_token(),
    }
    return Url(url=f"{LOGIN_URL}?{urlencode(params)}")


@router.post("/authorize")
async def verify_authorization(
 body: AuthorizationResponse
) -> Token:
    params = {
        "client_id": provider['client_id'],
        "client_secret": provider['client_secret'],
        "code": body.code,
        "state": body.state,
    }
    return await provider_module.exchange_code(params)
