from unittest.mock import Mock

import pytest

from trivia_game.trivia_api import TriviaAPIClient


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
