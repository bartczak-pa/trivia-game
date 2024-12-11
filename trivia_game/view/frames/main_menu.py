"""MainMenuFrame class module"""

from typing import Callable

import customtkinter as ctk  # type: ignore[import-untyped]

from .base_frame import BaseFrame


class MainMenuFrame(BaseFrame):
    def _setup_grid(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_widgets(self) -> None:
        self.button_mapping: dict[str, Callable[[], None]] = {
            "Start Game": lambda: self.controller.show_frame("StartGameFrame"),
            "High Scores": lambda: self.controller.show_frame("ScoreboardFrame"),
            "Settings": lambda: self.controller.show_frame("AppSettingsFrame"),
            "Exit": self.controller.quit,
        }
        self._setup_main_buttons()

    def _setup_main_buttons(self) -> None:
        for idx, (text, command) in enumerate(self.button_mapping.items(), start=1):
            button = ctk.CTkButton(self, text=text, command=command)
            button.grid(row=idx, column=0, pady=10, padx=20, sticky="ew")
