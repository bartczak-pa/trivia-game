import customtkinter as ctk

from trivia_game.base_types import AppControllerProtocol

class StartGameFrame(ctk.CTkFrame):
    category_var: ctk.StringVar
    difficulty_var: ctk.StringVar
    type_var: ctk.StringVar

    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...
    def set_categories(self, categories: list[str]) -> None: ...
