from unittest.mock import Mock

import pytest

from trivia_game.base_types import AppControllerProtocol, TriviaGameProtocol
from trivia_game.trivia_api import TriviaAPIClient
from trivia_game.view.frames import MainMenuFrame
from trivia_game.view.frames.base_frame import BaseFrame


@pytest.fixture
def trivia_client():
    """Fixture for TriviaAPIClient instance"""
    client = TriviaAPIClient()
    yield client
    client.session.close()


@pytest.fixture
def mock_response():
    """Fixture for mocked response"""
    response = Mock()
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_categories_response(mock_response):
    """Fixture for mocked categories response"""
    mock_response.json.return_value = {
        "trivia_categories": [
            {"id": 9, "name": "General Knowledge"},
            {"id": 10, "name": "Entertainment: Books"},
            {"id": 11, "name": "Entertainment: Film"},
        ]
    }
    return mock_response


@pytest.fixture
def mock_questions_success(mock_response):
    """Fixture for successful questions response"""
    mock_response.json.return_value = {
        "response_code": 0,
        "results": [
            {
                "type": "multiple",
                "difficulty": "medium",
                "category": "Entertainment: Video Games",
                "question": "What&apos;s the name of the main character?",
                "correct_answer": "Mario &amp; Luigi",
                "incorrect_answers": ["Bowser &amp; Koopa", "Peach &amp; Daisy", "Wario &amp; Waluigi"],
            },
            {
                "type": "boolean",
                "difficulty": "easy",
                "category": "Science: Computers",
                "question": "Is Python a programming language?",
                "correct_answer": "True",
                "incorrect_answers": ["False"],
            },
        ],
    }
    return mock_response


@pytest.fixture
def mock_controller():
    """Create mock controller with quiz brain"""
    controller = Mock(spec=AppControllerProtocol)
    controller.quiz_brain = Mock(spec=TriviaGameProtocol)

    # Setup quiz brain mock methods
    controller.quiz_brain.get_available_categories.return_value = ["Any Category", "History"]
    controller.quiz_brain.get_available_difficulties.return_value = ["Any Difficulty", "Easy"]
    controller.quiz_brain.get_available_question_types.return_value = ["Any Type", "Multiple Choice"]

    return controller


@pytest.fixture
def mock_customtkinter(mocker):
    """Mock all customtkinter widgets and attributes"""
    mocker.patch("customtkinter.CTkFrame.__init__", return_value=None)
    mocker.patch("customtkinter.CTkButton")
    mocker.patch("customtkinter.CTkLabel")
    mocker.patch("customtkinter.CTkOptionMenu")
    mocker.patch.object(BaseFrame, "tk", create=True)
    mocker.patch.object(BaseFrame, "_w", create=True)

    # Create separate StringVar mocks for each variable
    category_var = mocker.MagicMock()
    category_var.get.return_value = "Any Category"

    difficulty_var = mocker.MagicMock()
    difficulty_var.get.return_value = "Any Difficulty"

    type_var = mocker.MagicMock()
    type_var.get.return_value = "Any Type"

    # Patch StringVar to return different mocks based on initial value
    def mock_stringvar(value=None):
        if value == "Any Category":
            return category_var
        elif value == "Any Difficulty":
            return difficulty_var
        else:
            return type_var

    mocker.patch("customtkinter.StringVar", side_effect=mock_stringvar)


@pytest.fixture
def base_frame(mock_controller, mock_customtkinter):
    """Create base frame instance"""
    from trivia_game.view.frames.base_frame import BaseFrame

    return BaseFrame(None, mock_controller)


@pytest.fixture
def main_menu_frame(mock_controller, mock_customtkinter):
    frame = MainMenuFrame(None, mock_controller)
    frame.tk = Mock()
    frame._w = "mock_widget"
    return frame


@pytest.fixture
def start_game_frame(mock_controller, mock_customtkinter):
    """Create start game frame instance"""
    from trivia_game.view.frames.start_game import StartGameFrame

    return StartGameFrame(None, mock_controller)
