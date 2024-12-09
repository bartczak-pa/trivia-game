from collections.abc import Callable

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.base_types import AppControllerProtocol


class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None:
        """Create the main menu frame

        Args:
            parent (ctk.CTkFrame): The parent frame
            controller (AppInterface): The main application controller
        """
        super().__init__(parent)

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)  # Top spacing
        self.grid_rowconfigure(5, weight=1)  # Bottom spacing
        self.grid_columnconfigure(0, weight=1)  # Center buttons

        self.button_mapping: dict[str, Callable[[], None]] = {
            "Start Game": lambda: controller.show_frame(StartGameFrame),
            "High Scores": lambda: controller.show_frame(ScoreboardFrame),
            "Settings": lambda: controller.show_frame(AppSettingsFrame),
            "Exit": controller.quit,
        }
        self._setup_main_buttons()

    def _setup_main_buttons(self) -> None:
        """Create and pack the main buttons"""
        for idx, (text, command) in enumerate(self.button_mapping.items(), start=1):
            button = ctk.CTkButton(self, text=text, command=command)
            button.grid(row=idx, column=0, pady=10, padx=20, sticky="ew")


class StartGameFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None:
        """Create the start game frame

        Args:
            parent (ctk.CTkFrame): The parent frame
            controller (AppInterface): The main application controller

        """
        super().__init__(parent)

        # Configure frame grid
        self.grid_rowconfigure(0, weight=2)  # Top spacing
        self.grid_rowconfigure((1, 2, 3, 4), weight=0)  # Content rows
        self.grid_rowconfigure(5, weight=3)  # Bottom spacing
        self.grid_columnconfigure((0, 2), weight=1)  # Left and right spacing
        self.grid_columnconfigure(1, weight=0)  # Center column

        # Game options
        self.category_var = ctk.StringVar(value="Any Category")
        self.difficulty_var = ctk.StringVar(value="Any Difficulty")
        self.type_var = ctk.StringVar(value="Any Type")

        # Option menus
        categories = controller.quiz_brain.get_categories_with_any()
        difficulties = ["Any Difficulty", "Easy", "Medium", "Hard"]
        types = ["Any Type", "Multiple Choice", "True/False"]

        # Category selection
        ctk.CTkLabel(self, text="Category:").grid(row=2, column=1, pady=(20, 5), sticky="w")

        ctk.CTkOptionMenu(self, variable=self.category_var, values=categories, width=200).grid(
            row=2, column=1, pady=(20, 5)
        )

        # Difficulty selection
        ctk.CTkLabel(self, text="Difficulty:").grid(row=3, column=1, pady=5, sticky="w")

        ctk.CTkOptionMenu(self, variable=self.difficulty_var, values=difficulties, width=200).grid(
            row=3, column=1, pady=5
        )

        # Question type selection
        ctk.CTkLabel(self, text="Question Type:").grid(row=4, column=1, pady=5, sticky="w")

        ctk.CTkOptionMenu(self, variable=self.type_var, values=types, width=200).grid(row=4, column=1, pady=5)

        # Back button
        ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_frame(MainMenuFrame), width=200).grid(
            row=6, column=1, pady=(0, 30)
        )  # More bottom padding


class ScoreboardFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None:
        """Create the scoreboard frame

        Args:
            parent (ctk.CTkFrame): The parent frame
            controller (AppInterface): The main application controller
        """
        super().__init__(parent)
        # Add a label to test the frame
        ctk.CTkLabel(self, text="Scoreboard Frame").pack(pady=20)

        # Back button
        ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=10)


class AppSettingsFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None:
        """Create the settings frame

        Args:
            parent (ctk.CTkFrame): The parent frame
            controller (AppInterface): The main application controller
        """
        super().__init__(parent)
        # Add a label to test the frame
        ctk.CTkLabel(self, text="Settings Frame").pack(pady=20)

        # Back button
        ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=10)


# Frame classes tuple for initialization
FRAME_CLASSES: tuple[type[ctk.CTkFrame], ...] = (MainMenuFrame, StartGameFrame, ScoreboardFrame, AppSettingsFrame)
