from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.models.users import UserRole


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    is_active: bool
    role: UserRole
