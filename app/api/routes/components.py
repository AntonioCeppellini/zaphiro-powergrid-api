from __future__ import annotations
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.schemas.components import ComponentCreate, ComponentRead
from app.services.components import (
    list_components,
    create_component,
    update_component,
    delete_component,
)
from app.api.deps import get_current_user, require_manager
from app.models.users import User


router = APIRouter(prefix="/components", tags=["component"])


@router.get("", response_model=list[ComponentRead])
def components_list(
    component_type: Optional[str] = None,
    substation: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_components(db, component_type, substation, limit, offset)


@router.post("", response_model=ComponentRead)
def components_create(
    data: ComponentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    return create_component(db, payload=data.model_dump())


@router.put("/{component_id}", response_model=ComponentRead)
def components_update(
    component_id: UUID,
    data: ComponentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    try:
        return update_component(db, component_id, payload=data.model_dump())
    except LookupError:
        raise HTTPException(status_code=404, detail="Component not found")
    except ValueError as e:
        if str(e) == "component_type is required":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="component_type is required for PUT",
            )
        if str(e) == "component_type must not change":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Changing component is not allowed",
            )
        raise


@router.delete("/{component_id}", status_code=204)
def components_delete(
    component_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    try:
        return delete_component(db, component_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Component not found")
