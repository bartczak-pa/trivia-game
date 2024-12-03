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
