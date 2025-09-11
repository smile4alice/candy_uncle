from random import randint, uniform
from re import findall

from aiogram.types import Message

from app.common.exceptions import RollProcessingError, InputValidationError
from app.features.roll.schemas import RollResult


class RollService:
    """Service class for handling dice digit rolls."""
    
    def __init__(self, message: Message):
        self.message = message
        self.text = message.text or ""
        self.user = message.from_user

    async def process_roll_command(self) -> None:
        """Main method to process roll command."""
        roll = self.get_roll()
        text = self.to_text_from_user(roll)
        await self.message.answer(text=text)

    def get_roll(self) -> RollResult:
        """
        Extract and process dice roll from command text.

        :return: RollResult with roll data
        :raises InputValidationError: When command format is invalid
        :raises RollProcessingError: When roll processing fails
        """
        try:
            extract_digit = findall(
                r"(^\/[rр][оo][lл]{1,})\s*(\d*[.,]*\d*)(.*)",
                self.text.lower(),
            )[0][1]
            min_digit = 1
            if not extract_digit or extract_digit == "0":
                max_digit = 100
                result = randint(min_digit, max_digit)
            elif extract_digit.isdigit() and int(extract_digit) > 1:
                max_digit = int(extract_digit)
                result = randint(min_digit, max_digit)
            else:
                max_digit = float(extract_digit.replace(",", "."))
                max_digit = max_digit if max_digit > 0.1 else 1.0
                min_digit = 1.0 if max_digit > 1.0 else 0.1
                result = round(uniform(min_digit, max_digit), 2)
            return RollResult(
                max_digit=max_digit,
                result=result,
                min_digit=min_digit,
            )
        except IndexError:
            raise InputValidationError(f'Invalid command format: {self.text}. Expected: "/roll OPTIONAL[max_digit]"')
        except Exception as exc:
            raise RollProcessingError(f"Failed to process roll command: {exc}")

    def to_text_from_user(self, roll: RollResult) -> str:
        """
        Format roll result with user information.

        :param roll: RollResult object with roll data
        :return: Formatted text string
        """
        text = (
            f'<a href="{self.user.url}">{self.user.full_name}</a>'
            f" roll <b>{roll.result}</b> ({roll.min_digit} - {roll.max_digit})"
        )
        return text
