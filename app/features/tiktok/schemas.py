"""TikTok schemas."""

from pydantic import BaseModel


class TikTokServiceDTO(BaseModel):
    """TikTok service data transfer object."""

    media: str | None = None
    is_video: bool = False
    is_text: bool = False
