import customtkinter as ctk  # type: ignore[import-untyped]

from trivia_game.view.frames import FRAME_CLASSES, MainMenuFrame


class AppInterface(ctk.CTk):
    def __init__(self) -> None:
        """Create the main application interface"""
        super().__init__()

        self.title("Trivia Game")
        self.geometry("800x600")

        # Configure the main window grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Container for all frames
        self.container: ctk.CTkFrame = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        # Configure container grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store all frames
        self.frames: dict[type[ctk.CTkFrame], ctk.CTkFrame] = {}

        # Create and store all frames
        for F in FRAME_CLASSES:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenuFrame)

    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None:
        """Show a frame for the given class

        Args:
            frame_class (type[ctk.CTkFrame]): The class of the frame to show
        """
        frame = self.frames[frame_class]
        frame.tkraise()

    def quit(self) -> None:
        """Quit the application"""
        self.destroy()
