from typing import Protocol

import customtkinter as ctk  # type: ignore[import-untyped]


class AppControllerProtocol(Protocol):
    quiz_brain: "TriviaGameProtocol"

    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None: ...
    def quit(self) -> None: ...
    def show_error(self, message: str) -> None: ...


class TriviaGameProtocol(Protocol):
    def _load_categories(self) -> None: ...
    def get_categories_with_any(self) -> list[str]: ...
    def get_category_id(self, category_name: str) -> str | None: ...

    def get_difficulties(self) -> list[str]: ...
    def get_question_types(self) -> list[str]: ...
