import customtkinter as ctk  # type: ignore[import-untyped]

class ScoreDialog(ctk.CTkInputDialog):
    def __init__(self, parent: ctk.CTk, score: int) -> None: ...
