from enum import Enum


class Environment(Enum):
    TESTING = "TESTING"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class MediaTypeEnum(Enum):
    TEXT = "text"
    PHOTO = "photo"
    ANIMATION = "animation"
    STICKER = "sticker"
    VIDEO = "video"
    VOICE = "voice"
    AUDIO = "audio"


class MatchModeEnum(Enum):
    text = "text"
    regex = "regex"
