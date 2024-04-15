from re import findall
from typing import Sequence

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import session_factory
from src.enums import MatchTypeEnum, MediaTypeEnum
from src.exceptions import InvalidCommandError, RecordsNotFound
from src.lib import SERVER_ERROR
from src.logging import LOGGER
from src.models import Trigger, TriggerAnswer


class TriggerEventORM:
    pass  # TODO


class TriggerEventService:
    @staticmethod
    async def detect_triggers(text: str, chat_id: int) -> Trigger | None:
        try:
            async with session_factory() as session:
                query = select(Trigger).filter_by(is_active=True, chat_id=chat_id)
                result = await session.execute(query)
                records = result.scalars().all()
            if records:
                records_in_text = filter(
                    lambda record: (
                        (
                            record.match_type == MatchTypeEnum.text
                            and record.trigger in text
                        )
                        or findall(record.trigger, text.lower())
                    ),
                    records,
                )
                return next(records_in_text, None)
            else:
                return None
        except Exception as e:
            LOGGER.exception(e)
            return None

    @staticmethod
    async def put_trigger_event(text: str, chat_id: int) -> str:
        try:
            command_data: list = findall(
                r"\S+\s+(\S+)\s+(.+[^\sregex])\s*(regex$)?", text
            )
            if command_data:
                name, trigger, is_regex = command_data[0]
                match_type = MatchTypeEnum.regex if is_regex else MatchTypeEnum.text
            else:
                raise InvalidCommandError(
                    example='`/triggers_put <name> <trigger> <"regex" if regex_mode>`'
                )

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
                raise InvalidCommandError(example="delete_trigger trigger")
            else:
                trigger_name = command_data[1]
            async with session_factory() as session:
                query = delete(Trigger).filter_by(
                    trigger_name=trigger_name, chat_id=chat_id
                )
                result = await session.execute(query)
                await session.commit()
            if result.rowcount:
                response = f"{trigger_name} trigger successfully delete."
            else:
                response = f"{trigger_name} not found."
            return response
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR


class TriggerAnswerORM:
    pass  # TODO


class TriggerAnswerService:
    @staticmethod
    async def get_answer(text: str, chat_id: int) -> TriggerAnswer | str:
        trigger = await TriggerEventService.detect_triggers(text=text, chat_id=chat_id)
        random_answer_query = (
            select(TriggerAnswer)
            .filter_by(is_active=True, trigger_id=trigger.id)
            .order_by(func.random())
            .limit(1)
        )
        try:
            async with session_factory() as session:
                result = await session.execute(random_answer_query)
                record = result.scalar_one_or_none()
                if not record:
                    query = (
                        update(TriggerAnswer)
                        .filter_by(trigger_id=trigger.id)
                        .values(is_active=True)
                    )
                    await session.execute(query)
                    result = await session.execute(random_answer_query)
                    record = result.scalar_one_or_none()
                if record:
                    record.is_active = False
                    await session.commit()
                    return record
                else:
                    raise RecordsNotFound
        except RecordsNotFound as e:
            msg = str(e)
            LOGGER.warning(msg)
            return msg
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @classmethod
    async def put_answer(
        cls, trigger_name: str, chat_id: int, media_type: MediaTypeEnum, media: str
    ) -> str:
        try:
            async with session_factory() as session:
                trigger_instance = await cls._get_trigger_by_name(
                    session=session, name=trigger_name, chat_id=chat_id
                )
                if not trigger_instance:
                    raise RecordsNotFound(
                        message=f'No records were found matching the value "{trigger_name}"'
                    )
                else:
                    answer_instance = TriggerAnswer(
                        media_type=media_type,
                        answer=media,
                        trigger_id=trigger_instance.id,
                    )
                    session.add(answer_instance)
                await session.commit()
                text = "☑️put:\n" + f"#{answer_instance.id} `{answer_instance.answer}`"
                return text
        except RecordsNotFound as e:
            msg = str(e)
            LOGGER.warning(msg)
            return msg
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @classmethod
    async def get_count_answer_by_type(
        cls, trigger_name: str, chat_id: int, media_type: str
    ) -> int | str:
        try:
            async with session_factory() as session:
                trigger_instance = await cls._get_trigger_by_name(
                    session=session, name=trigger_name, chat_id=chat_id
                )
                query = (
                    select(func.count())
                    .select_from(TriggerAnswer)
                    .filter_by(trigger_id=trigger_instance.id, media_type=media_type)
                )
                result = await session.execute(query)
                return result.scalar_one()
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @classmethod
    async def get_answer_with_pagination(
        cls,
        trigger_name: str,
        chat_id: int,
        media_type: MediaTypeEnum,
        offset: int,
        items_per_page: int,
    ) -> Sequence[TriggerAnswer] | str:
        try:
            async with session_factory() as session:
                trigger_instance = await cls._get_trigger_by_name(
                    session=session, name=trigger_name, chat_id=chat_id
                )
                query = (
                    select(TriggerAnswer)
                    .filter_by(media_type=media_type, trigger_id=trigger_instance.id)
                    .limit(items_per_page)
                    .offset(offset)  # page (1-1) * 5 = offset 0
                )
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @classmethod
    async def _get_trigger_by_name(
        cls, session: AsyncSession, name: str, chat_id: int
    ) -> Trigger | None:
        query = select(Trigger).filter_by(name=name, chat_id=chat_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
