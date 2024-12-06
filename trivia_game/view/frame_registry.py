"""FrameRegistry class to register and get all frames in the application."""

from typing import ClassVar

import customtkinter as ctk  # type: ignore[import-untyped]


class FrameRegistry:
    """Class to register and get all frames in the application"""

    _frames: ClassVar[dict[str, type[ctk.CTkFrame]]] = {}

    @classmethod
    def register(cls, name: str, frame_class: type[ctk.CTkFrame]) -> None:
        """Register a frame class with a name

        Args:
            name (str): The name of the frame
            frame_class (type[ctk.CTkFrame]): The class of the frame to register

        Returns:
            None
        """
        cls._frames[name] = frame_class

    @classmethod
    def get_frame(cls, name: str) -> type[ctk.CTkFrame]:
        """Get a frame class by name

        Args:
            name (str): The name of the frame to get

        Returns:
            type[ctk.CTkFrame]: The class of the frame
        """
        return cls._frames[name]

    @classmethod
    def get_all_frames(cls) -> tuple[type[ctk.CTkFrame], ...]:
        """Get all registered frame classes

        Returns:
            tuple[type[ctk.CTkFrame], ...]: A tuple of all registered frame classes

        """
        return tuple(cls._frames.values())  # type: ignore[unused-ignore]
