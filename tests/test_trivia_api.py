import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from trivia_game.trivia_api import ResponseType, TriviaAPIClient


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


def test_error_messages():
    # Act & Assert
    assert TriviaAPIClient.ERROR_MESSAGES[1] == "No Results: The API doesn't have enough questions for your query."
    assert TriviaAPIClient.ERROR_MESSAGES[2] == "Invalid Parameter: Arguments passed in aren't valid."
    assert TriviaAPIClient.ERROR_MESSAGES[3] == "Token Not Found: Session Token does not exist."
    assert TriviaAPIClient.ERROR_MESSAGES[4] == "Token Empty: Session Token is empty."
    assert TriviaAPIClient.ERROR_MESSAGES[5] == "Rate Limit Exceeded: Too many requests."


def test_response_type_success():
    # Arrange
    data = {"key": "value"}

    # Act
    response = ResponseType(success=True, data=data)

    # Assert
    assert response.success
    assert response.data == data
    assert response.error is None


def test_response_type_error():
    # Arrange
    data = {}
    error_message = "An error occurred"

    # Act
    response = ResponseType(success=False, data=data, error=error_message)

    # Assert
    assert not response.success
    assert response.data == data
    assert response.error == error_message
