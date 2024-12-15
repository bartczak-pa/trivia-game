import customtkinter as ctk  # type: ignore[import-untyped]


class ScoreDialog(ctk.CTkInputDialog):
    def __init__(self, parent: ctk.CTkInputDialog, score: int):
        super().__init__(text=f"Congratulations! Your score: {score}\nEnter your name:", title="Game Over")
