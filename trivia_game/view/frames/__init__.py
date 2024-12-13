from trivia_game.view.frames.app_settings import AppSettingsFrame
from trivia_game.view.frames.main_menu import MainMenuFrame
from trivia_game.view.frames.quiz_frames import MultipleChoiceQuizFrame, TrueFalseQuizFrame
from trivia_game.view.frames.score_board import ScoreboardFrame
from trivia_game.view.frames.start_game import StartGameFrame

FRAME_CLASSES = (
    MainMenuFrame,
    StartGameFrame,
    ScoreboardFrame,
    AppSettingsFrame,
    TrueFalseQuizFrame,
    MultipleChoiceQuizFrame,
)
