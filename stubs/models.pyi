from dataclasses import dataclass
from enum import IntEnum

class TriviaResponseCode(IntEnum):
    SUCCESS: int
    NO_RESULTS: int
    INVALID_PARAMETER: int
    TOKEN_NOT_FOUND: int
    TOKEN_EMPTY: int
    RATE_LIMIT: int

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Question:
    type: str
    difficulty: str
    category: str
    question: str
    correct_answer: str
    incorrect_answers: list[str]
