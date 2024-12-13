from typing import ClassVar, Literal

from trivia_game.base_types import AppControllerProtocol, TriviaGameProtocol
from trivia_game.exceptions import CategoryError
from trivia_game.models import Question
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
        self.current_question: Question | None = None
        self.questions: list[Question] = []
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

    def get_difficulty_value(self, difficulty_name: str) -> Literal["easy", "medium", "hard"] | None:
        """Get API-compatible difficulty value"

        Args:
            difficulty_name (str): The difficulty name

        Returns:
            Literal["easy", "medium", "hard"] | None: The difficulty value
        """
        return None if difficulty_name == "Any Difficulty" else difficulty_name.lower()  # type: ignore[return-value]

    def get_available_question_types(self) -> list[str]:
        """Get list of available question types

        Returns:
            list[str]: The question types

        """
        return ["Any Type", "Multiple Choice", "True / False"]

    def get_question_type_value(self, question_type: str) -> str | None:
        """Get API-compatible question type value"""
        return self.TYPE_MAPPING[question_type]

    def load_questions(
        self,
        category: str | None,
        difficulty: Literal["easy", "medium", "hard"] | None,
        question_type: Literal["multiple", "boolean"] | None,
    ) -> None:
        """Load questions from the API

        Args:
            category (str | None): The category ID or None for 'Any Category'
            difficulty (str | None): The difficulty level or None for 'Any Difficulty'
            question_type (str | None): The question type or None for 'Any Type'
        """
        try:
            self.questions = self.api_client.fetch_questions(
                category=category, difficulty=difficulty, question_type=question_type
            )
            print(f"Fetched questions: {self.questions}")
            self.score = 0
            self.show_next_question()
        except Exception as e:
            msg: str = f"Error loading questions: {e}"
            self.controller.show_error(msg)

    def show_next_question(self) -> None:
        """Show next question or end game if no more questions"""
        if not self.questions:
            print("No more questions, showing scoreboard")  # TODO: Remove this line
            self.controller.show_frame("ScoreboardFrame")  # TODO: Work on ScoreboardFrame
            return

        self.current_question = self.questions.pop(0)
        print(f"Showing question: {self.current_question}")
        self.controller.show_frame(
            "TrueFalseQuizFrame" if self.current_question.type == "boolean" else "MultipleChoiceQuizFrame"
        )

    def check_answer(self, selected_answer: str) -> bool:
        """Check if selected answer is correct

        Args:
            selected_answer (str): The selected answer

        Returns:
            bool: True if correct, False otherwise
        """
        if not self.current_question:
            return False

        is_correct: bool = selected_answer == self.current_question.correct_answer

        if is_correct:
            self.score += 100
        return is_correct
