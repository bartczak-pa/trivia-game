import customtkinter as ctk

from trivia_game.base_types import AppControllerProtocol

class ScoreboardFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None: ...
