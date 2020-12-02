from urllib.parse import urlencode
from urllib.parse import parse_qsl

from api.routers.schemas import Url, AuthorizationResponse, GithubUser, User, Token
from api.routers.helpers import generate_token, create_access_token
from api.config import Settings

from typing import Dict
import httpx

settings = Settings()
provider = settings.provider[settings.default_provider]
LOGIN_URL = f"https://{provider['domain']}/login/oauth/authorize"
TOKEN_URL = f"https://{provider['domain']}/login/oauth/access_token"

USER_URL = "https://api.github.com/user"


fake_users_db = {
    "johndoe": {
        "id": 1,
        "login": "johndoe",
        "name": "John Doe",
        "company": "colab",
        "location": "NY",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "id": 2,
        "login": "alice",
        "name": "Alice Wonderson",
        "company": "colab",
        "location": "NY",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

def get_user_by_login(login):
    if login in fake_users_db:
        return fake_users_db[login]


def create_user(name, payload):
    fake_users_db[name] = payload
    return fake_users_db[name]



async def exchange_code(params):
    async with httpx.AsyncClient() as client:
        token_request = await client.post(TOKEN_URL, params=params)
        response: Dict[bytes, bytes] = dict(parse_qsl(token_request.content))
        github_token = response[b"access_token"].decode("utf-8")
        github_header = {"Authorization": f"token {github_token}"}
        user_request = await client.get(USER_URL, headers=github_header)
        github_user = GithubUser(**user_request.json())

    db_user = get_user_by_login(github_user.login)
    if db_user is None:
        db_user = create_user("javm", github_user)

    verified_user = fake_users_db[db_user.login]
    access_token = create_access_token(data=verified_user)
    return Token(access_token=access_token, token_type="bearer", user=db_user)
