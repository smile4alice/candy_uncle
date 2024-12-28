import re
from dataclasses import dataclass
from typing import Optional

import httpx
import requests
from aiogram.types import (
    BufferedInputFile,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)


@dataclass
class InstagramServiceDTO:
    media: list[InputMedia] | str = None  # type: ignore
    channel_url: str = None  # type: ignore
    is_photo: bool = False  # type: ignore
    is_video: bool = False  # type: ignore
    is_sidecar: bool = False  # type: ignore
    is_text: bool = False  # type: ignore


class InstagramService:
    temp_directory = "static"

    async def get_post_media(self, message: Message) -> InstagramServiceDTO:
        shortcode = self._get_shortcode(message.text)
        return await self._get_media_from_shortcode(message, shortcode, message.chat.id)

    def _get_shortcode(self, text):
        result = re.findall(r"(?:reel\/|p\/)([^\s\/]+)", text)
        if result:
            return result[0]

    async def _get_media_from_shortcode(self, message, shortcode, chat_id: int):
        post = await self.get_rapid_data(shortcode)

        output_data = InstagramServiceDTO()
        if post["__typename"] == "GraphVideo":
            output_data.media = post["video_url"]
            if 20 <= self._get_size(output_data.media) <= 50:
                output_data.is_video = True
                output_data.media = self._get_media2buffer_from_url(output_data.media)  # type: ignore
            elif self._get_size(output_data.media) <= 20:
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
                    if self._get_size(video_url) <= 50:
                        media = InputMediaVideo(
                            media=self._get_media2buffer_from_url(video_url),
                            supports_streaming=True,
                        )
                    else:
                        oversize.append(item["node"]["video_url"])
                        continue
                else:
                    media = InputMediaPhoto(media=item["node"]["display_url"])  # type: ignore

                output_data.media.append(media)

            if oversize:
                await message.bot.send_message(
                    chat_id=chat_id, text="\n".join(oversize)
                )

        return output_data

    async def get_rapid_data(self, shortcode):
        url = "https://instagram-looter2.p.rapidapi.com/post"
        querystring = {"link": f"https://www.instagram.com/p/{shortcode}/"}

        headers = {
            "X-RapidAPI-Key": "ee65df8621msh404447f5956604bp116883jsnd63366cc8a65",  # syniava
            # "X-RapidAPI-Key": "e27930093fmsh6d68b5601ab4285p1b3dd8jsn14ddb0e4702b", # smile
            "X-RapidAPI-Host": "instagram-looter2.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers, params=querystring)
        # with open("static/instad.py", "w", encoding="utf-8") as f:
        #     f.write(response.json().__str__())
        return response.json()

    @staticmethod
    def _get_size(url):
        try:
            response = requests.head(url)
            content_length = response.headers.get("Content-Length")
            if content_length:
                size_in_bytes = int(content_length)
                size_in_mb = size_in_bytes / (1024 * 1024)
                return size_in_mb
        except Exception:
            print("Failed to get video size.")

    @staticmethod
    def _get_media2buffer_from_url(url: str) -> BufferedInputFile:
        response = requests.get(url)
        return BufferedInputFile(response.content, "outputmedia")


@dataclass
class InstagramPostDTO:
    media: list[InputMedia] | str | None = None
    caption: Optional[str] = None
    is_video: bool = False
    is_photo: bool = False
    is_carousel: bool = False
    is_text: bool = False
    is_sidecar: bool = False
    error: Optional[str] = None


class InstagramServiceV2:
    """Improved Instagram service using new RapidAPI endpoint."""

    def __init__(self):
        self.api_url = "https://instagram-scraper-api2.p.rapidapi.com/v1/post_info"
        self.headers = {
            "x-rapidapi-key": "e27930093fmsh6d68b5601ab4285p1b3dd8jsn14ddb0e4702b",
            "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com",
        }

    def _sanitize_url(self, url: str) -> str:
        """Extract and sanitize Instagram URL from text."""
        instagram_pattern = r"https?://(?:www\.)?instagram\.com/[^\s]+"
        match = re.search(instagram_pattern, url)

        if not match:
            raise ValueError("No Instagram URL found in the text")

        instagram_url = match.group(0)
        return instagram_url

    async def get_post_media(self, message: Message) -> InstagramPostDTO:
        """Main method to process Instagram post and extract media."""
        try:
            post_url = message.text
            post_data = await self._fetch_post_data(post_url)  # type: ignore

            if not post_data:
                return InstagramPostDTO(error="Failed to fetch post data")

            return await self._process_post_data(post_data, message.chat.id)

        except Exception as e:
            print(f"Error processing Instagram post: {e}")
            return InstagramPostDTO(error="Failed to process Instagram post")

    async def _fetch_post_data(self, post_url: str) -> dict:
        """Fetch post data from Instagram API."""
        try:
            params = {
                "code_or_id_or_url": post_url,
                "include_insights": "false",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.api_url, headers=self.headers, params=params
                )
                response.raise_for_status()
                return response.json().get("data", {})

        except Exception as e:
            print(f"Error fetching post data: {e}")
            return {}

    async def _process_post_data(
        self, post_data: dict, chat_id: int
    ) -> InstagramPostDTO:
        """Process post data and extract media content."""
        output = InstagramPostDTO()

        try:
            # Set caption if available
            if caption_data := post_data.get("caption", {}):
                output.caption = caption_data.get("text")

            # Process based on media type
            media_type = post_data.get("media_type")

            if media_type == 2:  # Video
                return await self._process_video(post_data)
            elif media_type == 1:  # Photo
                return self._process_photo(post_data)
            elif media_type == 8:  # Carousel
                return await self._process_carousel(post_data, chat_id)

            return InstagramPostDTO(error="Unsupported media type")

        except Exception as e:
            print(f"Error processing post data: {e}")
            return InstagramPostDTO(error="Failed to process post data")

    async def _process_video(self, post_data: dict) -> InstagramPostDTO:
        """Process video post."""
        output = InstagramPostDTO(is_video=True)

        video_url = post_data.get("video_url")
        if not video_url:
            return InstagramPostDTO(error="Video URL not found")

        size_mb = await self._get_file_size(video_url)

        if size_mb <= 20:
            output.media = video_url
        elif 20 < size_mb <= 50:
            output.media = await self._url_to_buffer(video_url)  # type: ignore
        else:
            output.is_text = True
            output.media = video_url

        return output

    def _process_photo(self, post_data: dict) -> InstagramPostDTO:
        """Process photo post."""
        output = InstagramPostDTO(is_photo=True)

        if display_url := post_data.get("thumbnail_url"):
            output.media = display_url
        else:
            output.error = "Photo URL not found"

        return output

    async def _process_carousel(
        self, post_data: dict, chat_id: int
    ) -> InstagramPostDTO:
        """Process carousel/album post."""
        output = InstagramPostDTO(is_carousel=True, is_sidecar=True, media=[])
        oversize_videos = []

        carousel_media = post_data.get("carousel_media", [])

        for item in carousel_media:
            if item.get("media_type") == 2:  # Video
                video_url = item.get("video_url")
                if not video_url:
                    continue

                size_mb = await self._get_file_size(video_url)

                if size_mb <= 50:
                    media = InputMediaVideo(
                        media=await self._url_to_buffer(video_url),
                        supports_streaming=True,
                    )
                    output.media.append(media)  # type: ignore
                else:
                    oversize_videos.append(video_url)
                    continue

            elif item.get("media_type") == 1:  # Photo
                if photo_url := item.get("thumbnail_url"):
                    media = InputMediaPhoto(media=photo_url)  # type: ignore
                    output.media.append(media)

        # If there are large videos - add them as text
        if oversize_videos:
            output.is_text = True
            output.media = "\n".join(oversize_videos)

        return output

    @staticmethod
    async def _get_file_size(url: str) -> float:
        """Get file size in MB from URL."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url)
                if content_length := response.headers.get("content-length"):
                    return int(content_length) / (1024 * 1024)
            return 0
        except Exception as e:
            print(f"Error getting file size: {e}")
            return 0

    @staticmethod
    async def _url_to_buffer(url: str) -> BufferedInputFile:
        """Convert URL to BufferedInputFile."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return BufferedInputFile(response.content, "media_file")
