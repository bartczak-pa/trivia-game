"""ScoreboardFrame class module"""

import json
from datetime import datetime
from pathlib import Path

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.view.frames.base_frame import BaseFrame


class ScoreboardFrame(BaseFrame):
    def _setup_grid(self) -> None:
        """Configure grid layout"""
        self.grid_rowconfigure(0, weight=1)  # Top spacing
        self.grid_rowconfigure(2, weight=1)  # Bottom spacing
        self.grid_columnconfigure(0, weight=1)

    def _create_widgets(self) -> None:
        """Create and place widgets"""
        # Create scrollable frame for scores
        self.scores_frame = ctk.CTkScrollableFrame(self)
        self.scores_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        # Create back button
        ctk.CTkButton(self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenuFrame")).grid(
            row=3, column=0, pady=10
        )

        self.load_scores()

    def load_scores(self) -> None:
        """Load and display scores"""
        try:
            scores_file = Path("scores.json")
            if not scores_file.exists():
                self._display_no_scores()
                return

            with scores_file.open() as f:
                scores = json.load(f)

            if not scores:
                self._display_no_scores()
                return

            self._display_scores(scores)

        except Exception as e:
            self.controller.show_error(f"Error loading scores: {e!s}")
            self._display_no_scores()

    def _display_scores(self, scores: list[dict]) -> None:
        """Display scores in the scrollable frame"""
        # Clear previous widgets
        for widget in self.scores_frame.winfo_children():
            widget.destroy()

        # Create header
        self._create_score_row("Player", "Score", "Date", is_header=True)

        # Display scores
        for score in scores:
            self._create_score_row(score["player"], str(score["score"]), score["date"])

    def _create_score_row(self, player: str, score: str, date: str, is_header: bool = False) -> None:
        """Create a row in the score table"""
        font = ("Arial", 12, "bold") if is_header else ("Arial", 12)
        formatted_date = date if is_header else self._format_date(date)

        # Player name
        ctk.CTkLabel(
            self.scores_frame,
            text=player,
            font=font,
            width=150,
            anchor="center",  # Center the text
        ).grid(row=self._get_next_row(), column=0, padx=5, pady=5, sticky="ew")

        # Score
        ctk.CTkLabel(
            self.scores_frame,
            text=score,
            font=font,
            width=100,
            anchor="center",  # Center the text
        ).grid(row=self._get_current_row(), column=1, padx=5, pady=5, sticky="ew")

        # Date
        ctk.CTkLabel(
            self.scores_frame,
            text=formatted_date,
            font=font,
            width=150,
            anchor="center",  # Center the text
        ).grid(row=self._get_current_row(), column=2, padx=5, pady=5, sticky="ew")

    def _display_no_scores(self) -> None:
        """Display message when no scores are available"""
        ctk.CTkLabel(self.scores_frame, text="No scores available", font=("Arial", 14)).grid(
            row=0, column=0, padx=20, pady=20
        )

    def _get_next_row(self) -> int:
        """Get next available row in the scores frame"""
        return len(self.scores_frame.winfo_children()) // 3

    def _get_current_row(self) -> int:
        """Get current row number"""
        return (len(self.scores_frame.winfo_children()) - 1) // 3

    def _format_date(self, date_str: str) -> str:
        """Convert ISO format date to readable format

        Args:
            date_str (str): Date string in ISO format

        Returns:
            str: Date formatted as 'DD Month YYYY HH:MM'
        """
        parsed_date = datetime.fromisoformat(date_str)
        return parsed_date.strftime("%d %B %Y %H:%M")

    def refresh(self) -> None:
        """Refresh the scoreboard display"""
        # Clear previous widgets
        for widget in self.scores_frame.winfo_children():
            widget.destroy()

        # Reload and display scores
        self.load_scores()
