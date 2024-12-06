import customtkinter as ctk  # type: ignore[import-untyped]


class AppInterface(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Trivia Game")
        self.geometry("800x600")

        # Container for all frames
        self.container: ctk.CTkFrame = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Dictionary to store all frames
        self.frames: dict = {}
