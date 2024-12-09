from typing import Protocol

import customtkinter as ctk  # type: ignore[import-untyped]


class AppControllerProtocol(Protocol):
    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None: ...

    """Show a frame for the given class"""

    def quit(self) -> None: ...

    """Quit the application"""

    def show_error(self, message: str) -> None: ...

    """Show an error message

            Args:
                message (str): The error message to display
            """


class TriviaGameProtocol(Protocol):
    def _load_categories(self) -> None: ...
