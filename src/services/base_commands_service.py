from sqlalchemy import select

from src.database import async_session_maker
from src.exceptions import RecordsNotFound
from src.models.base_command_model import BaseCommandModel


async def get_text_by_command_name(name: str) -> str:
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
        async with async_session_maker() as session:
            query = select(BaseCommandModel).filter_by(name=name)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
        if record:
            return record.text
        else:
            raise RecordsNotFound()
    except RecordsNotFound as e:
        return str(e)
    except Exception as e:
        # TODO logger
        raise e


async def update_or_add_record_by_name(name: str, text: str) -> bool:
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
        async with async_session_maker() as session:
            query = select(BaseCommandModel).filter_by(name=name)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                record.text = text
            else:
                instance = BaseCommandModel(name=name, text=text)
                session.add(instance)
            await session.commit()
        return True
    except Exception:
        # TODO logger
        return False
