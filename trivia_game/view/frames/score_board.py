"""ScoreboardFrame class module"""

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.view.frames.base_frame import BaseFrame


class ScoreboardFrame(BaseFrame):
    def _setup_grid(self) -> None:
        """Configure grid layout"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_widgets(self) -> None:
        """Create and place widgets"""
        ctk.CTkLabel(self, text="Scoreboard Frame").grid(row=1, column=0, pady=20)

        ctk.CTkButton(self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenuFrame")).grid(
            row=1, column=0, pady=10
        )
