import httpx
from typing import Dict
from urllib.parse import urlencode
from urllib.parse import parse_qsl
from api.db import get_user_by_login, create_user, fake_users_db
from api.routers.schemas import Url, AuthorizationResponse, GoogleUser, User, Token
from api.routers.helpers import generate_token, create_access_token, decode_google_id_token
from api.config import get_settings, get_providers

settings = get_settings()
provider = get_providers()['google']

LOGIN_URL = f"https://{provider['domain']}/signin/oauth/authorize"
TOKEN_URL = f"https://oauth2.googleapis.com/token"
REDIRECT_URL = f"{settings.api_url}/auth/google"

def login_url():
    params = {
        'client_id': provider['client_id'],
        'response_type': 'code',
        'redirect_uri': REDIRECT_URL,
        'scope': 'email profile openid',
        'state': generate_token(),
    }
    return Url(url=f"{LOGIN_URL}?{urlencode(params)}")


async def exchange_code(body):
    params = {
    'client_id': provider['client_id'],
    'client_secret': provider['client_secret'],
    'code': body.code,
    'redirect_uri': REDIRECT_URL,
    'grant_type': 'authorization_code'
    }
    async with httpx.AsyncClient() as client:
        token_info = await client.post(TOKEN_URL, data=params)
        json_response = token_info.json()
        id_token = json_response['id_token']
        user_data = decode_google_id_token(id_token)
        user_data['login'] = user_data['email']
        google_user = GoogleUser(**user_data)

    db_user = get_user_by_login(google_user.login)
    if db_user is None:
        db_user = create_user(google_user.login, google_user)

    verified_user = fake_users_db[db_user.login]
    access_token = create_access_token(data=verified_user)
    return Token(access_token=access_token, token_type="bearer", user=db_user)
