from pydantic import BaseSettings

class Settings(BaseSettings):
    provider = {
    'github': {
       'domain': 'github.com',
       'client_id': '8a3847cc0c3c0137c4e5',
       'client_secret': 'f224953ec4f81de58c8c33188bf7cc71316576e6'
       },
     'google': {
        'domain': 'accounts.google.com',
        'client_id': '959419789086-u11hdmkljkcefar2l7vtff983tv2icu7.apps.googleusercontent.com',
        'client_secret': '576ASgg-3_XGMHqW8dCLEjDA'
     }
    }
    default_provider: str = 'github'
    api_url: str = 'http://localhost:8000'
    jwt_secret_key = 'hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH'
    jwt_algorithm = 'HS256'
