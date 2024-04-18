"""
Module containing custom exception classes for error handling.

This module defines custom exception classes that can be used for specific error
scenarios within an application.These exceptions provide  allowing for more
expressive error handling and better organization of code.
"""

from typing import Optional

from src.lib import INVALID_COMMAND_ERROR, RECORDS_NOT_FOUND_ERROR


class RecordsNotFoundError(Exception):
    """Exception raised when no records were found in the database."""

    def __init__(self, message: str = RECORDS_NOT_FOUND_ERROR) -> None:
        """
        Initialize the exception.

        :param message(str): The error message to display.
        """
        self.message = message
        super().__init__(self.message)


class InvalidCommandError(Exception):
    """Exception raised when an incorrect bot command is entered."""

    def __init__(
        self,
        message: str = INVALID_COMMAND_ERROR,
        example: Optional[str] = None,
    ) -> None:
        """
        Initialize the exception.

        :param message(str): The error message to display.
        :param example(Optional[str]): An optional example to include in the error message.
        """
        self.message = message
        if example:
            self.message += f"\nExample: {example}"
        super().__init__(self.message)
