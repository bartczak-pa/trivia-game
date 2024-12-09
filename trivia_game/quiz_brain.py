from trivia_game.base_types import AppControllerProtocol, TriviaGameProtocol
from trivia_game.exceptions import CategoryError
from trivia_game.trivia_api import TriviaAPIClient


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
        self.api_client: TriviaAPIClient = TriviaAPIClient()
        self.categories: dict[str, str] = {}

        self._load_categories()

    def _load_categories(self) -> None:
        """Load trivia categories from the API"""
        try:
            self.categories = self.api_client.fetch_categories()
        except CategoryError as e:
            self.controller.show_error(f"Error loading categories: {e}. Please try again later.")
