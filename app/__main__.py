import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web

from app import ROUTERS
from app.config import settings
from app.common.enums import Environment
from app.common.logging import LOGGER
from app.common.storage import STORAGE


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(
        f"{settings.WEBHOOK_HOST}{settings.WEBHOOK_PATH}",
        certificate=FSInputFile(settings.WEBHOOK_SSL_CERT),
        secret_token=settings.WEBHOOK_SECRET,
    )


def start_web_app(
    dp: Dispatcher,
    bot: Bot,
    loop: asyncio.AbstractEventLoop,
):
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Create aiohttp.web.Application instance
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )

    # Register webhook handler on application
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(
        app,
        host=settings.WEB_SERVER_HOST,
        port=settings.WEB_SERVER_PORT,
        loop=loop,
    )


def main(loop: asyncio.AbstractEventLoop):
    LOGGER.info("Bot is started")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=STORAGE)

    dp.include_routers(*ROUTERS)

    if settings.ENVIRONMENT == Environment.PRODUCTION:
        start_web_app(dp, bot, loop)
    else:
        loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
        loop.run_until_complete(dp.start_polling(bot))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    main(loop)
