from tkinter import messagebox as CTkMessagebox

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.base_types import AppControllerProtocol
from trivia_game.quiz_brain import QuizBrain
from trivia_game.view.frames import FRAME_CLASSES, MainMenuFrame


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

        self.show_frame(MainMenuFrame)

    def show_frame(self, frame_class: str | type[ctk.CTkFrame]) -> None:
        """Show a frame for the given class or frame name"""
        frame_type: type[ctk.CTkFrame]
        if isinstance(frame_class, str):
            try:
                frame_type = next(f for f in FRAME_CLASSES if f.__name__ == frame_class)
            except StopIteration as e:
                stop_iter_msg: str = f"Frame '{frame_class}' not found"
                raise ValueError(stop_iter_msg) from e
        else:
            frame_type = frame_class

        try:
            frame = self.frames[frame_type]
            frame.tkraise()
            # Refresh frame if it has a refresh method
            if hasattr(frame, "refresh"):
                frame.refresh()
        except KeyError as exc:
            key_err_msg: str = f"Frame '{frame_type.__name__}' not initialized"
            raise ValueError(key_err_msg) from exc

    def show_error(self, message: str) -> None:
        """Show an error message

        Args:
            message (str): The error message to display
        """
        CTkMessagebox.showerror("Error", message)

    def quit(self) -> None:
        """Quit the application"""
        self.destroy()
