from typing import Literal, TypedDict

DifficultyType = Literal["easy", "medium", "hard"]
QuestionType = Literal["multiple", "boolean"]

class TriviaResponseCode:
    SUCCESS: int
    NO_RESULTS: int
    INVALID_PARAMETER: int
    TOKEN_NOT_FOUND: int
    TOKEN_EMPTY: int
    RATE_LIMIT: int

class Question(TypedDict):
    type: QuestionType
    difficulty: DifficultyType
    category: str
    question: str
    correct_answer: str
    incorrect_answers: list[str]
