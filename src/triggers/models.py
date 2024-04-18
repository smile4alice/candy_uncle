from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.enums import MatchModeEnum, MediaTypeEnum


class TriggerEvent(Base):
    __tablename__ = "trigger_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    match_mode: Mapped[MatchModeEnum] = mapped_column(default=MatchModeEnum.text)
    name: Mapped[str] = mapped_column(String(length=100))
    event: Mapped[str] = mapped_column(String(length=4096))
    chat_id: Mapped[int]

    triggers: Mapped[List["Trigger"]] = relationship(
        back_populates="trigger_event", passive_deletes=True
    )


class Trigger(Base):
    __tablename__ = "triggers"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    media_type: Mapped[MediaTypeEnum]
    media: Mapped[str] = mapped_column(String(length=4096))
    trigger_event_id: Mapped[int] = mapped_column(
        ForeignKey("trigger_events.id", ondelete="Cascade")
    )

    trigger_event: Mapped["TriggerEvent"] = relationship(back_populates="triggers")
