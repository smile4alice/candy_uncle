from aiogram import F, Router
from aiogram.types import Message

from src.lib import SERVER_ERROR
from src.logging import LOGGER
from src.socials.filters import IsInstagram
from src.socials.services import InstagramServiceV2


socials_router: Router = Router()


# INSTAGRAM DOWNLOAD VIDEO
@socials_router.message(F.text, IsInstagram())
async def process_instagram_download(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
    serv = InstagramServiceV2()
    try:
        serv_output = await serv.get_post_media(message)
        if serv_output.is_video:
            await message.reply_video(video=serv_output.media, supports_streaming=True)  # type: ignore
        elif serv_output.is_photo:
            await message.bot.send_chat_action(
                chat_id=message.chat.id, action="upload_photo"
            )
            await message.reply_photo(photo=serv_output.media)  # type: ignore
        elif serv_output.is_sidecar:
            await message.reply_media_group(media=serv_output.media)  # type: ignore
        elif serv_output.is_text:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            await message.reply(text=serv_output.media)  # type: ignore

    except Exception as exc:
        LOGGER.exception(exc)
        message = await message.reply(text=SERVER_ERROR)
