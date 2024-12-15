from typing import ClassVar, Literal, Protocol, runtime_checkable

import customtkinter as ctk

# Import the protocols
from trivia_game.models import Question


@runtime_checkable
class AppControllerProtocol(Protocol):
    # ... existing protocol definition ...
    pass


@runtime_checkable
class TriviaGameProtocol(Protocol):
    # ... existing protocol definition ...
    pass


class TestAppControllerProtocol:
    def test_show_frame(self):
        class MockAppController:
            quiz_brain: TriviaGameProtocol

            def __init__(self):
                self.quiz_brain = None  # type: ignore[expected-type]

            def show_frame(self, frame_class: type[ctk.CTkFrame] | str) -> None:
                pass

            def quit(self) -> None:
                pass

            def show_error(self, message: str) -> None:
                pass

        controller = MockAppController()
        assert isinstance(controller, AppControllerProtocol)


class TestTriviaGameProtocol:
    class MockTriviaGame:
        categories: ClassVar[dict[str, str]] = {}
        current_question: ClassVar[Question | None] = None
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

    def test_trivia_game_protocol(self):
        game = self.MockTriviaGame()
        assert isinstance(game, TriviaGameProtocol)

    def test_trivia_game_method_signatures(self):
        game = self.MockTriviaGame()
        assert callable(game.get_available_categories)
        assert callable(game.get_category_id)
        assert callable(game.get_available_difficulties)
        assert callable(game.get_difficulty_value)
        assert callable(game.get_available_question_types)
        assert callable(game.get_question_type_value)
        assert callable(game.load_questions)
        assert callable(game.show_next_question)
        assert callable(game.check_answer)
