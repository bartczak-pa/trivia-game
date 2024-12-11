from typing import Callable

import customtkinter as ctk

from trivia_game.base_types import AppControllerProtocol

class MainMenuFrame(ctk.CTkFrame):
    button_mapping: dict[str, Callable[[], None]]

    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...
    def _setup_main_buttons(self) -> None: ...
