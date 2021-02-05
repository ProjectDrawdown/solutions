import httpx
from typing import Dict
from urllib.parse import urlencode
from urllib.parse import parse_qsl
from api.queries.user_queries import get_user, create_user
from api.routers.schemas import Url, AuthorizationResponse, GoogleUser, User, Token
from api.routers.helpers import generate_token, create_access_token, decode_google_id_token, row2dict
from api.config import get_settings, get_providers

settings = get_settings()
provider = get_providers()['google']

LOGIN_URL = f"https://{provider['domain']}/signin/oauth/authorize"
TOKEN_URL = f"https://oauth2.googleapis.com/token"
REDIRECT_URL = f"{settings.auth_redirect_url}/auth/google"

def login_url():
    params = {
        'client_id': provider['client_id'],
        'response_type': 'code',
        'redirect_uri': REDIRECT_URL,
        'scope': 'email profile openid',
        'state': generate_token(),
    }
    return Url(url=f"{LOGIN_URL}?{urlencode(params)}")


async def exchange_code(body, db):
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

    db_user = get_user(db, google_user)
    if db_user is None:
        db_user = create_user(db, google_user, 'google')

    user_dict = row2dict(db_user)
    access_token = create_access_token(data=user_dict)
    return Token(access_token=access_token, token_type="bearer", user=user_dict)
