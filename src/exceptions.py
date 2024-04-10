"""
Module containing custom exception classes for error handling.

This module defines custom exception classes that can be used for specific error
scenarios within an application.These exceptions provide  allowing for more
expressive error handling and better organization of code.
"""

from typing import Optional


class RecordsNotFound(Exception):
    """Exception raised when no records were found in the database."""

    def __init__(self, message: str = "No records were found."):
        """
        Initialize the exception.

        :param message: The error message to display.
        :type message: str
        """
        self.message = message
        super().__init__(self.message)


class InvalidCommandError(Exception):
    """Exception raised when incorrect bot command entered."""

    def __init__(
        self,
        message: str = "Incorrect bot command entered.",
        example: Optional[str] = None,
    ):
        """
        Initialize the exception.

        :param message: The error message to display.
        :type message: str
        """
        self.message = message
        if example:
            self.message += f"\nExample: {example}"
        super().__init__(self.message)
