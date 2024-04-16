from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class InfoCommand(Base):
    """Model for default commands"""

    __tablename__ = "info_commands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100), unique=True)
    info: Mapped[str] = mapped_column(String(length=4096))