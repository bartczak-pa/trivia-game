from trivia_game.view.frames.app_settings import AppSettingsFrame
from trivia_game.view.frames.main_menu import MainMenuFrame
from trivia_game.view.frames.score_board import ScoreboardFrame
from trivia_game.view.frames.start_game import StartGameFrame

from .quiz_frames import BaseQuizFrame, MultipleChoiceQuizFrame, TrueFalseQuizFrame

FRAME_CLASSES = (
    MainMenuFrame,
    StartGameFrame,
    ScoreboardFrame,
    AppSettingsFrame,
    BaseQuizFrame,
    MultipleChoiceQuizFrame,
    TrueFalseQuizFrame,
)
