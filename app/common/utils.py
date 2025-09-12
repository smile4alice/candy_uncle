"""Utility functions and decorators."""

import traceback
from functools import wraps
from typing import Callable, Any

from aiogram.types import Message

from app.config import settings
from app.common.logging import logger
from app.common.exceptions import BaseAppException


def error_handler(func: Callable) -> Callable:
    """Decorator to handle errors in route functions."""

    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs) -> Any:
        try:
            return await func(message, *args, **kwargs)
        except BaseAppException as exc:
            await _handle_app_error(message, exc)
        except Exception as exc:
            await _handle_generic_error(message, exc)

    return wrapper


async def _handle_app_error(message: Message, error: BaseAppException) -> None:
    """Handle application-specific errors."""
    try:
        # Send user-friendly message
        await message.bot.send_message(chat_id=message.chat.id, text=error.user_message)

        # Send detailed error to superuser
        await _send_error_to_superuser(message, error)

    except Exception as e:
        logger.exception(f"Failed to handle app error: {e}")


async def _handle_generic_error(message: Message, error: Exception) -> None:
    """Handle generic errors."""
    try:
        # Send generic user message
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Something went wrong. Please try again later.",
        )

        # Send detailed error to superuser
        await _send_error_to_superuser(message, error)

    except Exception as e:
        logger.exception(f"Failed to handle generic error: {e}")


async def _send_error_to_superuser(message: Message, error: Exception) -> None:
    """Send detailed error information to superuser."""
    try:
        error_details = _format_error_details(message, error)

        await message.bot.send_message(chat_id=settings.SUPERUSER_ID, text=error_details, parse_mode="HTML")

    except Exception as e:
        logger.exception(f"Failed to send error to superuser: {e}")


def _format_error_details(message: Message, error: Exception) -> str:
    """Format error details for superuser."""
    error_traceback = traceback.format_exc()
    user_message = message.text or "No text"
    user_id = message.from_user.id if message.from_user else None

    return (
        f"🚨 <b>Error occurred</b>\n\n"
        f"<b>Chat ID:</b> {message.chat.id}\n"
        f"<b>User ID:</b> {user_id}\n"
        f"<b>User message:</b> <code>{user_message}</code>\n"
        f"<b>Error:</b> {type(error).__name__}: {str(error)}\n\n"
        f"<b>Traceback:</b>\n<code>{error_traceback}</code>"
    )
