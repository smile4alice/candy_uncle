from sqlalchemy import delete, select

from src.database import session_factory
from src.exceptions import InvalidCommandError, RecordsNotFound
from src.lib import SERVER_ERROR
from src.logging import LOGGER
from src.models.base_command_model import BaseCommand


class CommandService:

    @staticmethod
    async def detect_command(text: str) -> bool:
        try:
            command_name = text[1:]
            # TODO caching with redis
            async with session_factory() as session:
                query = select(BaseCommand).where(
                    BaseCommand.name.like(f"%{command_name}%")
                )
                result = await session.execute(query)
                records = result.scalars().all()
            return bool(records)
        except Exception as e:
            LOGGER.exception(e)
            return False

    @staticmethod
    async def get_command_text(text: str) -> str:
        """
        Retrieve instance with command data by command name.

        Args:
            name (str): The command name by filter in the database.

        Returns:
            BaseCommandModel | None: An instance of BaseCommandModel if the command name
            is found in the database, otherwise None.

        Raises:
            RecordsNotFound: If no records were found in the database.
        """
        try:
            name = text.lower().split()[0][1:]
            async with session_factory() as session:
                query = select(BaseCommand).filter_by(name=name)
                result = await session.execute(query)
                record = result.scalar_one_or_none()
            if record:
                return record.text
            else:
                raise RecordsNotFound()
        except RecordsNotFound as e:
            msg = str(e)
            LOGGER.warning(msg)
            return msg
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def update_or_add_command(text: str) -> str:
        """
        This function first attempts to retrieve a record from the database based on
        the provided command name. If a record is found, its text data is updated with the
        provided text. If no record is found, a new

        Args:
            name (str): The command name to search for in the database.
            text (str): The text data to update or add to the record.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            command_data = text.lower().split()
            if len(command_data) < 3:
                example = "/update_base_command start Hello. I'm a beautiful bot."
                raise InvalidCommandError(example=example)
            else:
                command_name = command_data[1]
                command_text = " ".join(command_data[2:])

            async with session_factory() as session:
                query = select(BaseCommand).filter_by(name=command_name)
                result = await session.execute(query)
                record = result.scalar_one_or_none()
                if record:
                    record.text = command_text
                else:
                    instance = BaseCommand(name=command_name, text=command_text)
                    session.add(instance)
                await session.commit()
                return f"{command_name} command successfully update."
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def delete_command(text: str) -> str:
        try:
            command_data = text.lower().split()
            if len(command_data) < 2:
                example = "delete_command start"
                raise InvalidCommandError(example=example)
            else:
                command_name = command_data[1]

            async with session_factory() as session:
                query = delete(BaseCommand).filter_by(name=command_name)
                result = await session.execute(query)
                rowcount = result.rowcount
                await session.commit()
            if rowcount:
                response = f"{command_name} command successfully delete."
            else:
                response = f"{command_name} not found."
            return response
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR
