from pydantic import BaseSettings
import aiohttp
from typing import Any, Dict, List, Union, Optional
from functools import lru_cache
import pathlib
import aioredis
import fastapi_plugins

from api.db.database import get_session_maker

class Settings(BaseSettings):

    default_provider: str = 'google'
    api_url: str
    jwt_secret_key: str
    jwt_algorithm: str

    github_domain: str
    github_client_id: str
    github_client_secret: str
    github_user_url: str

    google_domain: str
    google_client_id: str
    google_client_secret: str

    database_url: str
    redis_url: str

    max_workers: int

    client_url: str
    auth_redirect_url: str

    is_production: Optional[bool]

    class Config:
        env_file = pathlib.Path(__file__).parents[0].joinpath('.env').resolve()

class RedisSettings(fastapi_plugins.RedisSettings):
    pass

@lru_cache()
def get_settings():
    return Settings()

@lru_cache()
def get_providers():
    settings = get_settings()
    provider = {
    'github': {
        'domain': settings.github_domain,
        'client_id': settings.github_client_id,
        'client_secret': settings.github_client_secret
        },
    'google': {
        'domain': settings.google_domain,
        'client_id': settings.google_client_id,
        'client_secret': settings.google_client_secret
        }
    }
    return provider

session_maker = get_session_maker(get_settings().database_url)

def get_db():
    db = session_maker()
    try:
        yield db
    finally:
        db.close()

def get_resource_path(entity: str, id: int):
  api_url = get_settings().api_url
  return f'{api_url}/resource/{entity}/{id}/'

def get_projection_path(path: str, id: int):
  api_url = get_settings().api_url
  return f'{api_url}/projection/{path}/{id}/'

def get_path(path: str, id: int):
  api_url = get_settings().api_url
  return f'{api_url}/{path}/{id}/'

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
class AioWrap(object):
    async def __call__(self, site: str) -> JSONType:
        async with aiohttp.ClientSession() as client:
            async with client.get(site) as resp:
                return await resp.json()

app = None

def get_app():
    return app
