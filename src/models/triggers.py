from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.enums import MatchTypeEnum, MediaTypeEnum


class Trigger(Base):
    __tablename__ = "triggers"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    match_type: Mapped[MatchTypeEnum] = mapped_column(default=MatchTypeEnum.text)
    name: Mapped[str] = mapped_column(String(length=100))
    trigger: Mapped[str] = mapped_column(String(length=4096))
    chat_id: Mapped[int]

    answers: Mapped[List["TriggersAnswer"]] = relationship(
        back_populates="trigger", lazy="selectin"
    )


class TriggersAnswer(Base):
    __tablename__ = "triggers_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    answer_type: Mapped[MediaTypeEnum]
    answer: Mapped[str] = mapped_column(String(length=4096))
    trigger_id: Mapped[int] = mapped_column(ForeignKey("triggers.id"))

    trigger: Mapped["Trigger"] = relationship(back_populates="answers", lazy="selectin")
