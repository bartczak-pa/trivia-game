import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.view.frames.base_frame import BaseFrame


class BaseQuizFrame(BaseFrame):
    def _setup_grid(self) -> None:
        """Configure grid layout"""
        self.grid_rowconfigure((0, 4), weight=1)  # Top and bottom spacing
        self.grid_rowconfigure((1, 2, 3), weight=0)  # Content rows
        self.grid_columnconfigure((0, 2), weight=1)  # Side spacing
        self.grid_columnconfigure(1, weight=0)  # Center content

    def _create_widgets(self) -> None:
        """Create and place widgets"""
        self._create_question_frame()
        self._create_question_label()

    def _create_question_frame(self) -> None:
        """Create and place frame for question"""
        self.question_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray25")).grid(
            row=2, column=1, pady=20, padx=40, sticky="nsew"
        )

    def _create_question_label(self) -> None:
        """Create and place question label"""
        self.question_label = ctk.CTkLabel(
            self.question_frame, text="Question text here", wraplength=600, pady=20, padx=20
        ).grid(row=0, column=0, sticky="nsew")

    def _handle_answer(self, answer: str) -> None:
        """Handle user's answer selection

        Args:
            answer (str): The selected answer
        """
        # Base implementation - override in subclasses if needed
        print(f"Selected answer: {answer}")  # For testing
