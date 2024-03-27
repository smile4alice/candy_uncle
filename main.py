import asyncio
import ssl

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src import BOT, settings
from src.routers import ROUTERS


async def on_startup(bot: Bot) -> None:
    # In case when you have a self-signed SSL certificate, you need to send the certificate
    # itself to Telegram servers for validation purposes
    # (see https://core.telegram.org/bots/self-signed)
    # But if you have a valid SSL certificate, you SHOULD NOT send it to Telegram servers.
    await bot.set_webhook(
        f"{settings.BASE_URL}{settings.WEBHOOK_PATH}",
        certificate=FSInputFile(settings.webhook_ssl_cert),
        secret_token=settings.WEBHOOK_SECRET,
    )


async def start_web_app(dp: Dispatcher, bot: Bot):
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=settings.WEBHOOK_SECRET
    )

    # Register webhook handler on application
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # Generate SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(settings.webhook_ssl_cert, settings.webhook_ssl_priv)

    # And finally start webserver
    web.run_app(
        app,
        host=settings.WEB_SERVER_HOST,
        port=settings.WEB_SERVER_PORT,
        ssl_context=context,
    )


async def main():
    print("Bot is started")

    dp = Dispatcher()

    dp.include_routers(*ROUTERS)

    if settings.IS_PROD:
        await start_web_app(dp, BOT)
    else:
        await dp.start_polling(BOT)


if __name__ == "__main__":
    asyncio.run(main())
