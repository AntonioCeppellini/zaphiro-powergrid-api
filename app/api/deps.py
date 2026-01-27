from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.connection import get_db
from app.models.users import User, UserRole
from app.services.users import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    takes the current user from the request.
    it takes the token.
    it returns the user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = get_user_by_username(db, username=username)
    if not user:
        raise credentials_exception

    return user


def require_manager(user: User = Depends(get_current_user)) -> User:
    """
    it checks if the current user is a manager.
    it receives the current user.
    it returns the user if everything is fine.
    """
    if user.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return user
