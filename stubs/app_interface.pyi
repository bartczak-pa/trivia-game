import customtkinter as ctk

class AppInterface(ctk.CTk):
    container: ctk.CTkFrame
    frames: dict[type[ctk.CTkFrame], ctk.CTkFrame]

    def __init__(self) -> None: ...
    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None: ...
