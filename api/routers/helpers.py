from datetime import datetime, timedelta

import jwt

from api.config import Settings
from .schemas import User

from fastapi import Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import ValidationError


settings = Settings()


def get_user_from_header(*, authorization: str = Header(None)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        try:
            token_data = User(**payload)
            return token_data
        except ValidationError:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception


def create_access_token(*, data: User, exp: int = None) -> bytes:
    to_encode = data.dict()
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
