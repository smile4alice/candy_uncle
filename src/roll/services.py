from dataclasses import dataclass
from random import randint, uniform
from re import findall

from aiogram.types import User

from src.lib import SERVER_ERROR
from src.logging import LOGGER


@dataclass
class RollResult:
    """Dataclass representing a dice digit roll."""

    max_digit: int | float
    result: int | float
    min_digit: int | float


class RollService:
    """Service class for handling dice digit rolls."""

    def get_roll(self, text: str) -> RollResult | str:
        """Extracts and processes a dice roll from the provided text.

        Args:
            text (str): The text containing the roll command.

        Returns:
            Roll: An instance of Roll representing the result of the roll.

        """
        try:
            extract_digit = findall(
                r"(^\/[rр][оo][lл]{1,})\s*(\d*[.,]*\d*)(.*)",
                text.lower(),
            )[0][1]
            min_digit = 1
            if not extract_digit or extract_digit == "0":
                max_digit = 100
                result = randint(min_digit, max_digit)
            elif extract_digit.isdigit() and int(extract_digit) > 1:
                max_digit = int(extract_digit)
                result = randint(min_digit, max_digit)
            else:
                max_digit = float(extract_digit.replace(",", "."))  # type: ignore
                max_digit = max_digit if max_digit > 0.1 else 1.0  # type: ignore
                min_digit = 1.0 if max_digit > 1.0 else 0.1  # type: ignore
                result = round(uniform(min_digit, max_digit), 2)  # type: ignore
            return RollResult(
                max_digit=max_digit,
                result=result,
                min_digit=min_digit,
            )
        except IndexError:
            return f'{text} != template "/roll OPTIONAL[max_digit]"'
        except Exception as exc:
            LOGGER.exception(exc)
            return SERVER_ERROR

    def to_text_from_user(self, from_user: User, roll: RollResult | str) -> str:
        """Format the text with user information and roll result

        Example:
            John Doe roll 46(1-100)
        """

        if isinstance(roll, RollResult):
            text = (
                f'<a href="{from_user.url}">{from_user.full_name}</a>'
                f" roll <b>{roll.result}</b> ({roll.min_digit} - {roll.max_digit})"
            )
            return text
        else:
            return roll
