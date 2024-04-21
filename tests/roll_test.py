from unittest.mock import AsyncMock

import pytest

from src.roll.handlers import process_roll
from src.roll.services import RollService


@pytest.fixture(scope="session")
def roll_service():
    return RollService()


@pytest.fixture(scope="session")
def roll_text_cases():
    cases = {
        "INTEGER": [
            {
                "case": "/roll 0 lorem",
                "max_digit": 100,
                "min_digit": 1,
            },
            {
                "case": "/roll 200lorem",
                "max_digit": 200,
                "min_digit": 1,
            },
            {
                "case": "/ролл 244 lorem 245",
                "max_digit": 244,
                "min_digit": 1,
            },
        ],
        "FLOAT": [
            {
                "case": "/roll 0.5 lorem",
                "max_digit": 0.5,
                "min_digit": 0.1,
            },
            {
                "case": "/roll 25.50 lorem",
                "max_digit": 25.50,
                "min_digit": 1,
            },
            {
                "case": "/roll 1lorem",
                "max_digit": 1.0,
                "min_digit": 0.1,
            },
            {
                "case": "/ролл 0,0 lorem 245",
                "max_digit": 1.0,
                "min_digit": 0.1,
            },
        ],
    }
    return cases


def test_roll_service_get_roll_integer(
    roll_service: RollService, roll_text_cases: dict
):
    for item in roll_text_cases["INTEGER"]:
        result = roll_service.get_roll(item["case"])
        assert result.max_digit == item["max_digit"]
        assert result.min_digit == item["min_digit"]


def test_roll_service_get_roll_float(roll_service: RollService, roll_text_cases: dict):
    for item in roll_text_cases["FLOAT"]:
        result = roll_service.get_roll(item["case"])
        assert result.max_digit == item["max_digit"]
        assert result.min_digit == item["min_digit"]


async def test_process_roll_handler():
    text_mock = "/roll 50"
    message_mock = AsyncMock(text=text_mock)
    await process_roll(message=message_mock)
    assert message_mock.answer.call_args[1]["text"].startswith("<a href")
