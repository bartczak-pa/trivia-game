import customtkinter as ctk

from trivia_game.base_types import AppControllerProtocol

class AppSettingsFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...
    def _setup_grid(self) -> None: ...
    def _create_widgets(self) -> None: ...
