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
        self._create_question_label()
        self._create_answer_buttons()

    def _create_question_label(self) -> None:
        """Create and place question label"""
        self.question_label: ctk.CTkLabel = ctk.CTkLabel(self, text="Question text here", wraplength=600)
        self.question_label.grid(row=1, column=1, pady=20)

    def _create_answer_buttons(self) -> None:
        """Create answer buttons - override in subclasses"""
        pass

    def _handle_answer(self, answer: str) -> None:
        """Handle answer selection - override in subclasses

        Args:
            answer (str): The selected answer
        """
        print(f"Selected answer: {answer}")  # For testing


class TrueFalseQuizFrame(BaseQuizFrame):
    def _create_answer_buttons(self) -> None:
        """Create True/False buttons"""
        button_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=1)

        ctk.CTkButton(button_frame, text="True", command=lambda: self._handle_answer("True"), width=200).grid(
            row=0, column=0, padx=10, pady=20
        )

        ctk.CTkButton(button_frame, text="False", command=lambda: self._handle_answer("False"), width=200).grid(
            row=0, column=1, padx=10, pady=20
        )


class MultipleChoiceQuizFrame(BaseQuizFrame):
    def _create_answer_buttons(self) -> None:
        """Create multiple choice buttons"""
        button_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=1)

        # TODO: Replace with actual answers
        for idx, answer in enumerate(["A", "B", "C", "D"]):
            row = idx // 2
            col = idx % 2
            ctk.CTkButton(button_frame, text=answer, command=lambda a=answer: self._handle_answer(a), width=200).grid(
                row=row, column=col, padx=10, pady=10
            )
