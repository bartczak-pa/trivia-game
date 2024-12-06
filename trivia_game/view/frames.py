from collections.abc import Callable

import customtkinter as ctk  # type: ignore[import-untyped]


class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: "AppInterface") -> None:  # type: ignore[name-defined]
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
    def __init__(self, parent: ctk.CTkFrame, controller: "AppInterface") -> None:  # type: ignore[name-defined]
        """Create the start game frame

        Args:
            parent (ctk.CTkFrame): The parent frame
            controller (AppInterface): The main application controller

        """
        super().__init__(parent)
        # Add a label to test the frame
        ctk.CTkLabel(self, text="Start Game Frame").pack(pady=20)

        # Back button
        ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_frame(MainMenuFrame)).pack(pady=10)


class ScoreboardFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, controller: "AppInterface") -> None:  # type: ignore[name-defined]
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
    def __init__(self, parent: ctk.CTkFrame, controller: "AppInterface") -> None:  # type: ignore[name-defined]
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
