import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.view.frames.base_frame import BaseFrame


class BaseQuizFrame(BaseFrame):
    """Base class for quiz question frames"""

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
        self.question_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray25"))
        self.question_frame.grid(row=2, column=1, pady=20, padx=40, sticky="nsew")

    def _create_question_label(self) -> None:
        """Create and place question label"""
        self.question_label = ctk.CTkLabel(
            self.question_frame, text="Question text here", wraplength=600, pady=20, padx=20
        )
        self.question_label.grid(row=0, column=0, sticky="nsew")

    def _handle_answer(self, answer: str) -> None:
        """Handle user's answer selection

        Args:
            answer (str): The selected answer
        """
        # Base implementation - override in subclasses if needed
        print(f"Selected answer: {answer}")  # For testing


class TrueFalseQuizFrame(BaseQuizFrame):
    """Frame for True/False quiz questions"""

    def _setup_grid(self) -> None:
        """Configure grid layout"""
        super()._setup_grid()

    def _create_widgets(self) -> None:
        """Create and place widgets"""
        super()._create_widgets()
        self._create_answer_buttons()

    def _create_answer_buttons(self) -> None:
        """Create True/False buttons"""
        button_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=1)

        for text in ["True", "False"]:
            ctk.CTkButton(button_frame, text=text, command=lambda t=text: self._handle_answer(t), width=200).grid(
                row=0, column=0 if text == "True" else 1, padx=10, pady=20
            )
