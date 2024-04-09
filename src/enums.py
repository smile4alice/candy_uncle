from enum import Enum


class Environment(Enum):
    TESTING = "TESTING"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class MediaTypeEnum(Enum):
    TEXT = "text"
    PHOTO = "photo"
    ANIMATION = "animation"
    VIDEO = "video"
    VOICE = "voice"
    AUDIO = "audio"


class MatchTypeEnum(Enum):
    text = "text"
    regex = "regex"
