from src.handlers.admin.config import config_router
from src.handlers.base_commands import base_commands_router
from src.handlers.triggers import triggers_router
from src.handlers.user_helpers import user_helpers_router


ROUTERS = (
    config_router,
    base_commands_router,
    user_helpers_router,
    triggers_router,
)

__all__ = ("ROUTERS",)
