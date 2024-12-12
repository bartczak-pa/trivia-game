from typing import ClassVar

from trivia_game.base_types import AppControllerProtocol, TriviaGameProtocol
from trivia_game.exceptions import CategoryError
from trivia_game.trivia_api import TriviaAPIClient


class QuizBrain(TriviaGameProtocol):
    TYPE_MAPPING: ClassVar[dict[str, str | None]] = {
        "Any Type": None,
        "Multiple Choice": "multiple",
        "True / False": "boolean",
    }

    def __init__(self, controller: AppControllerProtocol) -> None:
        """Create the quiz brain object

        Args:
            controller (AppControllerProtocol): The main application controller

        Attributes:
            controller (AppControllerProtocol): The main application controller
            api_client (TriviaAPIClient): The API client
            categories (dict[str, str]): The trivia categories
            current_question (dict): The current question being displayed
            questions (list[dict]): The list of questions for the current game
            score (int): The current score
        """

        self.controller: AppControllerProtocol = controller
        self.api_client: TriviaAPIClient = TriviaAPIClient()

        self.categories: dict[str, str] = {}
        self.current_question: dict = {}
        self.questions: list = []
        self.score: int = 0

        self._load_categories()

    def _load_categories(self) -> None:
        """Load trivia categories from the API"""
        try:
            self.categories = self.api_client.fetch_categories()
        except CategoryError as e:
            self.controller.show_error(f"Error loading categories: {e}. Please try again later.")

    def get_available_categories(self) -> list[str]:
        """Get list of available categories including 'Any Category' option

        Returns:
            list[str]: The categories with the 'Any Category' option
        """
        categories: list[str] = ["Any Category"]
        categories.extend(sorted(self.categories.keys()))
        return categories

    def get_category_id(self, category_name: str) -> str | None:
        """Get category ID for selected category name"

        Args:
            category_name (str): The category name

        Returns:
            str | None: The category ID or None if 'Any Category'

        """
        return None if category_name == "Any Category" else self.categories[category_name]

    def get_available_difficulties(self) -> list[str]:
        """ "Get list of available difficulty levels

        Returns:
            list[str]: The difficulties

        """
        return ["Any Difficulty", "Easy", "Medium", "Hard"]

    def get_difficulty_value(self, difficulty_name: str) -> str | None:
        """Get API-compatible difficulty value"

        Args:
            difficulty_name (str): The difficulty name

        Returns:
            str | None: The difficulty value or None if 'Any Difficulty'

        """
        return None if difficulty_name == "Any Difficulty" else difficulty_name.lower()

    def get_available_question_types(self) -> list[str]:
        """Get list of available question types

        Returns:
            list[str]: The question types

        """
        return ["Any Type", "Multiple Choice", "True / False"]

    def get_question_type_value(self, question_type: str) -> str | None:
        """Get API-compatible question type value"""
        return self.TYPE_MAPPING[question_type]
