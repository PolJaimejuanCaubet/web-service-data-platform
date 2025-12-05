from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from backend.app.config.config import settings as env
from typing import Optional


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, env.JWT_SECRET, algorithm=env.JWT_ALGORITHM)


def create_access_tokenX(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, env.JWT_SECRET, algorithm=env.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=env.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(to_encode, env.JWT_SECRET, algorithm=env.JWT_ALGORITHM)


def decode_token(token: str):
    try:
        user = jwt.decode(token, env.JWT_SECRET, algorithms=[env.JWT_ALGORITHM])
        return user
    except JWTError:
        return None
