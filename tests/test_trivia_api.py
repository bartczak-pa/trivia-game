from unittest.mock import Mock, patch

import pytest
import requests
from requests.adapters import HTTPAdapter

from trivia_game.exceptions import (
    CategoryError,
    InvalidParameterError,
    NoResultsError,
    RateLimitError,
    TokenError,
    TriviaAPIError,
)
from trivia_game.models import Question, TriviaResponseCode
from trivia_game.trivia_api import TriviaAPIClient


class TestCreateSession:
    """Test cases for creating a session"""

    def test_create_session_configuration(self, trivia_client):
        """Test if session is properly configured"""
        session = trivia_client._create_session(retries=3)
        assert isinstance(session, requests.Session)
        assert isinstance(session.get_adapter("http://"), HTTPAdapter)
        retry = session.get_adapter("http://").max_retries
        assert retry.total == 3
        assert retry.backoff_factor == 5
        assert retry.status_forcelist == [429, 500, 502, 503, 504]
        assert retry.allowed_methods == ["GET"]


class TestResponseCodeHandling:
    """Test cases for handling API response codes"""

    @pytest.mark.parametrize(
        "response_code,expected_exception,expected_message",
        [
            (TriviaResponseCode.NO_RESULTS, NoResultsError, "Not enough questions available for your query"),
            (TriviaResponseCode.INVALID_PARAMETER, InvalidParameterError, "Invalid parameters provided"),
            (TriviaResponseCode.TOKEN_NOT_FOUND, TokenError, "Session token not found"),
            (TriviaResponseCode.TOKEN_EMPTY, TokenError, "Token has returned all possible questions"),
            (TriviaResponseCode.RATE_LIMIT, RateLimitError, "Rate limit exceeded. Please wait 5 seconds"),
        ],
    )
    def test_response_code_handling(self, trivia_client, response_code, expected_exception, expected_message):
        """Test handling of different API response codes"""
        mock_data = {"response_code": response_code}

        with pytest.raises(expected_exception, match=expected_message):
            trivia_client._handle_response_code(mock_data)

    def test_response_code_missing(self, trivia_client):
        """Test handling of missing response code"""
        mock_data = {}

        with pytest.raises(TriviaAPIError, match="Response code not found in API response"):
            trivia_client._handle_response_code(mock_data)

    def test_response_code_success(self, trivia_client):
        """Test handling of success response code"""
        mock_data = {"response_code": TriviaResponseCode.SUCCESS}

        # Should not raise any exception
        trivia_client._handle_response_code(mock_data)


class TestMakeRequest:
    """Test cases for making requests to the API"""

    def test_successful_request(self, trivia_client, mock_response):
        """Test successful request without response code"""
        expected_data = {"some": "data"}
        mock_response.json.return_value = expected_data

        with patch("requests.Session.get", return_value=mock_response):
            result = trivia_client._make_request("http://test.url")
            assert result == expected_data

    def test_request_with_params(self, trivia_client, mock_response):
        """Test request with query parameters"""
        mock_response.json.return_value = {"data": "test"}
        test_params = {"param1": "value1", "param2": "value2"}

        with patch("requests.Session.get", return_value=mock_response) as mock_get:
            trivia_client._make_request("http://test.url", params=test_params)

            mock_get.assert_called_once_with("http://test.url", params=test_params, timeout=trivia_client.timeout)

    def test_invalid_json_response(self, trivia_client):
        """Test handling of invalid JSON response"""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value = mock_response

            with pytest.raises(
                TriviaAPIError, match=r"Invalid JSON response: Invalid JSON: line 1 column 1 \(char 0\)"
            ):
                trivia_client._make_request("http://test.url")

    @pytest.mark.parametrize(
        "exception_class,expected_error",
        [
            (requests.exceptions.ConnectionError, "Request failed: Connection error"),
            (requests.exceptions.Timeout, "Request failed: Request timed out"),
            (requests.exceptions.RequestException, "Request failed: Generic error"),
        ],
    )
    def test_request_exceptions(self, trivia_client, exception_class, expected_error):
        """Test handling of request exceptions"""
        with patch("requests.Session.get") as mock_get:
            mock_get.side_effect = exception_class("Generic error")

            with pytest.raises(TriviaAPIError, match=expected_error):
                trivia_client._make_request("http://test.url")

    @pytest.mark.parametrize(
        "status_code,expected_error",
        [
            (400, "Request failed: Bad Request"),
            (401, "Request failed: Authentication required"),
            (403, "Request failed: Access denied"),
            (404, "Request failed: Resource not found"),
            (429, "Request failed: Rate limit exceeded"),
            (500, "Request failed: Internal Server Error"),
            (502, "Request failed: Bad Gateway"),
            (503, "Request failed: Service Unavailable"),
            (504, "Request failed: Gateway Timeout"),
            (418, "Request failed: HTTP 418"),
        ],
    )
    def test_http_error_codes(self, trivia_client, status_code, expected_error):
        """Test handling of HTTP error status codes"""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)

            with pytest.raises(TriviaAPIError, match=expected_error):
                trivia_client._make_request("http://test.url")


