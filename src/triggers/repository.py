from typing import Sequence

from sqlalchemy import and_, delete, func, literal, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import session_factory
from src.enums import MatchModeEnum, MediaTypeEnum

from .models import Trigger, TriggerEvent


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
                    TriggerEvent.match_mode == MatchModeEnum.text,
                    literal(text).icontains(TriggerEvent.event),
                ),
                and_(
                    TriggerEvent.match_mode == MatchModeEnum.regex,
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
    async def create_or_update_by_name(
        cls,
        name: str,
        chat_id: int,
        event: str,
        match_mode: MatchModeEnum,
    ) -> TriggerEvent:
        """Update or create a TriggerEvent record by name.

        :param name (str): The name of the TriggerEvent to update or create.
        :param chat_id (int): The chat ID associated with the TriggerEvent.
        :param event (str): The event string for match.
        :param match_mode (MatchModeEnum): The match type of the TriggerEvent.
        :return (TriggerEvent): The updated or newly created TriggerEvent.
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
                record.match_mode = match_mode
            else:
                record = TriggerEvent(
                    name=name,
                    event=event,
                    match_mode=match_mode,
                    chat_id=chat_id,
                )
                session.add(record)
            await session.commit()
        return record

    @staticmethod
    async def delete_by_name(name: str, chat_id: int) -> bool:
        """Delete a TriggerEvent record by name and chat_id.

        :param name (str): The name of the TriggerEvent to delete.
        :param chat_id (int): The chat ID to filter by.
        :return (bool): True if the record was deleted successfully, False otherwise.
        """
        async with session_factory() as session:
            query = delete(TriggerEvent).filter_by(name=name, chat_id=chat_id)
            result = await session.execute(query)
            await session.commit()
        return bool(result.rowcount)


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
    async def create(
        trigger_event: str,
        chat_id: int,
        media_type: MediaTypeEnum,
        media: str,
    ) -> Trigger:
        """Update or create a TriggerEvent record by name.

        :param name: The name of the TriggerEvent to update or create.
        :param chat_id: The chat ID associated with the TriggerEvent.
        :param event: The event string.
        :param match_mode: The match type of the TriggerEvent.
        :return: The updated or newly created TriggerEvent.
        """
        async with session_factory() as session:
            trigger_event_record = await TriggerEventORM.get_one_by_name(
                name=trigger_event,
                chat_id=chat_id,
                current_session=session,
                only_active=False,
            )
            trigger_record = Trigger(
                media_type=media_type,
                media=media,
                trigger_event_id=trigger_event_record.id,
            )
            session.add(trigger_record)
            await session.commit()
        return trigger_record

    @staticmethod
    def _get_next_offset(
        items_per_page,
        total_items,
        offset,
    ):
        next_offset = items_per_page + int(offset) if offset else items_per_page
        return str(next_offset) if next_offset < total_items else None

    @staticmethod
    async def _get_total_items_by_type(
        trigger_event_id: int,
        media_type: MediaTypeEnum,
        session: AsyncSession,
    ) -> int:
        query = (
            select(func.count())
            .select_from(Trigger)
            .filter_by(trigger_event_id=trigger_event_id, media_type=media_type)
        )
        result = await session.execute(query)
        return result.scalar_one()

    @classmethod
    async def paginate_records_list(
        cls,
        event_name: str,
        chat_id: int,
        media_type: MediaTypeEnum,
        offset: str,
        items_per_page: int,
    ) -> tuple[str | None, Sequence[Trigger]]:
        async with session_factory() as session:
            trigger_event_record = await TriggerEventORM.get_one_by_name(
                current_session=session, name=event_name, chat_id=chat_id
            )
            total_items = await cls._get_total_items_by_type(
                trigger_event_record.id, media_type, session
            )
            next_offset = cls._get_next_offset(items_per_page, total_items, offset)
            query = (
                select(Trigger)
                .filter_by(
                    media_type=media_type,
                    trigger_event_id=trigger_event_record.id,
                )
                .limit(items_per_page)
                .offset(next_offset)  # page (1-1) * 5 = offset 0
            )
            result = await session.execute(query)
            return next_offset, result.scalars().all()

    @staticmethod
    async def delete_by_id(trigger_id: int) -> bool:
        """Delete a TriggerEvent record by name and chat_id.

        :param name (str): The name of the TriggerEvent to delete.
        :param chat_id (int): The chat ID to filter by.
        :return (bool): True if the record was deleted successfully, False otherwise.
        """
        async with session_factory() as session:
            query = delete(Trigger).filter_by(id=trigger_id)
            result = await session.execute(query)
            await session.commit()
        return bool(result.rowcount)
