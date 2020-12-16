from pydantic import BaseSettings
from functools import lru_cache
import pathlib
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

    class Config:
        env_file = pathlib.Path(__file__).parents[0].joinpath('.env').resolve()

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
