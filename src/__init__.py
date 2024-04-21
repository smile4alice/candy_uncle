from src.info_commands.handlers import info_commands_router
from src.roll.handlers import roll_router
from src.socials.handlers import socials_router
from src.triggers.handlers import triggers_router


ROUTERS = (
    info_commands_router,
    roll_router,
    triggers_router,
    socials_router,
)
