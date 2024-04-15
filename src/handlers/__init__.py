from src.handlers.admin.config import config_router
from src.handlers.info_commands import info_commands_router
from src.handlers.triggers import triggers_router
from src.handlers.user_helpers import user_helpers_router


ROUTERS = (
    config_router,
    info_commands_router,
    user_helpers_router,
    triggers_router,
)

__all__ = ("ROUTERS",)
