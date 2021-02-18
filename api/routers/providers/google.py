import httpx
from typing import Dict
from urllib.parse import urlencode
from urllib.parse import parse_qsl
from api.queries.user_queries import get_user, create_user
from api.routers.schemas import Url, AuthorizationResponse, GoogleUser, User, Token
from api.routers.helpers import generate_token, create_access_token, decode_google_id_token, row2dict
from api.config import get_settings, get_providers
from api.db import models

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
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return Url(url=f"{LOGIN_URL}?{urlencode(params)}")


async def exchange_code(body, db):
    params = {
        'client_id': provider['client_id'],
        'client_secret': provider['client_secret'],
        'code': body.code,
        'redirect_uri': REDIRECT_URL,
        'grant_type': 'authorization_code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    async with httpx.AsyncClient() as client:
        token_info = await client.post(TOKEN_URL, data=params)
        json_response = token_info.json()
        refresh_token = json_response['refresh_token']
        id_token = json_response['id_token']
        user_data = decode_google_id_token(id_token)
        user_data['login'] = user_data['email']
        google_user = GoogleUser(**user_data)

    db_user = get_user(db, google_user)
    if db_user is None:
        user = models.User(
            login = google_user.login,
            email = google_user.email,
            provider = 'google',
            name = google_user.name,
            location = google_user.location,
            picture = google_user.picture,
            is_active = True,
            meta = {}
        )
        db_user = create_user(db, user)

    user_dict = row2dict(db_user)
    user_dict['meta'] = {}
    user_dict['refresh_token'] = refresh_token
    access_token = create_access_token(data=user_dict)
    return Token(access_token=access_token, token_type="bearer", user=user_dict)

async def refresh_code(refresh_token, db):
    params = {
        'client_id': provider['client_id'],
        'client_secret': provider['client_secret'],
        'refresh_token': refresh_token,
        'redirect_uri': REDIRECT_URL,
        'grant_type': 'refresh_token',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    async with httpx.AsyncClient() as client:
        token_info = await client.post(TOKEN_URL, data=params)
        json_response = token_info.json()
        id_token = json_response['id_token']
        user_data = decode_google_id_token(id_token)
        user_data['login'] = user_data['email']

    db_user = db.query(models.User).filter(models.User.login==user_data['login']).first()

    user_dict = row2dict(db_user)
    user_dict['meta'] = {}
    user_dict['refresh_token'] = refresh_token
    access_token = create_access_token(data=user_dict)
    return Token(access_token=access_token, token_type="bearer", user=user_dict)
