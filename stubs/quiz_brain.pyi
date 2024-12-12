from typing import ClassVar

from trivia_game.base_types import AppControllerProtocol
from trivia_game.trivia_api import TriviaAPIClient

class QuizBrain:
    controller: AppControllerProtocol
    api_client: TriviaAPIClient
    categories: dict[str, str]
    current_question: dict
    questions: list
    score: int
    TYPE_MAPPING: ClassVar[dict[str, str | None]]

    def __init__(self, controller: AppControllerProtocol) -> None: ...
    def _load_categories(self) -> None: ...
    def get_categories_with_any(self) -> list[str]: ...
    def get_category_id(self, category_name: str) -> str | None: ...
    def get_difficulties(self) -> list[str]: ...
    def get_question_types(self) -> list[str]: ...
