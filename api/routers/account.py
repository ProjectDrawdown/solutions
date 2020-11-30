from urllib.parse import urlencode

from fastapi import APIRouter

from api.config import Settings
from .schemas import Url
from .helpers import generate_token

settings = Settings()
LOGIN_URL = "https://dev-oj3dl9a4.us.auth0.com/authorize"

REDIRECT_URL = f"{settings.api_url}"

router = APIRouter()

@router.get("/login")
def get_login_url() -> Url:
    params = {
        "client_id": settings.auth0_client_id,
        "redirect_uri": REDIRECT_URL,
        "state": generate_token(),
    }
    return Url(url=f"{LOGIN_URL}?{urlencode(params)}")
