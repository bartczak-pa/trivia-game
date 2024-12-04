from unittest.mock import Mock, patch

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from trivia_game.exceptions import (
    CategoryError,
    InvalidParameterError,
    NoResultsError,
    RateLimitError,
    TokenError,
    TriviaAPIError,
)
from trivia_game.models import TriviaResponseCode
from trivia_game.trivia_api import TriviaAPIClient


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


class TestCategories:
    def test_fetch_categories_success(self, trivia_client, mock_categories_response):
        """Test successful categories fetch"""
        with patch("requests.Session.get", return_value=mock_categories_response):
            categories = trivia_client.fetch_categories()

            assert len(categories) == 3
            assert categories["General Knowledge"] == "9"
            assert categories["Entertainment: Books"] == "10"
            assert categories["Entertainment: Film"] == "11"

    def test_fetch_categories_empty_response(self, trivia_client, mock_response):
        """Test handling of empty categories response"""
        mock_response.json.return_value = {"trivia_categories": []}

        with patch("requests.Session.get", return_value=mock_response):
            with pytest.raises(CategoryError, match="No categories found in API response"):
                trivia_client.fetch_categories()

    def test_fetch_categories_invalid_data(self, trivia_client, mock_response):
        """Test handling of invalid category data"""
        mock_response.json.return_value = {
            "trivia_categories": [
                {"id": 9},  # Missing name
                {"name": "Invalid"},  # Missing id
                {"id": 11, "name": "Valid Category"},
            ]
        }

        with patch("requests.Session.get", return_value=mock_response):
            categories = trivia_client.fetch_categories()

            assert len(categories) == 1
            assert categories["Valid Category"] == "11"

    def test_fetch_categories_network_error(self, trivia_client):
        """Test handling of network errors"""
        with patch("requests.Session.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(CategoryError, match="Failed to fetch categories: Request failed: Connection error"):
                trivia_client.fetch_categories()

    @pytest.mark.integration
    def test_real_categories_fetch(self):
        """Test fetching categories from actual API"""
        client = TriviaAPIClient()
        try:
            categories = client.fetch_categories()

            assert len(categories) > 0
            assert all(isinstance(name, str) and isinstance(id_, str) for name, id_ in categories.items())
        finally:
            client.session.close()


@pytest.mark.parametrize(
    "encoded,expected",
    [
        ("Hello%20World", "Hello World"),
        ("Entertainment%3A%20Video%20Games", "Entertainment: Video Games"),
        ("General%20Knowledge", "General Knowledge"),
        ("Science%3A%20Computers", "Science: Computers"),
        ("Entertainment%3A%20Books", "Entertainment: Books"),
        ("%2B919999999999", "+919999999999"),
        ("No%20encoding%20needed", "No encoding needed"),
        ("", ""),  # Empty string case
    ],
)
def test_decode_text(trivia_client, encoded, expected):
    """Test URL decoding of different text patterns"""
    decoded = trivia_client._decode_text(encoded)
    assert decoded == expected


def test_decode_text_already_decoded(trivia_client):
    """Test decoding already decoded text"""
    text = "Already decoded text"
    decoded = trivia_client._decode_text(text)
    assert decoded == text
