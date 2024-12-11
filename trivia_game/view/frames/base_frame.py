"""BaseFrame class module"""

import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.base_types import AppControllerProtocol


class BaseFrame(ctk.CTkFrame):
    """Base class for all frames with common functionality"""

    def __init__(self, parent: ctk.CTkFrame, controller: AppControllerProtocol) -> None:
        """Create the base frame

        Args:
            parent (ctk.CTkFrame): The parent frame
            controller (AppControllerProtocol): The main application controller
        """

        super().__init__(parent)
        self.controller = controller
        self._setup_grid()
        self._create_widgets()

    def _setup_grid(self) -> None:
        """Configure grid layout - override in subclasses"""
        pass

    def _create_widgets(self) -> None:
        """Create and place widgets - override in subclasses"""
        pass
