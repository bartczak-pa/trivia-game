import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.view.frame_registry import FrameRegistry


class AppInterface(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Trivia Game")
        self.geometry("800x600")

        # Container for all frames
        self.container: ctk.CTkFrame = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Dictionary to store all frames
        self.frames: dict[type[ctk.CTkFrame], ctk.CTkFrame] = {}

        # Use FrameRegistry to get all registered frames
        for frame_class in FrameRegistry.get_all_frames():
            frame = frame_class(self.container, self)  # type: ignore[unused-ignore]
            self.frames[frame_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None:
        """Show a frame for the given class

        Args:
            frame_class (type[ctk.CTkFrame]): The class of the frame to show

        Returns:
            None
        """
        frame = self.frames[frame_class]
        frame.tkraise()
