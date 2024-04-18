from re import findall

from src.enums import MatchModeEnum, MediaTypeEnum
from src.exceptions import InvalidCommandError, RecordsNotFoundError
from src.lib import SERVER_ERROR
from src.logging import LOGGER

from .lib import NOT_FOUND_EVENT, NOT_FOUND_TRIGGERS
from .models import Trigger, TriggerEvent
from .repository import TriggerEventORM, TriggerORM


class TriggerEventService:
    @staticmethod
    async def detect_triggers(text: str, chat_id: int) -> bool:
        try:
            record = await TriggerEventORM.search_triggers_in_text(text, chat_id)
            return bool(record)
        except Exception as e:
            LOGGER.exception(e)
            return False

    @staticmethod
    async def put_trigger_event(text: str, chat_id: int) -> str:
        try:
            command_data = findall(r"\S+\s+(\S+)\s+(.+[^\sregex])\s*(regex$)?", text)
            if command_data:
                name, event, is_regex = command_data[0]
                match_mode = MatchModeEnum.regex if is_regex else MatchModeEnum.text
            else:
                example = '<code>/put_trigger_event [name] [trigger] ["regex" if regex_mode]</code>'
                raise InvalidCommandError(example=example)
            await TriggerEventORM.create_or_update_by_name(
                name=name,
                chat_id=chat_id,
                event=event,
                match_mode=match_mode,
            )
            return f"☑️put <code>{name}</code>: <code>{event}</code>"
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def delete_trigger_event(text: str, chat_id: int) -> str:
        try:
            command_data = text.lower().split()
            if len(command_data) < 2:
                example = "delete_trigger_event trigger"
                raise InvalidCommandError(example=example)
            else:
                name = command_data[1]
            result = await TriggerEventORM.delete_by_name(name, chat_id)
            if result:
                return f"☑️delete: <code>{name}</code>"
            else:
                raise RecordsNotFoundError(NOT_FOUND_EVENT % name)
        except InvalidCommandError as e:
            return str(e)
        except RecordsNotFoundError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR


class TriggerService:
    @staticmethod
    async def get_trigger(text: str, chat_id: int) -> Trigger | str:
        try:
            trigger_event = await TriggerEventORM.search_triggers_in_text(text, chat_id)
            trigger = await TriggerORM.get_random_active_by_event_id(trigger_event.id)
            if trigger:
                return trigger
            else:
                raise RecordsNotFoundError(NOT_FOUND_TRIGGERS % trigger_event.name)
        except RecordsNotFoundError as e:
            msg = str(e)
            LOGGER.warning(msg)
            return msg
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def get_trigger_event_from_command(
        text: str, chat_id: int
    ) -> TriggerEvent | str:
        try:
            command_data = text.split()
            if len(command_data) < 2:
                raise InvalidCommandError(
                    example="<code>/command [trigger_event]</code>"
                )
            else:
                trigger_event = command_data[1]
                trigger_event_record = await TriggerEventORM.get_one_by_name(
                    name=trigger_event,
                    chat_id=chat_id,
                    only_active=False,
                )
                if trigger_event_record:
                    return trigger_event_record
                else:
                    raise RecordsNotFoundError(NOT_FOUND_EVENT % trigger_event)
        except InvalidCommandError as e:
            return str(e)
        except RecordsNotFoundError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def put_trigger(
        chat_id: int,
        media_type: MediaTypeEnum,
        media: str,
        state_data: dict,
    ) -> str:
        try:
            trigger_event = state_data["trigger_event"]
            await TriggerORM.update_by_id_or_create(
                trigger_event=trigger_event,
                chat_id=chat_id,
                media_type=media_type,
                media=media,
            )
            text = f"☑️put <code>{trigger_event}</code>"
            return text
        except RecordsNotFoundError as e:
            msg = str(e)
            LOGGER.warning(msg)
            return msg
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR
