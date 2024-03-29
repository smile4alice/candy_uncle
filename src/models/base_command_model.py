from sqlalchemy import Column, Integer, String

from src.database import Base


class BaseCommandModel(Base):
    """Model for default commands"""

    __tablename__ = "base_commands"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(length=255), nullable=False, unique=True)
    text: str = Column(String(length=4096), nullable=False)
