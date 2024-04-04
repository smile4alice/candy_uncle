from unittest.mock import AsyncMock

import pytest
from src.handlers.base_commands import process_start, process_update_command


@pytest.fixture(scope="session")
def start_command_text():
    return "test start message 1"


async def test_update_command(start_command_text: str):
    text_mock = f"/update_base_command start {start_command_text}"
    message_mock = AsyncMock(text=text_mock)
    await process_update_command(message=message_mock)
    message_mock.reply.assert_called_with(text="start command successfully update.")


async def test_start_command(start_command_text: str):
    text_mock = "/start"
    message_mock = AsyncMock(text=text_mock)
    await process_start(message=message_mock)
    message_mock.reply.assert_called_with(text=start_command_text)
