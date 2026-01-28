from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

import app.models

from app.core.security import hash_password
from app.models.users import User, UserRole


def main() -> None:
    """
    Create demo users:
      - manager / managerpass
      - user / userpass
    """
    database_url = os.getenv("DATABASE_URL")

    manager_username = "manager"
    manager_password = "managerpass"
    user_username = "user"
    user_password = "userpass"

    engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with SessionLocal() as db:
        rows = [
            {
                "username": manager_username,
                "hashed_password": hash_password(manager_password),
                "role": UserRole.manager,
                "is_active": True,
            },
            {
                "username": user_username,
                "hashed_password": hash_password(user_password),
                "role": UserRole.user,
                "is_active": True,
            },
        ]

        query = insert(User).values(rows)

        query = query.on_conflict_do_nothing(index_elements=[User.username])

        db.execute(query)
        db.commit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise
