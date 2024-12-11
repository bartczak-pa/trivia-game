from tkinter import messagebox as CTkMessagebox

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.base_types import AppControllerProtocol
from trivia_game.quiz_brain import QuizBrain
from trivia_game.view.frames import FRAME_CLASSES


class AppInterface(ctk.CTk, AppControllerProtocol):
    def __init__(self) -> None:
        """Create the main application interface"""
        super().__init__()

        self.title("Trivia Game")
        self.geometry("800x600")

        # Initialize the quiz brain
        self.quiz_brain = QuizBrain(self)

        # Configure the main window grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Container for all frames
        self.container: ctk.CTkFrame = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        # Configure container grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store all frames
        self.frames: dict[type[ctk.CTkFrame], ctk.CTkFrame] = {}

        # Create and store all frames
        for F in FRAME_CLASSES:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(FRAME_CLASSES[0])

    def show_frame(self, frame_name: str | type[ctk.CTkFrame]) -> None:
        if isinstance(frame_name, str):
            frame_class = next(f for f in FRAME_CLASSES if f.__name__ == frame_name)
        else:
            frame_class = frame_name
        frame = self.frames[frame_class]
        frame.tkraise()

    def show_error(self, message: str) -> None:
        """Show an error message

        Args:
            message (str): The error message to display
        """
        CTkMessagebox.showerror("Error", message)

    def quit(self) -> None:
        """Quit the application"""
        self.destroy()
