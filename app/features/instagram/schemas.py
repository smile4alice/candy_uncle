"""Instagram schemas."""

from typing import Any

from aiogram.types import InputMedia
from pydantic import BaseModel


class InstagramServiceDTO(BaseModel):
    """Instagram service data transfer object."""

    media: list[InputMedia] | str | None = None
    channel_url: str | None = None
    is_photo: bool = False
    is_video: bool = False
    is_sidecar: bool = False
    is_text: bool = False

    class Config:
        arbitrary_types_allowed = True
