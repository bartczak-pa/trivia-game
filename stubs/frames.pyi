from collections.abc import Callable

import customtkinter as ctk

from trivia_game.app_interface import AppInterface

class MainMenuFrame(ctk.CTkFrame):
    button_mapping: dict[str, Callable[[], None]]

    def __init__(self, parent: ctk.CTkFrame, controller: AppInterface) -> None: ...
    def _setup_main_buttons(self) -> None: ...

class StartGameFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppInterface) -> None: ...

class ScoreboardFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppInterface) -> None: ...

class AppSettingsFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppInterface) -> None: ...

FRAME_CLASSES: tuple[type[ctk.CTkFrame], ...]
