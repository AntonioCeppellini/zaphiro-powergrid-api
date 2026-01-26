from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.users import User


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    from the user.username it takes the user from the db.
    receives username.
    return the User or None.
    """
    return db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    from the username and the password authenticates or not the user.
    receives username and password.
    return the User or None.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
