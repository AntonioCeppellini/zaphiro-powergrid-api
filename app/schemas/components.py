from __future__ import annotations
from typing import Annotated, Literal, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# base schema for components
class ComponentCreateBase(BaseModel):
    name: str
    substation: str


class TransformerCreate(ComponentCreateBase):
    component_type: Literal["transformer"]
    capacity_mva: float
    voltage_kv: float


class LineCreate(ComponentCreateBase):
    component_type: Literal["line"]
    length_km: float
    voltage_kv: float


class SwitchCreate(ComponentCreateBase):
    component_type: Literal["switch"]
    status: Literal["open", "closed"]


ComponentCreate = Annotated[
    Union[TransformerCreate, LineCreate, SwitchCreate],
    Field(discriminator="component_type"),
]


class ComponentReadBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    substation: str
    component_type: str

class TransformerRead(ComponentReadBase):
    component_type: Literal["transformer"]
    capacity_mva: float
    voltage_kv: float

class LineRead(ComponentReadBase):
    component_type: Literal["line"]
    length_km: float
    voltage_kv: float

class SwitchRead(ComponentReadBase):
    component_type: Literal["switch"]
    status: str

ComponentRead = Annotated[
    Union[TransformerRead, LineRead, SwitchRead],
    Field(discriminator="component_type"),
]
