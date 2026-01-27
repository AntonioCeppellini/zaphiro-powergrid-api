from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.tests.config import TEST_DATABASE_URL
from app.models.components import Transformer, Line, Switch
from app.core.security import hash_password
from app.models.users import User, UserRole


_ENGINE = None
_SESSIONLOCAL = None


def _get_sessionlocal():
    global _ENGINE, _SESSIONLOCAL
    if _SESSIONLOCAL is None:
        _ENGINE = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
        _SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)
    return _SESSIONLOCAL


def override_get_db():
    SessionLocal = _get_sessionlocal()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestDatabase:
    def __init__(self, session: Session):
        self.session = session

    def populate_test_database(self) -> None:
        components = []

        # --- Transformers ---
        for i in range(1, 4):
            components.append(
                Transformer(
                    component_type="transformer",
                    name=f"T-seed-{i}",
                    substation="S1",
                    capacity_mva=50.0 * i,
                    voltage_kv=132.0,
                )
            )

        # --- Lines ---
        for i in range(1, 4):
            components.append(
                Line(
                    component_type="line",
                    name=f"L-seed-{i}",
                    substation="S2",
                    length_km=5.0 * i,
                    voltage_kv=132.0,
                )
            )

        # --- Switches ---
        for i in range(1, 4):
            components.append(
                Switch(
                    component_type="switch",
                    name=f"SW-seed-{i}",
                    substation="S3",
                    status="open" if i % 2 == 0 else "closed",
                )
            )

        self.session.add_all(components)
        self.session.commit()

        # Manager user
        self.session.add(
            User(
                username="manager",
                hashed_password=hash_password("managerpass"),
                role=UserRole.manager,
                is_active=True,
            )
        )
        
        # Regular user
        self.session.add(
            User(
                username="user",
                hashed_password=hash_password("userpass"),
                role=UserRole.user,
                is_active=True,
            )
        )
        
        self.session.commit()
