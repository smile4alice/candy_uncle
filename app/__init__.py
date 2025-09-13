"""Main app module."""

from app.features.instagram.routes import router as instagram_router
from app.features.roll.routes import router as roll_router
from app.features.tiktok.routes import router as tiktok_router
from app.features.youtube.routes import router as youtube_router


ROUTERS = [
    instagram_router,
    roll_router,
    tiktok_router,
    youtube_router,
]
