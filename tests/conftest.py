from unittest.mock import MagicMock, Mock

import pytest

from trivia_game.trivia_api import TriviaAPIClient
from trivia_game.view.frames import MainMenuFrame
from trivia_game.view.frames.base_frame import BaseFrame
from trivia_game.view.frames.quiz_frames import BaseQuizFrame, MultipleChoiceQuizFrame, TrueFalseQuizFrame

# Ignore folder in progress
collect_ignore = ["in_progress/"]


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
def mock_controller(mocker):
    """Create a mock controller with quiz_brain"""
    controller = mocker.Mock()
    controller.quiz_brain = mocker.Mock()
    controller.quiz_brain.current_question = None
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


@pytest.fixture
def mock_question(mocker):
    """Create a mock Question object"""
    question = mocker.Mock()
    question.question = "Test Question"
    question.type = "multiple"
    question.correct_answer = "A"
    question.incorrect_answers = ["B", "C", "D"]
    return question


@pytest.fixture
def base_quiz_frame(mock_controller, mock_ctk):
    """Create a BaseQuizFrame instance with mocked widgets"""
    frame = BaseQuizFrame(None, mock_controller)
    frame.question_frame = mock_ctk.CTkFrame()
    frame.question_label = mock_ctk.CTkLabel()
    frame.score_label = mock_ctk.CTkLabel()
    return frame


@pytest.fixture
def true_false_frame(mock_controller):
    """Create a TrueFalseQuizFrame instance"""
    return TrueFalseQuizFrame(None, mock_controller)


@pytest.fixture
def multiple_choice_frame(mock_controller):
    """Create a MultipleChoiceQuizFrame instance"""
    return MultipleChoiceQuizFrame(None, mock_controller)


@pytest.fixture
def quiz_brain(mock_controller):
    """Create a QuizBrain instance with mock controller"""
    from trivia_game.quiz_brain import QuizBrain

    brain = QuizBrain(mock_controller)
    brain.score = 0
    brain.current_question = None
    brain.questions = []

    return brain


@pytest.fixture(autouse=True)
def mock_ctk(monkeypatch):
    """Mock CustomTkinter widgets and root for testing"""
    mock_tk = MagicMock()

    # Create mock classes
    mock_tk.CTkFrame = MagicMock()
    mock_tk.CTkLabel = MagicMock()
    mock_tk.CTkButton = MagicMock()

    # Add required methods to Frame
    mock_tk.CTkFrame.return_value.winfo_children = MagicMock(return_value=[])
    mock_tk.CTkFrame.return_value.grid = MagicMock()
    mock_tk.CTkFrame.return_value.configure = MagicMock()

    # Add required methods to Label
    mock_tk.CTkLabel.return_value.grid = MagicMock()
    mock_tk.CTkLabel.return_value.configure = MagicMock()

    # Add required methods to Button
    mock_tk.CTkButton.return_value.grid = MagicMock()
    mock_tk.CTkButton.return_value.configure = MagicMock()

    # Patch the entire customtkinter module
    monkeypatch.setattr("customtkinter.CTkFrame", mock_tk.CTkFrame)
    monkeypatch.setattr("customtkinter.CTkLabel", mock_tk.CTkLabel)
    monkeypatch.setattr("customtkinter.CTkButton", mock_tk.CTkButton)

    return mock_tk
