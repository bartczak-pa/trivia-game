import customtkinter as ctk

from trivia_game.base_types import AppControllerProtocol
from trivia_game.quiz_brain import QuizBrain

class AppInterface(ctk.CTk, AppControllerProtocol):
    container: ctk.CTkFrame
    frames: dict[type[ctk.CTkFrame], ctk.CTkFrame]
    quiz_brain: QuizBrain

    def __init__(self) -> None: ...
    def show_frame(self, frame_class: str | type[ctk.CTkFrame]) -> None: ...
    def show_error(self, message: str) -> None: ...
    def quit(self) -> None: ...
