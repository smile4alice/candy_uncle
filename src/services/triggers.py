from re import findall
from typing import Iterator

from sqlalchemy import delete, select

from src.database import session_factory
from src.enums import MatchTypeEnum
from src.exceptions import InvalidCommandError
from src.lib import INVALID_COMMAND, SERVER_ERROR
from src.logging import LOGGER
from src.models import Trigger


class TriggersService:
    @staticmethod
    async def detect_trigger(text: str, chat_id: int) -> Iterator[Trigger] | None:
        results: Iterator[Trigger] | None = None
        try:
            # TODO caching with redis
            async with session_factory() as session:
                query = select(Trigger).filter_by(is_active=True, chat_id=chat_id)
                result = await session.execute(query)
                records = result.scalars().all()
            if records:
                results = filter(
                    lambda record: (
                        (
                            record.match_type == MatchTypeEnum.text
                            and record.trigger in text
                        )
                        or findall(record.trigger, text.lower())
                    ),
                    records,
                )
            return results
        except Exception as e:
            LOGGER.exception(e)
            return None

    @classmethod
    async def get_answer(cls, text: str, chat_id: int):
        await cls.detect_trigger(text=text, chat_id=chat_id)
        return "Not Implemented."

    @staticmethod
    async def update_or_add_trigger(text: str, chat_id: int) -> str:
        try:
            data: list = findall(
                r"(?<=\/update_trigger)\s*(\S+)\s*(.+[^regex])\s*(regex$)?", text
            )
            if data:
                trigger, name, regex = data[0]
                if regex:
                    match_type = MatchTypeEnum.regex
                else:
                    match_type = MatchTypeEnum.text
            else:
                response = (
                    INVALID_COMMAND
                    % 'Trigger update <name> <trigger> <"regex" if regex_mode>'
                )
                return response
            async with session_factory() as session:
                query = select(Trigger).filter_by(trigger=trigger, chat_id=chat_id)
                result = await session.execute(query)
                instance = result.scalar_one_or_none()
                if instance:
                    instance.trigger = trigger
                    instance.match_type = match_type

                else:
                    instance = Trigger(
                        name=name,
                        trigger=trigger,
                        match_type=match_type,
                        chat_id=chat_id,
                    )
                    session.add(instance)
                await session.commit()
                return f"sucessfully updated name: {name} trigger: {trigger}"
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def delete_trigger(text: str, chat_id: int) -> str:
        try:
            command_data = text.lower().split()
            if len(command_data) < 2:
                example = "delete_trigger trigger"
                raise InvalidCommandError(example=example)
            else:
                trigger_name = command_data[1]

            async with session_factory() as session:
                query = delete(Trigger).filter_by(
                    trigger_name=trigger_name, chat_id=chat_id
                )
                result = await session.execute(query)
                rowcount = result.rowcount
                await session.commit()
            if rowcount:
                response = f"{trigger_name} trigger successfully delete."
            else:
                response = f"{trigger_name} not found."
            return response
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR
