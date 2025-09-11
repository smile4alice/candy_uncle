"""TikTok feature module."""

from app.features.tiktok.routes import tiktok_router
from app.features.tiktok.schemas import TikTokServiceDTO

__all__ = ["tiktok_router", "TikTokServiceDTO"]
