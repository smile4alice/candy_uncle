"""Instagram services."""

import re

import httpx
from aiogram.types import (
    BufferedInputFile,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)

from app.config import settings
from app.common.exceptions import InstagramAPIError
from app.features.instagram.schemas import InstagramServiceDTO


class InstagramService:
    def __init__(self, message: Message) -> None:
        """
        Initialize Instagram service with message data.
        
        :param message: Telegram message object containing Instagram URL
        """
        self.message = message
        self.chat_id = message.chat.id
        self.text = message.text or ""
        self.shortcode = self._get_shortcode(self.text)

    async def process_instagram_content(self) -> None:
        """Main method to process Instagram content."""
        await self.message.bot.send_chat_action(chat_id=self.chat_id, action="upload_video")
        
        serv_output = await self._get_media_from_shortcode()
        
        if serv_output.is_video:
            await self.message.reply_video(video=serv_output.media, supports_streaming=True)
        elif serv_output.is_photo:
            await self.message.bot.send_chat_action(chat_id=self.chat_id, action="upload_photo")
            await self.message.reply_photo(photo=serv_output.media)
        elif serv_output.is_sidecar:
            await self.message.reply_media_group(media=serv_output.media)
        elif serv_output.is_text:
            await self.message.bot.send_chat_action(chat_id=self.chat_id, action="typing")
            await self.message.reply(text=serv_output.media)

    def _get_shortcode(self, text: str) -> str | None:
        """
        Extract Instagram shortcode from URL.
        
        :param text: Text containing Instagram URL
        :return: Instagram shortcode or None if not found
        """
        result = re.findall(r"(?:reel\/|p\/)([^\s\/]+)", text)
        if result:
            return result[0]
        return None

    async def _get_media_from_shortcode(self):
        post = await self.get_rapid_data(self.shortcode)

        output_data = InstagramServiceDTO()
        if post["__typename"] == "GraphVideo":
            output_data.media = post["video_url"]
            if 20 <= await self._get_size(output_data.media) <= 50:
                output_data.is_video = True
                output_data.media = await self._get_media2buffer_from_url(output_data.media)
            elif await self._get_size(output_data.media) <= 20:
                output_data.is_video = True
            else:
                output_data.is_text = True
        elif post["__typename"] == "GraphImage":
            output_data.media = post["display_url"]
            output_data.is_photo = True

        elif post["__typename"] == "GraphSidecar":
            output_data.is_sidecar = True
            output_data.media = list()

            oversize = list()

            for item in post["edge_sidecar_to_children"]["edges"]:
                if item["node"]["is_video"]:
                    video_url = item["node"]["video_url"]
                    if await self._get_size(video_url) <= 50:
                        media = InputMediaVideo(
                            media=await self._get_media2buffer_from_url(video_url),
                            supports_streaming=True,
                        )
                    else:
                        oversize.append(item["node"]["video_url"])
                        continue
                else:
                    media = InputMediaPhoto(media=item["node"]["display_url"])

                output_data.media.append(media)

            if oversize:
                await self.message.bot.send_message(
                    chat_id=self.chat_id, text="\n".join(oversize)
                )

        return output_data

    async def get_rapid_data(self, shortcode: str) -> dict:
        """
        Fetch Instagram post data from RapidAPI.
        
        :param shortcode: Instagram post shortcode
        :return: Instagram post data dictionary
        :raises InstagramAPIError: When API request fails
        """
        url = "https://instagram-looter2.p.rapidapi.com/post"
        querystring = {"link": f"https://www.instagram.com/p/{shortcode}/"}

        headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "instagram-looter2.p.rapidapi.com",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=querystring)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise InstagramAPIError(f"Instagram API request failed: {e}")

    @staticmethod
    async def _get_size(url: str) -> float | None:
        """
        Get file size from URL in MB.
        
        :param url: File URL
        :return: File size in MB or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url)
                content_length = response.headers.get("Content-Length")
                if content_length:
                    size_in_bytes = int(content_length)
                    size_in_mb = size_in_bytes / (1024 * 1024)
                    return size_in_mb
        except Exception:
            print("Не вдалося отримати розмір відео.")
        return None

    @staticmethod
    async def _get_media2buffer_from_url(url: str) -> BufferedInputFile:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return BufferedInputFile(response.content, "outputmedia")
