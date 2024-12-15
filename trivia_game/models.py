"""Models for the trivia game."""

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Literal, TypeVar

T = TypeVar("T")
DifficultyType = Literal["easy", "medium", "hard"]
QuestionType = Literal["multiple", "boolean"]


class TriviaResponseCode(IntEnum):
    """Enum for trivia API response codes."""

    SUCCESS: int = 0
    NO_RESULTS: int = 1
    INVALID_PARAMETER: int = 2
    TOKEN_NOT_FOUND: int = 3
    TOKEN_EMPTY: int = 4
    RATE_LIMIT: int = 5


@dataclass
class Category:
    """Dataclass for a trivia category."""

    id: str
    name: str


@dataclass
class Question:
    """Dataclass for a trivia question."""

    type: QuestionType
    difficulty: DifficultyType
    category: str
    question: str
    correct_answer: str
    incorrect_answers: list[str]

    def all_answers(self) -> list[str]:
        """Return all answers including correct and incorrect ones.

        Returns:
            list[str]: All answers
        """
        return [self.correct_answer, *self.incorrect_answers]


@dataclass
class ScoreboardEntry:
    player_name: str
    score: int
    date: datetime
