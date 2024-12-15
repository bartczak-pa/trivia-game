from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_controller():
    """Create a mock controller with quiz_brain"""
    controller = Mock()
    controller.quiz_brain = Mock()
    controller.quiz_brain.current_question = None
    return controller


@pytest.fixture
def quiz_brain(mock_controller):
    """Create a QuizBrain instance with mock controller"""
    from trivia_game.quiz_brain import QuizBrain

    brain = QuizBrain(mock_controller)
    brain.score = 0
    brain.current_question = None
    brain.questions = []
    return brain


@pytest.fixture
def mock_question(mocker):
    """Create a mock Question object"""
    question = mocker.Mock()
    question.question = "Test Question"
    question.type = "multiple"
    question.difficulty = "medium"
    question.correct_answer = "A"
    question.incorrect_answers = ["B", "C", "D"]
    return question
