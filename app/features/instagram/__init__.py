"""Instagram feature module."""

from app.features.instagram.routes import instagram_router
from app.features.instagram.schemas import InstagramServiceDTO

__all__ = ["instagram_router", "InstagramServiceDTO"]
