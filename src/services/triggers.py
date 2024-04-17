from re import findall
from typing import Sequence

from sqlalchemy import and_, delete, func, literal, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import session_factory
from src.enums import MatchModeEnum, MediaTypeEnum
from src.exceptions import InvalidCommandError, RecordsNotFound
from src.lib import SERVER_ERROR
from src.logging import LOGGER
from src.models import Trigger, TriggerEvent


class TriggerEventORM:
    """Methods of interacting with the database using SQLAlchemy"""

    @staticmethod
    async def search_triggers_in_text(text: str, chat_id: int) -> TriggerEvent | None:
        """Search for a TriggerEvent in the database based on text.

        :param text: The text to search for.
        :param chat_id: The chat ID to filter by.
        :return: The TriggerEvent that matches the search criteria, or None if not found.
        """
        async with session_factory() as session:
            query = select(TriggerEvent).filter_by(is_active=True, chat_id=chat_id)
            search_condition = or_(
                and_(
                    TriggerEvent.match_type == MatchModeEnum.text,
                    literal(text).icontains(TriggerEvent.event),
                ),
                and_(
                    TriggerEvent.match_type == MatchModeEnum.regex,
                    literal(text).op("~*")(TriggerEvent.event),
                ),
            )
            query = query.where(search_condition)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @staticmethod
    async def get_one_by_name(
        name: str,
        chat_id: int,
        current_session: AsyncSession | None = None,
        only_active=True,
    ) -> TriggerEvent | None:
        """Get a TriggerEvent filtered by name and chat_id.

        :param name: The name of the TriggerEvent to filter.
        :param chat_id: The chat ID to filter by.
        :param current_session: The current session to execute the query, or None to create a new session.
        :param only_active: If True, only active TriggerEvents will be considered (default is True).
        :return: The TriggerEvent that matches the filter criteria, or None if not found.
        """
        query = select(TriggerEvent).filter_by(name=name, chat_id=chat_id)
        if only_active:
            query.filter_by(is_active=True)
        if current_session:
            result = await current_session.execute(query)
        else:
            async with session_factory() as session:
                result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def update_by_name_or_create(
        cls,
        name: str,
        chat_id: int,
        event: str,
        match_type: MatchModeEnum,
    ) -> TriggerEvent:
        """Update or create a TriggerEvent record by name.

        :param name: The name of the TriggerEvent to update or create.
        :param chat_id: The chat ID associated with the TriggerEvent.
        :param event: The event string.
        :param match_type: The match type of the TriggerEvent.
        :return: The updated or newly created TriggerEvent.
        """
        async with session_factory() as session:
            record = await cls.get_one_by_name(
                name=name,
                chat_id=chat_id,
                current_session=session,
                only_active=False,
            )
            if record:
                record.event = event
                record.match_type = match_type
            else:
                record = TriggerEvent(
                    name=name,
                    event=event,
                    match_type=match_type,
                    chat_id=chat_id,
                )
                session.add(record)
            await session.commit()
        return record

    @staticmethod
    async def delete_by_name(name: str, chat_id: int) -> bool:
        """Delete a TriggerEvent record by name and chat_id.

        :param name: The name of the TriggerEvent to delete.
        :param chat_id: The chat ID to filter by.
        :return: True if the record was deleted successfully, False otherwise.
        """
        async with session_factory() as session:
            query = delete(TriggerEvent).filter_by(name=name, chat_id=chat_id)
            result = await session.execute(query)
            await session.commit()
        return bool(result.rowcount)


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
                match_type = MatchModeEnum.regex if is_regex else MatchModeEnum.text
            else:
                example = '<code>/put_trigger_event [name] [trigger] ["regex" if regex_mode]</code>'
                raise InvalidCommandError(example=example)
            await TriggerEventORM.update_by_name_or_create(
                name=name,
                chat_id=chat_id,
                event=event,
                match_type=match_type,
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
                raise RecordsNotFound(f"❌not found: <code>{name}</code>")
        except InvalidCommandError as e:
            return str(e)
        except RecordsNotFound as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR


class TriggerORM:
    """Methods of interacting with the database using SQLAlchemy"""

    @staticmethod
    async def get_random_active_by_event_id(
        trigger_event_id: int,
    ) -> Trigger | None:
        random_trigger_query = (
            select(Trigger)
            .filter_by(
                is_active=True,
                trigger_event_id=trigger_event_id,
            )
            .order_by(func.random())
            .limit(1)
        )
        async with session_factory() as session:
            result = await session.execute(random_trigger_query)
            record = result.scalar_one_or_none()
            if not record:
                query = (
                    update(Trigger)
                    .filter_by(trigger_event_id=trigger_event_id)
                    .values(is_active=True)
                )
                await session.execute(query)
                result = await session.execute(random_trigger_query)
                record = result.scalar_one_or_none()
            if record:
                record.is_active = False
                await session.commit()
        return record

    @staticmethod
    async def update_by_id_or_create(
        trigger_event: str,
        chat_id: int,
        media_type: MediaTypeEnum,
        media: str,
    ) -> Trigger:
        """Update or create a TriggerEvent record by name.

        :param name: The name of the TriggerEvent to update or create.
        :param chat_id: The chat ID associated with the TriggerEvent.
        :param event: The event string.
        :param match_type: The match type of the TriggerEvent.
        :return: The updated or newly created TriggerEvent.
        """
        async with session_factory() as session:
            trigger_event_record = await TriggerEventORM.get_one_by_name(
                name=trigger_event,
                chat_id=chat_id,
                current_session=session,
                only_active=False,
            )
            # TODO search by media and trigger id for unique
            trigger_record = Trigger(
                media_type=media_type,
                media=media,
                trigger_event_id=trigger_event_record.id,
            )
            session.add(trigger_record)
            await session.commit()
        return trigger_record


class TriggerService:
    @staticmethod
    async def get_trigger(text: str, chat_id: int) -> Trigger | str:
        try:
            trigger_event = await TriggerEventORM.search_triggers_in_text(text, chat_id)
            trigger = await TriggerORM.get_random_active_by_event_id(trigger_event.id)
            if trigger:
                return trigger
            else:
                raise RecordsNotFound(
                    f"❌not found triggers for event <code>{trigger_event.name}</code>"
                )
        except RecordsNotFound as e:
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
                    raise RecordsNotFound(
                        f"❌not found event: <code>{trigger_event}<code>"
                    )
        except InvalidCommandError as e:
            return str(e)
        except RecordsNotFound as e:
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
                    .select_from(Trigger)
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
    ) -> Sequence[Trigger] | str:
        try:
            async with session_factory() as session:
                trigger_instance = await cls._get_trigger_by_name(
                    session=session, name=trigger_name, chat_id=chat_id
                )
                query = (
                    select(Trigger)
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
    ) -> TriggerEvent | None:
        query = select(TriggerEvent).filter_by(name=name, chat_id=chat_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
