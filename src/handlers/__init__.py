from src.handlers.admin.base_commands_admin import admin_base_commands_router
from src.handlers.base_commands import base_commands_router


ROUTERS = (
    admin_base_commands_router,
    base_commands_router,
)

__all__ = ("ROUTERS",)
