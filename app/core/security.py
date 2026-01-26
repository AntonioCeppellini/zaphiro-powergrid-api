from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    hashing a password.
    takes the clear password and returns the hashed version.
    return the hashed password.
    """
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    verifying a password.
    takes a clear password check against the hashed version.
    returns a bool (True/False).
    """
    return password_hasher.verify(password, hashed_password)


def create_access_token(
    subject: str,
    expires_minutes: int | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    """
    creating a jwt token.
    subject is intended to be the user.id
    extra should be role right now but using extra to be open to
    update such as scopes ecc...
    subject is the user.id
    expires_minutes is the time for the token to expire
    extra right now is a dictionary {"role": user.role}.
    return the token.
    """
    if not expires_minutes:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(expires_minutes)

    data = {"sub": subject, "exp": expire}

    if extra:
        data.update(extra)

    token = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return token


def decode_token(token: str) -> dict[str:any]:
    """
    decodes and validate JWT a given token.
    raises JWT exceptions if invalid/expired.
    returns the payload that created the token.
    """
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
