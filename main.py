import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web
from src.config import SETTINGS, Environment
from src.handlers import ROUTERS
from src.logging import LOGGER


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(
        f"{SETTINGS.WEB_SERVER_HOST}{SETTINGS.WEBHOOK_PATH}",
        certificate=FSInputFile(SETTINGS.WEBHOOK_SSL_CERT),
        secret_token=SETTINGS.WEBHOOK_SECRET,
    )


def start_web_app(dp: Dispatcher, bot: Bot):
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Create aiohttp.web.Application instance
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=SETTINGS.WEBHOOK_SECRET
    )

    # Register webhook handler on application
    webhook_requests_handler.register(app, path=SETTINGS.WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(
        app,
        host=SETTINGS.WEB_SERVER_HOST,
        port=SETTINGS.WEB_SERVER_PORT,
    )


async def main():
    LOGGER.info("Bot is started")

    bot = Bot(token=SETTINGS.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(*ROUTERS)

    if SETTINGS.ENVIRONMENT == Environment.PRODUCTION:
        start_web_app(dp, bot)
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
