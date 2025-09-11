"""Main app module."""

from app.features.instagram import instagram_router
from app.features.roll import roll_router
from app.features.tiktok import tiktok_router


ROUTERS = (
    roll_router,
    instagram_router,
    tiktok_router,
)
