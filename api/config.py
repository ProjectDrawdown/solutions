from pydantic import BaseSettings

class Settings(BaseSettings):
    api_url: str = 'localhost'
    github_client_id = '123456'
