from pydantic import BaseSettings

class Settings(BaseSettings):
    provider = {
    'github': {
       'domain': 'github.com',
       'client_id': '8a3847cc0c3c0137c4e5',
       'client_secret': 'f224953ec4f81de58c8c33188bf7cc71316576e6'
       },
     'google': {
        'domain': 'google.com',
        'client_id': '123'
     }
    }
    default_provider: str = 'github'
    api_url: str = 'http://localhost:8000'
    jwt_secret_key = 'hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH'
    jwt_algorithm = 'HS256'
