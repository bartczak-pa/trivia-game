import random

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
        self._clear_previous_widgets()
        self._create_score_label()
        self._create_question_frame()
        self._create_question_label()
        self.display_question()

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

    def _create_answer_buttons(self) -> None:
        """Create answer buttons - to be implemented by child classes"""
        raise NotImplementedError("Child classes must implement _create_answer_buttons")

    def _handle_answer(self, answer: str) -> None:
        """Handle user's answer selection. Base implementation - override in subclasses if needed

        Args:
            answer (str): The selected answer
        """
        is_correct = self.controller.quiz_brain.check_answer(answer)

        # Update score display
        self.update_score()

        # Show visual feedback
        self.question_frame.configure(fg_color="green" if is_correct else "red")
        # Wait and continue
        self.after(1000, lambda _=None: self._reset_and_continue())

    def _reset_and_continue(self) -> None:
        """Reset frame color and show next question"""
        self.question_frame.configure(fg_color=("gray85", "gray25"))
        self.controller.quiz_brain.show_next_question()

    def display_question(self) -> None:
        """Display current question"""
        if current_question := self.controller.quiz_brain.current_question:
            question_text = current_question.question
            self.question_label.configure(text=question_text)

    def refresh(self) -> None:
        """Refresh frame content. Base implementation - override in subclasses if needed"""
        self.display_question()
        self._create_answer_buttons()

    def _clear_previous_widgets(self) -> None:
        """Clear all widgets except the question frame"""
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.question_frame:
                widget.destroy()

    def _create_score_label(self) -> None:
        """Create and place score label"""
        self.score_label: ctk.CTkLabel = ctk.CTkLabel(
            self, text=f"Score: {self.controller.quiz_brain.score}", font=("Arial", 16, "bold")
        )
        self.score_label.grid(row=1, column=1, pady=10)

    def update_score(self) -> None:
        """Update score label"""
        self.score_label.configure(text=f"Score: {self.controller.quiz_brain.score}")


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

        if _ := self.controller.quiz_brain.current_question:
            for text in ["True", "False"]:
                ctk.CTkButton(button_frame, text=text, command=lambda t=text: self._handle_answer(t), width=200).grid(
                    row=0, column=0 if text == "True" else 1, padx=10, pady=20
                )


class MultipleChoiceQuizFrame(BaseQuizFrame):
    def _setup_grid(self) -> None:
        """Configure grid layout"""
        super()._setup_grid()

    def _create_widgets(self) -> None:
        """Create and place widgets"""
        super()._create_widgets()
        self._create_answer_buttons()

    def _create_answer_buttons(self) -> None:
        """Create multiple choice buttons"""
        button_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=1)

        if current_question := self.controller.quiz_brain.current_question:
            answers = current_question.all_answers()
            random.shuffle(answers)

            for idx, answer in enumerate(answers):
                row, col = divmod(idx, 2)
                ctk.CTkButton(
                    button_frame, text=answer, command=lambda a=answer: self._handle_answer(a), width=200
                ).grid(row=row, column=col, padx=10, pady=10)
