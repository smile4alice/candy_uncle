"""Roll schemas."""

from pydantic import BaseModel


class RollResult(BaseModel):
    """Pydantic model representing a dice digit roll."""

    max_digit: int | float
    result: int | float
    min_digit: int | float
