from typing import ClassVar

import customtkinter as ctk

class FrameRegistry:
    _frames: ClassVar[dict[str, type[ctk.CTkFrame]]]

    @classmethod
    def register(cls, name: str, frame_class: type[ctk.CTkFrame]) -> None: ...
    @classmethod
    def get_frame(cls, name: str) -> type[ctk.CTkFrame]: ...
    @classmethod
    def get_all_frames(cls) -> tuple[type[ctk.CTkFrame], ...]: ...
