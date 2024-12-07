from typing import Protocol

import customtkinter as ctk  # type: ignore[import-untyped]


class AppControllerProtocol(Protocol):
    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None: ...

    """Show a frame for the given class"""

    def quit(self) -> None: ...

    """Quit the application"""


class TriviaGameProtocol(Protocol):
    pass
