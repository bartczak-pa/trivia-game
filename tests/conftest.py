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
