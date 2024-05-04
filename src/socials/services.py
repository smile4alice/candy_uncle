import re
from dataclasses import dataclass

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
            print("Не вдалося отримати розмір відео.")

    @staticmethod
    def _get_media2buffer_from_url(url: str) -> BufferedInputFile:
        response = requests.get(url)
        return BufferedInputFile(response.content, "outputmedia")
