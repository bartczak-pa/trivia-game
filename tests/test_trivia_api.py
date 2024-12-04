from unittest.mock import Mock, patch

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from trivia_game.exceptions import InvalidParameterError, NoResultsError, RateLimitError, TokenError, TriviaAPIError
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


@pytest.mark.parametrize(
    "exception_class,expected_error",
    [
        (requests.exceptions.Timeout, "Request failed: Request timed out"),
        (requests.exceptions.ConnectionError, "Request failed: Connection error"),
        (requests.exceptions.RequestException, "Request failed: Generic error"),
    ],
)
def test_make_request_http_exceptions(trivia_client, exception_class, expected_error):
    """Test handling of different HTTP exceptions"""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = exception_class("Generic error")

        with pytest.raises(TriviaAPIError, match=expected_error):
            trivia_client._make_request("http://test.com")


def test_make_request_success(trivia_client):
    """Test successful API request"""
    mock_response = Mock()
    mock_response.json.return_value = {"response_code": TriviaResponseCode.SUCCESS, "results": ["test_data"]}
    mock_response.raise_for_status.return_value = None

    with patch("requests.Session.get", return_value=mock_response) as mock_get:
        result = trivia_client._make_request("http://test.com", {"param": "value"})

        # Verify the request was made correctly
        mock_get.assert_called_once_with("http://test.com", params={"param": "value"}, timeout=trivia_client.timeout)

        # Verify response processing
        assert result == {"response_code": 0, "results": ["test_data"]}


def test_make_request_invalid_json(trivia_client):
    """Test handling of invalid JSON response"""
    mock_response = Mock()
    mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "", 0)
    mock_response.raise_for_status.return_value = None

    with patch("requests.Session.get", return_value=mock_response):
        with pytest.raises(TriviaAPIError, match="Request failed: Invalid JSON"):
            trivia_client._make_request("http://test.com")


def test_make_request_with_error_response_code(trivia_client):
    """Test handling of error response codes"""
    mock_response = Mock()
    mock_response.json.return_value = {"response_code": TriviaResponseCode.NO_RESULTS}
    mock_response.raise_for_status.return_value = None

    with patch("requests.Session.get", return_value=mock_response):
        with pytest.raises(NoResultsError):
            trivia_client._make_request("http://test.com")


@pytest.mark.parametrize(
    "status_code,expected_error",
    [
        (400, "Request failed: Bad Request"),
        (401, "Request failed: Authentication required"),
        (403, "Request failed: Access denied"),
        (404, "Request failed: Resource not found"),
        (500, "Request failed: Internal Server Error"),
    ],
)
def test_make_request_http_error_codes(trivia_client, status_code, expected_error):
    """Test handling of different HTTP error status codes"""
    with patch("requests.Session.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)

        with pytest.raises(TriviaAPIError, match=expected_error):
            trivia_client._make_request("http://test.com")


def test_make_request_timeout_configuration(trivia_client):
    """Test timeout configuration in request"""
    mock_response = Mock()
    mock_response.json.return_value = {"response_code": TriviaResponseCode.SUCCESS}
    mock_response.raise_for_status.return_value = None

    custom_timeout = 5
    trivia_client.timeout = custom_timeout

    with patch("requests.Session.get", return_value=mock_response) as mock_get:
        trivia_client._make_request("http://test.com")
        mock_get.assert_called_once_with("http://test.com", params=None, timeout=custom_timeout)


@pytest.mark.parametrize(
    "response_data,expected_token",
    [
        ({"response_code": 0, "token": "abc123"}, "abc123"),
        ({"response_code": 0, "token": "xyz789"}, "xyz789"),
    ],
)
def test_request_session_token_success(trivia_client, mock_response, response_data, expected_token):
    """Test successful token request"""
    mock_response.json.return_value = response_data

    with patch("requests.Session.get", return_value=mock_response):
        token = trivia_client.request_session_token()
        assert token == expected_token


def test_request_session_token_invalid_response(trivia_client, mock_response):
    """Test token request with invalid response"""
    mock_response.json.return_value = {"response_code": 3}

    with patch("requests.Session.get", return_value=mock_response):
        with pytest.raises(TokenError, match="Session token not found"):
            trivia_client.request_session_token()


@pytest.mark.parametrize(
    "exception_class,expected_error",
    [
        (requests.exceptions.ConnectionError, "Request failed: Connection error"),
        (requests.exceptions.Timeout, "Request failed: Request timed out"),
        (requests.exceptions.RequestException, "Request failed: Generic error"),
    ],
)
def test_request_session_token_request_errors(trivia_client, exception_class, expected_error):
    """Test token request with various request errors"""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = exception_class("Generic error")

        with pytest.raises(TriviaAPIError, match=expected_error):
            trivia_client.request_session_token()


def test_reset_session_token_returns_same_token(trivia_client, mock_response):
    """Test that token reset returns the same token but wipes progress"""
    existing_token = "existing_token_123"
    trivia_client._session_token = existing_token

    mock_response.json.return_value = {
        "response_code": 0,
        "token": existing_token,  # Same token returned
    }

    with patch("requests.Session.get", return_value=mock_response) as mock_get:
        token = trivia_client.reset_session_token()

        # Verify same token is returned
        assert token == existing_token

        # Verify correct reset command was sent
        mock_get.assert_called_once_with(
            trivia_client.SESSION_TOKEN_API_URL,
            params={"command": "reset", "token": existing_token},
            timeout=trivia_client.timeout,
        )
