from trivia_game import trivia_api
from trivia_game.base_types import AppControllerProtocol, TriviaGameProtocol


class QuizBrain(TriviaGameProtocol):
    def __init__(self, controller: AppControllerProtocol) -> None:
        """Create the quiz brain object

        Args:
            controller (AppControllerProtocol): The main application controller
        Attributes:
            self.controller (AppControllerProtocol): The main application controller
            self.api_client (trivia_api.TriviaAPIClient): The trivia API client
            self.categories (dict[str, str]): The trivia categories

        """
        self.controller: AppControllerProtocol = controller
        self.api_client: trivia_api.TriviaAPIClient = trivia_api.TriviaAPIClient()
        self.categories: dict[str, str] = self.api_client.fetch_categories()
        print(self.categories)
