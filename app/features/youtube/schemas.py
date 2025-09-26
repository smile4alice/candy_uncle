"""YouTube schemas."""

from enum import Enum

from aiogram.types import BufferedInputFile
from pydantic import BaseModel


class MediaType(str, Enum):
    """Media type enumeration."""

    VIDEO = "video"
    SHORTS = "shorts"


class QualityType(str, Enum):
    """Quality type enumeration."""

    HIGHEST = "highest"
    LOWEST = "lowest"
    MEDIUM = "medium"


class YouTubeServiceDTO(BaseModel):
    """YouTube service data transfer object."""

    media: BufferedInputFile | str | None = None
    title: str | None = None
    duration: int | None = None
    views: int | None = None
    media_type: MediaType | None = None
    quality: str | None = None
    file_size: float | None = None  # in MB
    upload_date: str | None = None  # YYYYMMDD format
    error_message: str | None = None

    class Config:
        arbitrary_types_allowed = True
