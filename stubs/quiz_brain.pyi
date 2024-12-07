from trivia_game.app_interface import AppInterface
from trivia_game.trivia_api import TriviaAPIClient

class QuizBrain:
    interface: AppInterface
    api_client: TriviaAPIClient
    categories: dict[str, str]

    def __init__(self, interface: AppInterface) -> None: ...
