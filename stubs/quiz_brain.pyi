from trivia_game.base_types import AppControllerProtocol
from trivia_game.trivia_api import TriviaAPIClient

class QuizBrain:
    controller: AppControllerProtocol
    api_client: TriviaAPIClient
    categories: dict[str, str]

    def __init__(self, controller: AppControllerProtocol) -> None: ...
    def _load_categories(self) -> None: ...
    def get_categories_with_any(self) -> list[str]: ...
