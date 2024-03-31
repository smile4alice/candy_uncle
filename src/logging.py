"""Logging module for sending logs via aiogram library.

This module provides functionality for logging messages and sending them to
a specified chat using the aiogram library. It includes classes for defining log
senders, handlers for emitting log records, and a singleton logger instance
configured to use these components.

Attributes:
    LOGGER: Singleton instance of the logging.Logger class.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Coroutine

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from src.config import SETTINGS


class BaseSender(ABC):
    """Abstract base class for sending logs."""

    @abstractmethod
    def writeLog(self, msg: str) -> None:
        """Method for sending logs.

        Args:
            msg (str): The message to send.

        Example:
            def writeLog(self, msg):
                with open('logs.txt', 'a') as f:
                    f.write(msg)
        """
        pass


class AiogramLogSender(BaseSender):
    """Class for sending logs via aiogram library."""

    def __init__(self, bot: Bot, chat_id: int) -> None:
        """Initialize the AiogramLogSender.

        Args:
            bot (Bot): An instance of the aiogram Bot.
            chat_id (int): The ID of the chat to send logs to.

        """
        self.bot = bot
        self.chat_id = chat_id

    def _run_async(self, coroutine: Coroutine) -> None:
        """Run an asynchronous operation."""
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.run(coroutine)
        else:
            task = loop.create_task(coroutine)
            if not loop.is_running():
                loop.run_until_complete(task)

    def send_logs(self, msg: str) -> Coroutine:
        """Create and return a coroutine for sending log messages to the specified chat."""
        coroutine = self.bot.send_message(
            chat_id=self.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2
        )
        return coroutine

    def writeLog(self, msg: str) -> None:
        self._run_async(self.send_logs(msg=f"```{msg[-2000:]}```"))


class SpecialHandler(logging.Handler):
    """Special logging handler for emitting log records.

    This logging handler emits log records by sending them to a specified log sender
    object, which handles the actual delivery of log messages.
    """

    def __init__(self, sender: BaseSender) -> None:
        self.sender = sender
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        """This method is called to emit a log record by sending it to the
        specified log sender object for processing and delivery.
        """
        msg = self.format(record)
        self.sender.writeLog(msg)


def init_logger() -> logging.Logger:
    """This function creates and configures an instance of the logging.Logger class,
    setting it up with handlers that send log records.
    """
    logs_format = (
        "%(levelname)-8s | %(asctime)-20s| %(filename)s:%(lineno)s | %(message)s"
    )
    logs_date_format = "%H:%M:%S %d-%m-%Y"
    formatter = logging.Formatter(logs_format, logs_date_format)

    console_hanlder = logging.StreamHandler()
    console_hanlder.setFormatter(formatter)
    console_hanlder.setLevel("INFO")

    special_handler = SpecialHandler(
        AiogramLogSender(
            bot=Bot(token=SETTINGS.BOT_TOKEN),
            chat_id=SETTINGS.SUPERUSER_ID,
        )
    )
    special_handler.setFormatter(formatter)
    special_handler.setLevel("WARNING")

    logger = logging.getLogger()
    logger.addHandler(special_handler)
    logger.addHandler(console_hanlder)
    return logger


LOGGER = init_logger()
"""Singleton instance of logging"""
