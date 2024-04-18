from unittest.mock import AsyncMock

import pytest

from src.info_commands.handlers import (
    process_delete_command,
    process_put_command,
    process_use_command,
)


@pytest.fixture(scope="session")
def start_command_text():
    return "test start message 1"


async def test_put_command(start_command_text: str):
    text_mock = f"/put_command start {start_command_text}"
    message_mock = AsyncMock(text=text_mock)
    await process_put_command(message=message_mock)
    message_mock.reply.assert_called_with(
        text=f"☑️put <code>start</code>: <code>{start_command_text}</code>"
    )


async def test_put_command_without_text():
    text_mock = "/put_command"
    message_mock = AsyncMock(text=text_mock)
    await process_put_command(message=message_mock)
    error_msg = "Incorrect bot command entered.\nExample: <code>/put_command start Hello. I'm a beautiful bot.</code>"
    message_mock.reply.assert_called_with(text=error_msg)


async def test_start_command(start_command_text: str):
    text_mock = "/start"
    message_mock = AsyncMock(text=text_mock)
    await process_use_command(message=message_mock)
    message_mock.reply.assert_called_with(text=start_command_text)


async def test_delete_command():
    text_mock = "/delete_command start"
    message_mock = AsyncMock(text=text_mock)
    await process_delete_command(message=message_mock)
    message_mock.reply.assert_called_with(text="☑️delete: <code>start</code>")


async def test_delete_non_exist_command_():
    text_mock = "/delete_command test"
    message_mock = AsyncMock(text=text_mock)
    await process_delete_command(message=message_mock)
    message_mock.reply.assert_called_with(text="❌not found command: <code>test</code>")


async def test_delete_without_command():
    text_mock = "/delete_command"
    message_mock = AsyncMock(text=text_mock)
    await process_delete_command(message=message_mock)
    message_mock.reply.assert_called_with(
        text="Incorrect bot command entered.\nExample: <code>/delete_command start</code>"
    )
