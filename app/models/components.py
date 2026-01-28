from __future__ import annotations
import uuid
import enum

from typing import List
from sqlalchemy import String, Integer, ForeignKey, Float, Enum, Index, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class ComponentType(str, enum.Enum):
    transformer = "transformer"
    line = "line"
    switch = "switch"


class SwitchStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class Component(Base):
    """
    Base component table.
    Types (Transformer, Line, Switch) extend this via joined-table inheritance.
    """

    __tablename__ = "components"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    substation: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    component_type: Mapped[ComponentType] = mapped_column(
        Enum(ComponentType, name="component_type"), nullable=False, index=True
    )

    measurements: Mapped[List["Measurement"]] = relationship(
        "Measurement",
        back_populates="component",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_components_type_substation", "component_type", "substation"),
    )

    __mapper_args__ = {
        "polymorphic_on": component_type,
        "polymorphic_identity": "component",
    }


class Transformer(Component):
    __tablename__ = "transformers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("components.id", ondelete="CASCADE"),
        primary_key=True,
    )

    capacity_mva: Mapped[float] = mapped_column(Float, nullable=False)

    voltage_kv: Mapped[float] = mapped_column(Float, nullable=False)

    # component: Mapped["Component"] = relationship(
    #     back_populates="transformer"
    # )

    __mapper_args__ = {"polymorphic_identity": ComponentType.transformer.value}


class Line(Component):
    __tablename__ = "lines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("components.id", ondelete="CASCADE"),
        primary_key=True,
    )

    length_km: Mapped[float] = mapped_column(Float, nullable=False)

    voltage_kv: Mapped[float] = mapped_column(Float, nullable=False)

    __mapper_args__ = {"polymorphic_identity": ComponentType.line.value}


class Switch(Component):
    __tablename__ = "switches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("components.id", ondelete="CASCADE"),
        primary_key=True,
    )

    status: Mapped[SwitchStatus] = mapped_column(
        Enum(SwitchStatus, name="switch_status"), nullable=False
    )

    __mapper_args__ = {"polymorphic_identity": ComponentType.switch.value}
