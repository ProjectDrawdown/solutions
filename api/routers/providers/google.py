from urllib.parse import urlencode
from urllib.parse import parse_qsl

from api.db import get_user_by_login, create_user, fake_users_db

from api.routers.schemas import Url, AuthorizationResponse, GoogleUser, User, Token
from api.routers.helpers import generate_token, create_access_token
from api.config import Settings

from typing import Dict
import httpx

#from authlib.integrations.starlette_client import OAuth

settings = Settings()

provider = settings.provider[settings.default_provider]



LOGIN_URL = f"https://{provider['domain']}/signin/oauth/authorize"
#TOKEN_URL = f"https://{provider['domain']}/signin/oauth/access_token"
TOKEN_URL = f"https://oauth2.googleapis.com/token"
USER_URL = "https://api.github.com/user"
REDIRECT_URL = f"{settings.api_url}/auth/{settings.default_provider}"

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'


async def exchange_code(params):
    google_params = {
    'redirect_uri': REDIRECT_URL,
    'grant_type': 'authorization_code'
    }
    params.pop('state')
    params.update(google_params)
    print(params)
    async with httpx.AsyncClient() as client:
        token_request = await client.post(TOKEN_URL, data=params)
        print("Token")
        print(token_request)
        response: Dict[bytes, bytes] = dict(parse_qsl(token_request.content))
        github_token = response[b"access_token"].decode("utf-8")
        github_header = {"Authorization": f"token {github_token}"}
        user_request = await client.get(USER_URL, headers=github_header)
        github_user = Google(**user_request.json())

    db_user = get_user_by_login(github_user.login)
    if db_user is None:
        db_user = create_user("antonio", github_user)

    verified_user = fake_users_db[db_user.login]
    access_token = create_access_token(data=verified_user)
    return Token(access_token=access_token, token_type="bearer", user=db_user)
