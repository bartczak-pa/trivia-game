from unittest.mock import Mock

import pytest

from trivia_game.view.frames import AppSettingsFrame, MainMenuFrame, MultipleChoiceQuizFrame, StartGameFrame


@pytest.fixture
def mock_quiz_brain(mocker):
    """Create mock quiz brain with required methods"""
    mock = mocker.Mock()
    mock.get_available_categories.return_value = ["Any Category", "History", "Science"]
    mock.get_available_difficulties.return_value = ["Any Difficulty", "Easy", "Medium", "Hard"]
    mock.get_available_question_types.return_value = ["Any Type", "Multiple Choice", "True/False"]
    mock.get_category_id.return_value = "9"
    mock.get_difficulty_value.return_value = "easy"
    mock.get_question_type_value.return_value = "multiple"
    return mock


@pytest.fixture
def mock_controller(mock_quiz_brain):
    """Create mock controller with quiz brain"""
    controller = Mock()
    controller.quiz_brain = mock_quiz_brain
    return controller


@pytest.fixture
def main_menu_frame(mock_controller):
    """Create MainMenuFrame instance"""
    return MainMenuFrame(None, mock_controller)


@pytest.fixture
def app_settings_frame(mock_controller):
    """Create AppSettingsFrame instance"""
    return AppSettingsFrame(None, mock_controller)


@pytest.fixture
def start_game_frame(mock_controller):
    """Create StartGameFrame instance"""
    return StartGameFrame(None, mock_controller)


@pytest.fixture
def scoreboard_frame(mock_controller):
    from trivia_game.view.frames.score_board import ScoreboardFrame

    return ScoreboardFrame(None, mock_controller)


@pytest.fixture
def multiple_choice_frame(mock_controller, mocker):
    """Create a MultipleChoiceQuizFrame instance"""
    # Mock the current question's all_answers method to return a list
    mock_controller.quiz_brain.current_question.all_answers.return_value = ["A", "B", "C", "D"]

    # Patch random.shuffle to avoid actual shuffling
    mocker.patch("random.shuffle")

    return MultipleChoiceQuizFrame(None, mock_controller)
