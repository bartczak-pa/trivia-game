import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from trivia_game.exceptions import InvalidParameterError, NoResultsError, RateLimitError
from trivia_game.models import TriviaResponseCode


def test_create_session_configuration(trivia_client):
    """Test if session is properly configured"""
    session = trivia_client._create_session(retries=3)

    # Verify session is created
    assert isinstance(session, requests.Session)

    # Verify adapter configuration
    adapter = session.get_adapter("http://")
    assert isinstance(adapter, HTTPAdapter)

    # Verify retry configuration
    retry = adapter.max_retries
    assert isinstance(retry, Retry)
    assert retry.total == 3
    assert retry.backoff_factor == 5
    assert retry.status_forcelist == [429, 500, 502, 503, 504]
    assert retry.allowed_methods == ["GET"]


@pytest.mark.parametrize(
    "response_code,expected_exception,expected_message",
    [
        (TriviaResponseCode.NO_RESULTS, NoResultsError, "Not enough questions available for your query"),
        (TriviaResponseCode.INVALID_PARAMETER, InvalidParameterError, "Invalid parameters provided"),
        (TriviaResponseCode.RATE_LIMIT, RateLimitError, "Rate limit exceeded. Please wait 5 seconds"),
    ],
)
def test_response_code_handling(trivia_client, response_code, expected_exception, expected_message):
    """Test handling of different API response codes"""
    mock_data = {"response_code": response_code}

    with pytest.raises(expected_exception, match=expected_message):
        trivia_client._handle_response_code(mock_data)
