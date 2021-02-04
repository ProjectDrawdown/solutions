import jwt
from datetime import datetime, timedelta
from api.config import get_settings
from .schemas import User
from fastapi import Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.params import Security
from pydantic import ValidationError

settings = get_settings()
security = HTTPBearer() 
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d

def get_user_from_header(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials, settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        try:
            token_data = User(**payload)
            return token_data
        except ValidationError:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

def get_refresh_token_from_header(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials, settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        try:
            return payload['refresh_token']
        except ValidationError:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

def create_access_token(*, data: User, exp: int = None) -> bytes:
    to_encode = data
    if exp is not None:
        to_encode.update({"exp": exp})
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def generate_token():
    return 0

def decode_google_id_token(id_token):
    decoded_token = jwt.decode(id_token, verify=False)
    return decoded_token
