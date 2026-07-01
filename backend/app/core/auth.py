"""
Auth helpers — password hashing (bcrypt) + JWT (HS256).
Cookie name: apt_token  |  Algorithm: HS256  |  Expiry: 24h
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production-use-a-long-random-string")
ALGORITHM  = "HS256"
EXPIRE_H   = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
COOKIE     = "apt_token"


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int, login: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=EXPIRE_H)
    return jwt.encode(
        {"sub": str(user_id), "login": login, "role": role, "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    """Raises JWTError on invalid/expired token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
