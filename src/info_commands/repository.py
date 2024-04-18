from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import session_factory

from .models import InfoCommand


class InfoCommandORM:
    """Methods of interacting with the database using SQLAlchemy"""

    @staticmethod
    async def get_one_by_name_and_chat_id(
        name: str,
        chat_id: int,
        current_session: AsyncSession | None = None,
    ) -> InfoCommand | None:
        """
        Get command filtered by name.

        :param current_session (AsyncSession | None): current session for
         execute the query or None for create new session.
        :param name (str): The name of the command to filter.
        :param chat_id (int): The chat ID associated with the InfoCommand.
        :return (InfoCommand | None]): Command that match the filter
         criteria or None if records not found.
        """
        query = select(InfoCommand).filter_by(name=name, chat_id=chat_id)
        if current_session:
            result = await current_session.execute(query)
        else:
            async with session_factory() as session:
                result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def create_or_update_by_name_and_chat_id(
        cls, name: str, info: str, chat_id: int
    ) -> InfoCommand:
        """
        Create or update InfoCommand record by name.

        :param name (str): The name of the command to filter.
        :param chat_id (int): The chat ID associated with the InfoCommand.
        :param info (str): The command info for command when use it.
        :return (InfoCommand | None]): Command that match the filter criteria or None if records not found.
        """
        async with session_factory() as session:
            record = await cls.get_one_by_name_and_chat_id(
                name=name, chat_id=chat_id, current_session=session
            )
            if record:
                record.info = info
            else:
                record = InfoCommand(name=name, info=info, chat_id=chat_id)
                session.add(record)
            await session.commit()
        return record

    @staticmethod
    async def delete_by_name_and_chat_id(name: str, chat_id: int) -> bool:
        """
        Delete command record by name and chat_id.

        :param name (str): The name of the command to filter.
        :param chat_id (int): The chat ID associated with the InfoCommand.
        :return (bool]): Command that match the filter criteria or None if records not found.
        """
        async with session_factory() as session:
            query = delete(InfoCommand).filter_by(name=name, chat_id=chat_id)
            result = await session.execute(query)
            await session.commit()
        return bool(result.rowcount)
