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

    def get_categories_with_any(self) -> list[str]:
        """Get the categories with the 'Any Category' option

        Returns:
            list[str]: The categories with the 'Any Category' option
        """
        categories: list[str] = ["Any Category"]
        categories.extend(sorted(self.categories.keys()))
        return categories

    def get_category_id(self, category_name: str) -> str | None:
        """Get category ID for API request

        Args:
            category_name (str): The category name

        Returns:
            str | None: The category ID or None if 'Any Category'

        """
        if category_name == "Any Category":
            return None
        return self.categories[category_name]

    def get_difficulties(self) -> list[str]:
        """Get the difficulties for the quiz

        Returns:
            list[str]: The difficulties

        """
        return ["Any Difficulty", "Easy", "Medium", "Hard"]

    def get_question_types(self) -> list[str]:
        """Get the question types for the quiz

        Returns:
            list[str]: The question types

        """
        return ["Any Type", "Multiple Choice", "True / False"]
