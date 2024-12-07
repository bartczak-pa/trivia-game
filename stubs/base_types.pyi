from typing import Protocol

import customtkinter as ctk

class AppControllerProtocol(Protocol):
    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None: ...
    def quit(self) -> None: ...

class TriviaGameProtocol(Protocol):
    pass
