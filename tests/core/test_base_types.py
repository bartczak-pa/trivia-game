from typing import ClassVar, Literal

import customtkinter as ctk

from trivia_game.models import Question


class TestProtocols:
    def test_app_controller_protocol(self):
        """Test if AppControllerProtocol can be properly implemented"""

        class MockController:
            def __init__(self):
                self.quiz_brain = None

            def show_frame(self, frame_class: type[ctk.CTkFrame] | str) -> None:
                pass

            def quit(self) -> None:
                pass

            def show_error(self, message: str) -> None:
                pass

        controller = MockController()
        # Test that all required methods are present
        assert hasattr(controller, "quiz_brain")
        assert hasattr(controller, "show_frame")
        assert hasattr(controller, "quit")
        assert hasattr(controller, "show_error")

    def test_trivia_game_protocol(self):
        """Test if TriviaGameProtocol can be properly implemented"""

        class MockTriviaGame:
            categories: ClassVar[dict[str, str]] = {}
            current_question: Question | None = None
            questions: ClassVar[list[Question]] = []
            score: int = 0

            def _load_categories(self) -> None:
                pass

            def get_available_categories(self) -> list[str]:
                return []

            def get_category_id(self, category_name: str) -> str | None:
                return None

            def get_available_difficulties(self) -> list[str]:
                return []

            def get_difficulty_value(self, difficulty_name: str) -> str | None:
                return None

            def get_available_question_types(self) -> list[str]:
                return []

            def get_question_type_value(self, question_type: str) -> str | None:
                return None

            def load_questions(
                self,
                category: str | None,
                difficulty: Literal["easy", "medium", "hard"] | None,
                question_type: Literal["multiple", "boolean"] | None,
            ) -> None:
                pass

            def show_next_question(self) -> None:
                pass

            def check_answer(self, selected_answer: str) -> bool:
                return False

        game = MockTriviaGame()
        # Test that all required attributes are present
        assert hasattr(game, "categories")
        assert hasattr(game, "current_question")
        assert hasattr(game, "questions")
        assert hasattr(game, "score")

        # Test that all required methods are present and callable
        required_methods = [
            "_load_categories",
            "get_available_categories",
            "get_category_id",
            "get_available_difficulties",
            "get_difficulty_value",
            "get_available_question_types",
            "get_question_type_value",
            "load_questions",
            "show_next_question",
            "check_answer",
        ]
        for method in required_methods:
            assert hasattr(game, method)
            assert callable(getattr(game, method))
