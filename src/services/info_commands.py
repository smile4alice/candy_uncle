from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import session_factory
from src.exceptions import InvalidCommandError, RecordsNotFound
from src.lib import SERVER_ERROR
from src.logging import LOGGER
from src.models.info_command import InfoCommand


class InfoCommandORM:
    """Methods of interacting with the database using SQLAlchemy"""

    @staticmethod
    async def get_one_by_name(
        name: str,
        current_session: AsyncSession | None = None,
    ) -> InfoCommand | None:
        """
        Get command filtered by name.

        :param current_session (AsyncSession | None): current session for
         execute the query or None for create new session.
        :param name (str): The name of the command to filter.
        :return (InfoCommand | None]): Command that match the filter
         criteria or None if records not found.
        """
        query = select(InfoCommand).filter_by(name=name)
        if current_session:
            result = await current_session.execute(query)
        else:
            async with session_factory() as session:
                result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def update_or_add_by_name(cls, name: str, info: str) -> InfoCommand:
        """
        Update or create command record by name.

        :param name (str): The name of the command to filter.
        :return (InfoCommand | None]): Command that match the filter criteria or None if records not found.
        """
        async with session_factory() as session:
            record = await cls.get_one_by_name(name=name, current_session=session)
            if record:
                record.info = info
            else:
                record = InfoCommand(name=name, info=info)
                session.add(record)
            await session.commit()
        return record

    @staticmethod
    async def delete_by_name(name: str) -> bool:
        """
        Delete command record by name.

        :param name (str): The name of the command to filter.
        :return (bool]): Command that match the filter criteria or None if records not found.
        """
        async with session_factory() as session:
            query = delete(InfoCommand).filter_by(name=name)
            result = await session.execute(query)
            await session.commit()
        return bool(result.rowcount)


class InfoCommandService:
    @staticmethod
    def _get_name_from_command(text: str) -> str:
        """As example get "command_name" from text = "/command_name value" """
        command_name = text.split()[0][1:]
        return command_name

    @classmethod
    async def detect_command(cls, text: str) -> bool:
        """
        Checking for a match by keyword in the text

        :param command_name (str): The name of the command to search for.
        :return (bool]): True if a match is found, False if not.
        """
        try:
            command_name = cls._get_name_from_command(text)
            records = await InfoCommandORM.get_one_by_name(command_name)
            return bool(records)
        except Exception as e:
            LOGGER.exception(e)
            return False

    @classmethod
    async def use_command(cls, text: str) -> str:
        """
        Retrieve command info by command name.

        :param text (str): The Message text with command name by filter in the database.
        :return (str): command data if the command name is found in the database,
         else InvalidCommandError warning text.
        """
        try:
            command_name = cls._get_name_from_command(text)
            record = await InfoCommandORM.get_one_by_name(command_name)
            if record:
                return record.info
            else:
                raise InvalidCommandError
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @classmethod
    async def update_or_add(cls, text: str) -> str:
        """
        This function first attempts to retrieve a record from the database based on
        the provided command name. If a record is found, it's text data is updated with the
        provided text. If no record is found, then create a new.

        :param text (str): The message text with command name and data to
         update or add to the record.
        :return (str): is operation was successful or no.
        """
        try:
            command_data = text.lower().split()
            if len(command_data) < 3:
                example = "<code>/put_command start Hello. I'm a beautiful bot.</code>"
                raise InvalidCommandError(example=example)
            else:
                command_name = command_data[1]
                command_info = " ".join(command_data[2:])
                await InfoCommandORM.update_or_add_by_name(command_name, command_info)
                return (
                    f"☑️put:\n<code>{command_name}</code> = <code>{command_info}</code>"
                )
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def delete_command(text: str) -> str:
        """
        Delete command info by command name.

        :param text (str): The message text with command name and data to update or add to the record.
        :return (str): is operation was successful or no.
        """
        try:
            command_data = text.lower().split()
            if len(command_data) < 2:
                example = "<code>/delete_command start</code>"
                raise InvalidCommandError(example=example)
            else:
                command_name = command_data[1]

            result = await InfoCommandORM.delete_by_name(command_name)
            if result:
                return f"☑️delete: <code>{command_name}</code>"
            else:
                raise RecordsNotFound(
                    message=f"❌not found: <code>{command_name}</code>"
                )
        except InvalidCommandError as e:
            return str(e)
        except RecordsNotFound as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR
