from trivia_game.base_types import AppControllerProtocol
from trivia_game.trivia_api import TriviaAPIClient

class QuizBrain:
    controller: AppControllerProtocol
    api_client: TriviaAPIClient
    categories: dict[str, str]

    def __init__(self, controller: AppControllerProtocol) -> None: ...
