"""YouTube services."""

import asyncio
import re
import tempfile
import os
from datetime import datetime
from html import escape
from typing import Optional, Dict, Any

from aiogram.types import BufferedInputFile, Message
import yt_dlp

from app.common.logging import logger
from app.config import settings
from app.features.youtube.schemas import YouTubeServiceDTO, MediaType


# YouTube service constants
YOUTUBE_MAX_DURATION = 600  # 10 minutes in seconds
YOUTUBE_MAX_FILE_SIZE = 50  # 50MB in MB (Telegram bot limit)


class YouTubeService:
    """Service for handling YouTube downloads."""

    def __init__(self, message: Message) -> None:
        """
        Initialize YouTube service with message data.

        :param message: Telegram message object containing YouTube URL
        """
        self.message = message
        self.chat_id = message.chat.id
        self.text = message.text or ""
        self.url = self._extract_url(self.text)

    async def process_youtube_content(self) -> None:
        """Main method to process YouTube content."""
        await self._process_video()

    async def _process_video(self) -> None:
        """Process single video download."""
        await self.message.bot.send_chat_action(chat_id=self.chat_id, action="upload_video")

        # Run YouTube operations in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        service_output = await loop.run_in_executor(None, self._download_video)

        if service_output.error_message:
            # Log the error and send to superuser only
            logger.warning(f"YouTube download failed: {service_output.error_message}")

            # Send error details to superuser
            error_details = (
                f"🚨 <b>YouTube Download Failed</b>\n\n"
                f"<b>URL:</b> <code>{self.url}</code>\n"
                f"<b>Error:</b> {service_output.error_message}\n"
                f"<b>Chat ID:</b> {self.chat_id}\n"
                f"<b>User ID:</b> {self.message.from_user.id if self.message.from_user else 'Unknown'}"
            )

            try:
                await self.message.bot.send_message(
                    chat_id=settings.SUPERUSER_ID, text=error_details, parse_mode="HTML"
                )
            except Exception as e:
                logger.exception(f"Failed to send error to superuser: {e}")

            return

        if service_output.media_type == MediaType.VIDEO:
            # Send as video with preview for better UX
            await self.message.reply_video(
                video=service_output.media,
                caption=self._format_video_caption(service_output),
                parse_mode="HTML",
                supports_streaming=True,
            )
        elif service_output.media_type == MediaType.AUDIO:
            await self.message.reply_audio(
                audio=service_output.media,
                caption=self._format_audio_caption(service_output),
                parse_mode="HTML",
            )

    def _download_video(self) -> YouTubeServiceDTO:
        """
        Download YouTube video using yt-dlp with automatic quality degradation.

        :return: YouTubeServiceDTO with download results
        """
        output_data = YouTubeServiceDTO()

        try:
            # First, get video info
            info = self._get_video_info()
            if not info:
                output_data.error_message = "Failed to get video information."
                return output_data

            # Extract video info
            output_data.title = info.get("title", "Unknown")
            output_data.duration = info.get("duration", 0)
            output_data.views = info.get("view_count", 0)
            output_data.upload_date = info.get("upload_date")

            # Determine if it's a short
            if "/shorts/" in self.url or output_data.duration and output_data.duration <= 60:
                output_data.media_type = MediaType.SHORTS

            # Check if video is too long
            if output_data.duration and output_data.duration > YOUTUBE_MAX_DURATION:
                max_minutes = YOUTUBE_MAX_DURATION // 60
                output_data.error_message = (
                    f"Video too long ({self._format_duration(output_data.duration)}). "
                    f"Maximum duration is {max_minutes} minutes. Skipping download."
                )
                return output_data

            # Try video download with quality degradation
            video_result = self._try_video_download_with_ytdlp(info)
            if video_result:
                return video_result

            # Fallback to audio download
            audio_result = self._try_audio_download_with_ytdlp(info)
            if audio_result:
                return audio_result

            output_data.error_message = "No suitable streams found for download."

        except Exception as e:
            error_msg = str(e)
            logger.error(f"YouTube download error: {error_msg}")

            # Handle specific yt-dlp errors
            if "Video unavailable" in error_msg:
                output_data.error_message = "Video is unavailable or private."
            elif "Private video" in error_msg:
                output_data.error_message = "Video is private."
            elif "Video unavailable" in error_msg:
                output_data.error_message = "Video not found or has been removed."
            elif "Sign in to confirm your age" in error_msg:
                output_data.error_message = "Video requires age verification."
            else:
                output_data.error_message = f"Download failed: {error_msg}"

        return output_data

    def _get_video_info(self) -> Optional[Dict[str, Any]]:
        """
        Get video information using yt-dlp.

        :return: Video info dictionary or None if failed
        """
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                return info
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None

    def _try_video_download_with_ytdlp(self, info: Dict[str, Any]) -> Optional[YouTubeServiceDTO]:
        """
        Try video download using yt-dlp with quality degradation.

        :param info: Video info dictionary
        :return: YouTubeServiceDTO if successful, None otherwise
        """
        # Any format under 50MB
        quality_levels = [
            {"format": "best[filesize<50M][ext=mp4]/best[filesize<50M]/best[ext=mp4]/best"},
        ]

        for quality in quality_levels:
            try:
                output_data = YouTubeServiceDTO()
                output_data.title = info.get("title", "Unknown")
                output_data.duration = info.get("duration", 0)
                output_data.views = info.get("view_count", 0)
                output_data.upload_date = info.get("upload_date")
                output_data.media_type = MediaType.VIDEO

                # Download with current quality
                media_file = self._download_with_ytdlp(quality["format"])
                if media_file:
                    output_data.media = media_file
                    # Clean quality string to avoid HTML parsing issues
                    quality_str = quality["format"].replace("[", "").replace("]", "").replace("<=", "≤")
                    output_data.quality = f"Video ({quality_str})"
                    return output_data

            except Exception as e:
                logger.debug(f"Failed to download video with quality {quality}: {e}")
                continue

        return None

    def _try_audio_download_with_ytdlp(self, info: Dict[str, Any]) -> Optional[YouTubeServiceDTO]:
        """
        Try audio download using yt-dlp.

        :param info: Video info dictionary
        :return: YouTubeServiceDTO if successful, None otherwise
        """
        try:
            output_data = YouTubeServiceDTO()
            output_data.title = info.get("title", "Unknown")
            output_data.duration = info.get("duration", 0)
            output_data.views = info.get("view_count", 0)
            output_data.upload_date = info.get("upload_date")
            output_data.media_type = MediaType.AUDIO

            # Download audio with size limit
            media_file = self._download_with_ytdlp(
                "bestaudio[filesize<50M][ext=m4a]/bestaudio[filesize<50M]/bestaudio[ext=m4a]/bestaudio"
            )
            if media_file:
                output_data.media = media_file
                output_data.quality = "Audio (m4a/mp3)"
                return output_data

        except Exception as e:
            logger.debug(f"Failed to download audio: {e}")

        return None

    def _download_with_ytdlp(self, format_selector: str) -> Optional[BufferedInputFile]:
        """
        Download media using yt-dlp with specified format.

        :param format_selector: Format selector for yt-dlp
        :return: BufferedInputFile if successful, None otherwise
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                ydl_opts = {
                    "format": format_selector,
                    "outtmpl": f"{temp_dir}/%(title)s.%(ext)s",
                    "quiet": True,
                    "no_warnings": True,
                    "max_filesize": YOUTUBE_MAX_FILE_SIZE * 1024 * 1024,  # Convert MB to bytes
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url])

                # Find the downloaded file
                files = os.listdir(temp_dir)
                if files:
                    file_path = os.path.join(temp_dir, files[0])

                    # Read file content
                    with open(file_path, "rb") as f:
                        content = f.read()

                    # Determine file extension
                    file_ext = os.path.splitext(files[0])[1][1:]  # Remove the dot
                    filename = f"youtube_media.{file_ext}"

                    return BufferedInputFile(content, filename)

            except Exception as e:
                logger.error(f"Failed to download with yt-dlp: {e}")
                return None

    def _extract_url(self, text: str) -> str:
        """
        Extract YouTube URL from text.

        :param text: Text containing YouTube URL
        :return: Clean YouTube URL
        """
        # Remove any extra text and get the URL
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, text)

        for url in urls:
            if "youtube.com" in url or "youtu.be" in url:
                # Remove any query parameters after the video ID for shorts
                if "/shorts/" in url:
                    return url.split("?")[0]
                return url

        return text.strip()

    def _format_duration(self, seconds: int) -> str:
        """
        Format duration in seconds to MM:SS or HH:MM:SS format.

        :param seconds: Duration in seconds
        :return: Formatted duration string
        """
        if seconds < 3600:  # Less than 1 hour
            minutes, secs = divmod(seconds, 60)
            return f"{minutes}:{secs:02d}"
        else:  # 1 hour or more
            hours, remainder = divmod(seconds, 3600)
            minutes, secs = divmod(remainder, 60)
            return f"{hours}:{minutes:02d}:{secs:02d}"

    def _format_video_caption(self, data: YouTubeServiceDTO) -> str:
        """Format video caption with HTML escaping."""
        caption = f"🎥 <b>{escape(data.title)}</b>\n"
        if data.views:
            caption += f"👀 <b>Views:</b> {data.views:,}\n"

        # Add upload date from video info
        if hasattr(data, "upload_date") and data.upload_date:
            upload_date = datetime.strptime(data.upload_date, "%Y%m%d").strftime("%Y-%m-%d")
            caption += f"📅 <b>Uploaded:</b> {upload_date}"

        return caption

    def _format_audio_caption(self, data: YouTubeServiceDTO) -> str:
        """Format audio caption with HTML escaping."""
        caption = f"🎵 <b>{escape(data.title)}</b>\n"
        if data.views:
            caption += f"👀 <b>Views:</b> {data.views:,}\n"

        # Add upload date from video info
        if hasattr(data, "upload_date") and data.upload_date:
            upload_date = datetime.strptime(data.upload_date, "%Y%m%d").strftime("%Y-%m-%d")
            caption += f"📅 <b>Uploaded:</b> {upload_date}"

        return caption
