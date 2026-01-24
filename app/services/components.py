from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.components import Component, Transformer, Line, Switch, ComponentType


def list_components(
    db: Session,
    component_type: Optional[str] = None,
    substation: OPtional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    query = select(Component).offset(offset).limit(limit)

    if component_type:
        query = query.where(Component.component_type == ComponentType(component_type))
    if substation:
        query = query.where(Component.substation == substation)

    return db.execute(query).scalars().all()


def get_component(db: Session, component_id: UUID) -> Component | None:
    query = select(Component).where(Component.id == component_id)
    return db.execute(query).scalar_one_or_none()


def create_component(db: Session, payload: dict) -> Component:
    component_type = payload["component_type"]

    if component_type == "transformer":
        new_component = Transformer(**payload)
    elif component_type == "line":
        new_component = Line(**payload)
    elif component_type == "switch":
        new_component = Switch(**payload)
    else:
        raise ValueError("Invalid component_type")

    db.add(new_component)
    db.commit()
    db.refresh(new_component)
    return new_component


def update_component(db: Session, component_id: UUID, payload: dict) -> Component:
    component = get_component(db, component_id)
    if not component:
        raise LookupError("not_found")

    incoming_type = payload.get("component_type")
    old_type = component.component_type.value

    if incoming_type is None:
        raise ValueError("component_type is required")

    if incoming_type != old_type:
        raise ValueError("component_type must not change")

    for key, value in payload.items():
        setattr(component, key, value)

    db.commit()
    db.refresh(component)
    return component


def delete_component(db: Session, component_id: UUID) -> None:
    component = get_component(db, component_id)

    if not component:
        raise LookupError("not_found")

    db.delete(component)
    db.commit()
