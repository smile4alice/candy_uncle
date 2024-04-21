from src.exceptions import InvalidCommandError, RecordsNotFoundError
from src.lib import SERVER_ERROR
from src.logging import LOGGER

from .lib import NOT_FOUND_COMMAND
from .repository import InfoCommandORM


class InfoCommandService:
    @staticmethod
    def _get_name_from_command(text: str) -> str:
        """As example get "command_name" from text = "/command_name value" """
        command_name = text.split()[0][1:]
        return command_name

    @classmethod
    async def detect_command(cls, text: str, chat_id: int) -> bool:
        """
        Checking for a match by keyword in the text

        :param command_name (str): The name of the command to search for.
        :param chat_id (int): The chat ID associated with the InfoCommand.
        :return (bool]): True if a match is found, False if not.
        """
        try:
            command_name = cls._get_name_from_command(text)
            records = await InfoCommandORM.get_one_by_name_and_chat_id(
                command_name, chat_id
            )
            return bool(records)
        except Exception as e:
            LOGGER.exception(e)
            return False

    @classmethod
    async def use_command(cls, text: str, chat_id: int) -> str:
        """
        Retrieve command info by command name and chat_id.

        :param text (str): The Message text with command name by filter in the database.
        :param chat_id (int): The chat ID associated with the InfoCommand.
        :return (str): command data if the command name is found in the database,
         else InvalidCommandError warning text.
        """
        try:
            command_name = cls._get_name_from_command(text)
            record = await InfoCommandORM.get_one_by_name_and_chat_id(
                command_name, chat_id
            )
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
    async def put_command(cls, text: str, chat_id: int) -> str:
        """
        This function first attempts to retrieve a record from the database based on
        the provided command name and chat_id. If a record is found, it's text data is updated with the
        provided text. If no record is found, then create a new.

        :param text (str): The message text with command name and data to
         update or add to the record.
        :param chat_id (int): The chat ID associated with the InfoCommand.
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
                await InfoCommandORM.create_or_update_by_name_and_chat_id(
                    command_name, command_info, chat_id=chat_id
                )
                return f"☑️put <code>{command_name}</code>: <code>{command_info}</code>"
        except InvalidCommandError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR

    @staticmethod
    async def delete_command(text: str, chat_id: int) -> str:
        """
        Delete command info by command name and chat_id.

        :param text (str): The message text with command name and data to update or add to the record.
        :param chat_id (int): The chat ID associated with the InfoCommand.
        :return (str): is operation was successful or no.
        """
        try:
            command_data = text.lower().split()
            if len(command_data) < 2:
                example = "<code>/delete_command start</code>"
                raise InvalidCommandError(example=example)
            else:
                command_name = command_data[1]

            result = await InfoCommandORM.delete_by_name_and_chat_id(
                command_name, chat_id
            )
            if result:
                return f"☑️delete: <code>{command_name}</code>"
            else:
                raise RecordsNotFoundError(NOT_FOUND_COMMAND % command_name)
        except InvalidCommandError as e:
            return str(e)
        except RecordsNotFoundError as e:
            return str(e)
        except Exception as e:
            LOGGER.exception(e)
            return SERVER_ERROR
