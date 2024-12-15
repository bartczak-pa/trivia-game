"""StartGameFrame class module."""

from typing import Literal

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.view.frames.base_frame import BaseFrame


class StartGameFrame(BaseFrame):
    def _setup_grid(self) -> None:
        """Configure grid layout"""
        self.grid_rowconfigure(0, weight=2)  # Top spacing
        self.grid_rowconfigure((1, 2, 3, 4), weight=0)  # Content rows
        self.grid_rowconfigure(5, weight=3)  # Bottom spacing
        self.grid_columnconfigure((0, 2), weight=1)  # Left and right spacing
        self.grid_columnconfigure(1, weight=0)  # Center column

    def _create_widgets(self) -> None:
        """Create and place widgets"""
        self._init_variables()
        self._create_option_menus()
        self._create_buttons()

    def _init_variables(self) -> None:
        """Initialize StringVar variables"""
        self.category_var = ctk.StringVar(value="Any Category")
        self.difficulty_var = ctk.StringVar(value="Any Difficulty")
        self.type_var = ctk.StringVar(value="Any Type")

    def _create_option_menus(self) -> None:
        """Create and place option menus"""
        categories = self.controller.quiz_brain.get_available_categories()
        difficulties = self.controller.quiz_brain.get_available_difficulties()
        types = self.controller.quiz_brain.get_available_question_types()

        self._create_option_menu("Category:", self.category_var, categories, 2)
        self._create_option_menu("Difficulty:", self.difficulty_var, difficulties, 3)
        self._create_option_menu("Question Type:", self.type_var, types, 4)

    def _create_option_menu(self, label: str, variable: ctk.StringVar, values: list[str], row: int) -> None:
        """Create and place an option menu with label"""
        ctk.CTkLabel(self, text=label).grid(row=row, column=1, pady=(20 if row == 2 else 5), sticky="w")
        ctk.CTkOptionMenu(self, variable=variable, values=values, width=200).grid(
            row=row, column=1, pady=(20 if row == 2 else 5)
        )

    def _create_buttons(self) -> None:
        """Create and place buttons"""
        ctk.CTkButton(self, text="Start Game", command=self._start_game, width=200).grid(row=5, column=1, pady=30)
        ctk.CTkButton(
            self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenuFrame"), width=200
        ).grid(row=6, column=1, pady=(0, 30))

    def get_selected_values(
        self,
    ) -> tuple[str | None, Literal["easy", "medium", "hard"] | None, Literal["multiple", "boolean"] | None]:
        """Get currently selected values from option menus

        Returns:
            tuple: (category_id, difficulty_value, question_type)
                - category_id: The category ID or None for 'Any Category'
                - difficulty_value: The difficulty level or None for 'Any Difficulty'
                - question_type: The question type or None for 'Any Type'

        """
        category_id = self.controller.quiz_brain.get_category_id(self.category_var.get())
        difficulty_value = self.controller.quiz_brain.get_difficulty_value(self.difficulty_var.get())
        question_type = self.controller.quiz_brain.get_question_type_value(self.type_var.get())
        return category_id, difficulty_value, question_type  # type: ignore[return-value]

    def _start_game(self) -> None:
        """Start the game with selected options"""
        category_id, difficulty_value, question_type = self.get_selected_values()
        self.controller.quiz_brain.load_questions(category_id, difficulty_value, question_type)
