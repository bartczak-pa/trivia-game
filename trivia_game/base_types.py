from typing import Protocol

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.models import Question


class AppControllerProtocol(Protocol):
    quiz_brain: "TriviaGameProtocol"

    def show_frame(self, frame_class: type[ctk.CTkFrame] | str) -> None: ...
    def quit(self) -> None: ...
    def show_error(self, message: str) -> None: ...


class TriviaGameProtocol(Protocol):
    categories: dict[str, str]
    current_question: Question | None
    questions: list[Question]
    score: int

    def _load_categories(self) -> None: ...
    def get_available_categories(self) -> list[str]: ...
    def get_category_id(self, category_name: str) -> str | None: ...
    def get_available_difficulties(self) -> list[str]: ...
    def get_difficulty_value(self, difficulty_name: str) -> str | None: ...
    def get_available_question_types(self) -> list[str]: ...
    def get_question_type_value(self, question_type: str) -> str | None: ...