class TestParseAndValidateResponse:
    """Test cases for parsing and validating API responses"""

    def test_successful_response(self, trivia_client):
        """Test successful response parsing"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response_code": TriviaResponseCode.SUCCESS,
            "token": "valid_token",
            "data": "test",
        }

        result = trivia_client._parse_and_validate_response(mock_response)
        assert result["data"] == "test"
        assert result["token"] == "valid_token"

    def test_invalid_json(self, trivia_client):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "", 0)

        with pytest.raises(TriviaAPIError, match=r"Invalid JSON response: Invalid JSON: line 1 column 1 \(char 0\)"):
            trivia_client._parse_and_validate_response(mock_response)

    def test_invalid_token(self, trivia_client):
        """Test handling of invalid token in response"""
        mock_response = Mock()
        mock_response.json.return_value = {"response_code": TriviaResponseCode.SUCCESS, "token": ""}

        with pytest.raises(TokenError, match="Invalid token received"):
            trivia_client._parse_and_validate_response(mock_response)

    @pytest.mark.parametrize(
        "response_code,expected_exception,expected_message",
        [
            (TriviaResponseCode.NO_RESULTS, NoResultsError, "Not enough questions available for your query"),
            (TriviaResponseCode.INVALID_PARAMETER, InvalidParameterError, "Invalid parameters provided"),
            (TriviaResponseCode.TOKEN_NOT_FOUND, TokenError, "Session token not found"),
            (TriviaResponseCode.TOKEN_EMPTY, TokenError, "Token has returned all possible questions"),
            (TriviaResponseCode.RATE_LIMIT, RateLimitError, "Rate limit exceeded. Please wait 5 seconds"),
        ],
    )
    def test_api_error_responses(self, trivia_client, response_code, expected_exception, expected_message):
        """Test handling of API error responses"""
        mock_response = Mock()
        mock_response.json.return_value = {"response_code": response_code}

        with pytest.raises(expected_exception, match=expected_message):
            trivia_client._parse_and_validate_response(mock_response)


class TestTokenManagement:
    """Test cases for managing session tokens"""

    @pytest.mark.parametrize(
        "response_data,expected_token",
        [
            ({"response_code": 0, "token": "abc123"}, "abc123"),
            ({"response_code": 0, "token": "xyz789"}, "xyz789"),
        ],
    )
    def test_request_session_token_success(self, trivia_client, mock_response, response_data, expected_token):
        """Test successful token request"""
        mock_response.json.return_value = response_data

        with patch("requests.Session.get", return_value=mock_response):
            token = trivia_client.request_session_token()
            assert token == expected_token

    def test_request_session_token_invalid_response(self, trivia_client, mock_response):
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
    def test_request_session_token_request_errors(self, trivia_client, exception_class, expected_error):
        """Test token request with various request errors"""
        with patch("requests.Session.get") as mock_get:
            mock_get.side_effect = exception_class("Generic error")

            with pytest.raises(TriviaAPIError, match=expected_error):
                trivia_client.request_session_token()

    def test_reset_session_token_returns_same_token(self, trivia_client, mock_response):
        """Test that token reset returns the same token but wipes progress"""
        existing_token = "existing_token_123"
        trivia_client._session_token = existing_token

        mock_response.json.return_value = {
            "response_code": 0,
            "token": existing_token,
        }

        with patch("requests.Session.get", return_value=mock_response) as mock_get:
            token = trivia_client.reset_session_token()

            assert token == existing_token
            mock_get.assert_called_once_with(
                trivia_client.SESSION_TOKEN_API_URL,
                params={"command": "reset", "token": existing_token},
                timeout=trivia_client.timeout,
            )

    def test_reset_token_without_session(self, trivia_client):
        """Test reset attempt without active session token"""
        trivia_client._session_token = None

        with pytest.raises(TokenError, match="Cannot reset: No active session token"):
            trivia_client.reset_session_token()

    def test_reset_token_network_error(self, trivia_client):
        """Test token reset with network error"""
        trivia_client._session_token = "existing_token"

        with patch("requests.Session.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(TriviaAPIError, match="Request failed: Connection error"):
                trivia_client.reset_session_token()

    def test_reset_token_invalid_response(self, trivia_client, mock_response):
        """Test token reset with invalid API response"""
        trivia_client._session_token = "existing_token"
        mock_response.json.return_value = {"response_code": 3}

        with patch("requests.Session.get", return_value=mock_response):
            with pytest.raises(TokenError, match="Session token not found"):
                trivia_client.reset_session_token()

    def test_reset_token_empty_token_response(self, trivia_client, mock_response):
        """Test token reset with missing token in response"""
        trivia_client._session_token = "existing_token"
        mock_response.json.return_value = {"response_code": 0, "token": ""}

        with patch("requests.Session.get", return_value=mock_response):
            with pytest.raises(TokenError, match="Invalid token received"):
                trivia_client.reset_session_token()


class TestCategories:
    def test_fetch_categories_success(self, trivia_client, mock_categories_response, mock_response):
        """Test successful categories fetch"""
        mock_response.json.return_value = {
            "trivia_categories": [
                {"id": "9", "name": "General Knowledge"},
                {"id": "10", "name": "Books"},
                {"id": "11", "name": "Film"},
            ]
        }

        with patch("requests.Session.get", return_value=mock_response):
            categories = trivia_client.fetch_categories()
            assert len(categories) == 3
            assert categories["General Knowledge"] == "9"
            assert categories["Books"] == "10"
            assert categories["Film"] == "11"

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

    def _extracted_from_test_fetch_categories_invalid_data_4(self, trivia_client, arg1, arg2, arg3):
        result = trivia_client.fetch_categories()
        assert len(result) == arg1
        assert result[arg2] == arg3
        return result

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


class TestDecodeText:
    @pytest.mark.parametrize(
        "encoded,expected",
        [
            ("Hello%20World", "Hello World"),
            ("&quot;Hello&quot;", '"Hello"'),
            ("Test%20&amp;%20More", "Test & More"),
            ("&lt;tag&gt;", "<tag>"),
            ("Don&apos;t stop", "Don't stop"),
            ("&quot;Let them eat cake&quot;", '"Let them eat cake"'),
        ],
    )
    def test_decode_text(self, trivia_client, encoded, expected):
        """Test decoding of both URL encoding and HTML entities"""
        decoded = trivia_client._decode_text(encoded)
        assert decoded == expected

    def test_decode_text_already_decoded(self, trivia_client):
        """Test decoding already decoded text"""
        text = "Already decoded text"
        decoded = trivia_client._decode_text(text)
        assert decoded == text


class TestFormatQuestion:
    def test_format_question_success(self, trivia_client):
        """Test successful question formatting with HTML entities and URL encoding"""
        raw_data = {
            "type": "multiple",
            "difficulty": "medium",
            "category": "Entertainment%3A%20Video%20Games",
            "question": "What&apos;s the main character&apos;s name%3F",
            "correct_answer": "Mario%20&amp;%20Luigi",
            "incorrect_answers": ["Bowser%20&amp;%20Koopa", "Peach%20&amp;%20Daisy", "Wario%20&amp;%20Waluigi"],
        }

        question = trivia_client._format_question(raw_data)

        assert question.type == "multiple"
        assert question.difficulty == "medium"
        assert question.category == "Entertainment: Video Games"
        assert question.question == "What's the main character's name?"
        assert question.correct_answer == "Mario & Luigi"
        assert len(question.incorrect_answers) == 3
        assert question.incorrect_answers[0] == "Bowser & Koopa"

    def test_format_question_boolean_type(self, trivia_client):
        """Test formatting boolean type questions"""
        raw_data = {
            "type": "boolean",
            "difficulty": "easy",
            "category": "Science",
            "question": "Is the Earth flat%3F",
            "correct_answer": "False",
            "incorrect_answers": ["True"],
        }

        question = trivia_client._format_question(raw_data)

        assert question.type == "boolean"
        assert question.correct_answer == "False"
        assert question.incorrect_answers == ["True"]

    def test_format_question_special_characters(self, trivia_client):
        """Test handling of various special characters and HTML entities"""
        raw_data = {
            "type": "multiple",
            "difficulty": "hard",
            "category": "General%20Knowledge",
            "question": "&quot;Hello%20World&quot;%20&#39;Test&#39;%20&lt;tag&gt;",
            "correct_answer": "Answer%20with%20&amp;%20symbol",
            "incorrect_answers": ["Test%201", "Test%202"],
        }

        question = trivia_client._format_question(raw_data)

        assert question.question == "\"Hello World\" 'Test' <tag>"
        assert question.correct_answer == "Answer with & symbol"


class TestFetchQuestions:
    @pytest.mark.parametrize(
        "params,expected",
        [
            (
                {},
                {
                    "type": "multiple",
                    "difficulty": "medium",
                    "category": "Entertainment: Video Games",
                    "question": "Test?",
                    "correct_answer": "Yes",
                    "incorrect_answers": ["No", "Maybe", "Never"],
                },
            ),
            (
                {"amount": 1, "difficulty": "hard"},
                {
                    "type": "multiple",
                    "difficulty": "hard",
                    "category": "Entertainment: Video Games",
                    "question": "Hard test?",
                    "correct_answer": "Correct",
                    "incorrect_answers": ["Wrong1", "Wrong2", "Wrong3"],
                },
            ),
        ],
    )
    def test_fetch_questions_success(self, trivia_client, mock_response, params, expected):
        """Test successful questions fetch with different parameters"""
        mock_response.json.return_value = {"response_code": TriviaResponseCode.SUCCESS, "results": [expected]}

        with patch("requests.Session.get", return_value=mock_response):
            questions = trivia_client.fetch_questions(**params)
            assert len(questions) == 1
            assert isinstance(questions[0], Question)
            assert questions[0].type == expected["type"]
            assert questions[0].difficulty == expected["difficulty"]

    def test_fetch_questions_token_empty_auto_reset_success(self, trivia_client, mock_response):
        """Test successful token reset within retry limit"""
        initial_token = "initial_token_123"
        trivia_client._session_token = initial_token

        # First call returns token empty
        mock_response.json.return_value = {"response_code": TriviaResponseCode.TOKEN_EMPTY}

        # Second call (token reset) returns new token
        reset_response = Mock()
        reset_response.json.return_value = {"response_code": TriviaResponseCode.SUCCESS, "token": "new_token_123"}

        # Third call returns success
        success_response = Mock()
        success_response.json.return_value = {
            "response_code": TriviaResponseCode.SUCCESS,
            "results": [
                {
                    "type": "multiple",
                    "difficulty": "medium",
                    "category": "Test",
                    "question": "Test?",
                    "correct_answer": "Yes",
                    "incorrect_answers": ["No"],
                }
            ],
        }

        with patch("requests.Session.get") as mock_get:
            mock_get.side_effect = [mock_response, reset_response, success_response]

            questions = trivia_client.fetch_questions()

            assert len(mock_get.call_args_list) == 3
            assert questions[0].question == "Test?"
            assert trivia_client._session_token == "new_token_123"

    def test_fetch_questions_max_retries_exceeded(self, trivia_client, mock_response):
        """Test token reset exceeding max retries"""
        trivia_client._session_token = "initial_token"

        # Questions request response
        empty_token_response = Mock()
        empty_token_response.json.return_value = {"response_code": TriviaResponseCode.TOKEN_EMPTY}

        # Token reset response
        reset_token_response = Mock()
        reset_token_response.json.return_value = {"response_code": TriviaResponseCode.SUCCESS, "token": "new_token"}

        with patch("requests.Session.get") as mock_get:
            # Simulate sequence:
            # 1. Questions request (TOKEN_EMPTY)
            # 2. Token reset (SUCCESS)
            # 3. Questions request (TOKEN_EMPTY)
            # ... repeat until max retries
            mock_get.side_effect = [
                empty_token_response,  # First questions request
                reset_token_response,  # First reset
                empty_token_response,  # Second questions request
                reset_token_response,  # Second reset
                empty_token_response,  # Third questions request
                reset_token_response,  # Third reset
                empty_token_response,  # Fourth questions request (exceeds max retries)
            ]

            with pytest.raises(TokenError, match="Maximum retry attempts reached for token reset"):
                trivia_client.fetch_questions(max_retries=3)

    @pytest.mark.parametrize(
        "amount,expected_error",
        [
            (0, "Amount must be between 1 and 50"),
            (51, "Amount must be between 1 and 50"),
            (-1, "Amount must be between 1 and 50"),
        ],
    )
    def test_fetch_questions_invalid_amount(self, trivia_client, amount, expected_error):
        """Test handling of invalid amount parameter"""
        with pytest.raises(InvalidParameterError, match=expected_error):
            trivia_client.fetch_questions(amount=amount)


class TestValidateToken:
    def test_validate_token_success(self, trivia_client):
        """Test successful token validation"""
        data = {"token": "valid_token_123"}
        trivia_client._validate_token(data)  # Should not raise any exception

    def test_validate_token_empty(self, trivia_client):
        """Test validation with empty token"""
        data = {"token": ""}

        with pytest.raises(TokenError, match="Invalid token received"):
            trivia_client._validate_token(data)

    def test_validate_token_missing(self, trivia_client):
        """Test validation with missing token field"""
        data = {"some_field": "value"}
        trivia_client._validate_token(data)  # Should not raise any exception

    def test_validate_token_none(self, trivia_client):
        """Test validation with None token value"""
        data = {"token": None}

        with pytest.raises(TokenError, match="Invalid token received"):
            trivia_client._validate_token(data)
