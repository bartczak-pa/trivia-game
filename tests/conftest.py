import pytest

from trivia_game.trivia_api import TriviaAPIClient


@pytest.fixture
def client():
    """Return a TriviaAPIClient instance."""
    return TriviaAPIClient("http://example.com/api")
