from collections.abc import Callable

import customtkinter as ctk

from trivia_game.base_types import AppControllerProtocol

class MainMenuFrame(ctk.CTkFrame):
    button_mapping: dict[str, Callable[[], None]]

    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...
    def _setup_main_buttons(self) -> None: ...

class StartGameFrame(ctk.CTkFrame):
    category_var: ctk.StringVar
    difficulty_var: ctk.StringVar
    type_var: ctk.StringVar

    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...
    def get_selected_values(self) -> tuple[str | None, str | None, str | None]: ...

class ScoreboardFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...

class AppSettingsFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...

FRAME_CLASSES: tuple[type[ctk.CTkFrame], ...]
