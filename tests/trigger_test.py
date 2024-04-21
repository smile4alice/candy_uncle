from unittest.mock import AsyncMock

from src.triggers.handlers import process_put_trigger_event


async def test_put_trigger_event_simple():
    simple_text = r"test1 test1"
    command = f"/put_trigger_event {simple_text}"
    message_mock = AsyncMock(text=command)
    await process_put_trigger_event(message=message_mock)

    message_mock.reply.assert_called_with(
        text="☑️put <code>test1</code>: <code>test1</code>"
    )


async def test_put_trigger_event_regex():
    simple_text = r"test2 \Sest2 regex"
    command = f"/put_trigger_event {simple_text}"
    message_mock = AsyncMock(text=command)
    await process_put_trigger_event(message=message_mock)

    message_mock.reply.assert_called_with(
        text="☑️put <code>test2</code>: <code>\\Sest2</code>"
    )
