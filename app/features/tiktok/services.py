"""TikTok services."""

import re

import httpx
from aiogram.types import BufferedInputFile, Message

from app.config import settings
from app.common.exceptions import TikTokAPIError
from app.features.tiktok.schemas import TikTokServiceDTO


class TikTokService:
    def __init__(self, message: Message):
        self.message = message
        self.chat_id = message.chat.id
        self.text = message.text or ""
        self.video_id = self._get_video_id(self.text)

    async def process_tiktok_content(self) -> None:
        """Main method to process TikTok content."""
        await self.message.bot.send_chat_action(chat_id=self.chat_id, action="upload_video")
        
        serv_output = await self._get_media_from_video_id()
        
        if serv_output.is_video:
            await self.message.reply_video(video=serv_output.media, supports_streaming=True)
        elif serv_output.is_text:
            await self.message.bot.send_chat_action(chat_id=self.chat_id, action="typing")
            await self.message.reply(text=serv_output.media)

    def _get_video_id(self, text: str) -> str | None:
        """
        Extract TikTok video ID from URL.
        
        :param text: Text containing TikTok URL
        :return: TikTok video ID or None if not found
        """
        # TikTok URL patterns: https://www.tiktok.com/@username/video/1234567890
        # or https://vm.tiktok.com/xxxxx
        result = re.findall(r"(?:tiktok\.com\/@[\w\.]+\/video\/|vm\.tiktok\.com\/)([^\s\/\?]+)", text)
        if result:
            return result[0]
        return None

    async def _get_media_from_video_id(self):
        video_data = await self.get_tiktok_data(self.video_id)
        
        output_data = TikTokServiceDTO()
        if video_data and "video_url" in video_data:
            output_data.media = video_data["video_url"]
            if await self._get_size(output_data.media) <= 50:
                output_data.is_video = True
                output_data.media = await self._get_media2buffer_from_url(output_data.media)
            else:
                output_data.is_text = True
                output_data.media = f"Video too large. Direct link: {video_data['video_url']}"
        else:
            output_data.is_text = True
            output_data.media = "Could not download TikTok video"
        
        return output_data

    async def get_tiktok_data(self, video_id: str) -> dict | None:
        """
        Fetch TikTok video data from API.
        
        :param video_id: TikTok video ID
        :return: TikTok video data dictionary or None if failed
        :raises TikTokAPIError: When API request fails
        """
        # Using RapidAPI TikTok service
        url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
        params = {"url": f"https://www.tiktok.com/@user/video/{video_id}"}
        headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                if data.get("code") == 0:  # Success response
                    return {
                        "video_url": data.get("data", {}).get("play"),
                        "title": data.get("data", {}).get("title", ""),
                        "author": data.get("data", {}).get("author", {})
                    }
        except httpx.RequestError as e:
            raise TikTokAPIError(f"TikTok API request failed: {e}")
        
        return None

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
