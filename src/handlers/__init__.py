from src.handlers.admin.base_commands_admin import admin_base_commands_router
from src.handlers.base_commands import base_commands_router
from src.handlers.user_helpers import user_helpers_router


ROUTERS = (
    admin_base_commands_router,
    base_commands_router,
    user_helpers_router,
)

__all__ = ("ROUTERS",)
