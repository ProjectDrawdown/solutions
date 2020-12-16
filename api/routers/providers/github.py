import httpx
from urllib.parse import urlencode
from urllib.parse import parse_qsl
from typing import Dict
from api.queries import get_user, create_user
from api.routers.schemas import Url, AuthorizationResponse, GithubUser, User, Token
from api.routers.helpers import generate_token, create_access_token, row2dict
from api.config import get_settings, get_providers

settings = get_settings()
provider = get_providers()['github']

LOGIN_URL = f"https://{provider['domain']}/login/oauth/authorize"
TOKEN_URL = f"https://{provider['domain']}/login/oauth/access_token"
REDIRECT_URL = f"{settings.api_url}/auth/github"

USER_URL = settings.github_user_url

def login_url():
    params = {
        'client_id': provider['client_id'],
        'redirect_uri': REDIRECT_URL,
        'state': generate_token(),
    }
    return Url(url=f"{LOGIN_URL}?{urlencode(params)}")

async def exchange_code(body, db):
    params = {
        'client_id': provider['client_id'],
        'client_secret': provider['client_secret'],
        'code': body.code,
        'state': body.state,
    }
    async with httpx.AsyncClient() as client:
        token_request = await client.post(TOKEN_URL, params=params)
        response: Dict[bytes, bytes] = dict(parse_qsl(token_request.content))
        github_token = response[b"access_token"].decode("utf-8")
        github_header = {"Authorization": f"token {github_token}"}
        user_request = await client.get(USER_URL, headers=github_header)
        github_user = GithubUser(**user_request.json())

    db_user = get_user(db, github_user)
    if db_user is None:
        db_user = create_user(db, github_user)

    user_data = row2dict(db_user)
    access_token = create_access_token(data=user_data)
    return Token(access_token=access_token, token_type="bearer", user=user_data)
