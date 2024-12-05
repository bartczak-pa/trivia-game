"""Module for interacting with the trivia API."""

import html
import types
from typing import Any, ClassVar, cast
from urllib.parse import unquote

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
from trivia_game.models import DifficultyType, Question, QuestionType, TriviaResponseCode


class TriviaAPIClient:
    """Client for handling Trivia API interactions

    Attributes:
        QUESTIONS_API_URL (ClassVar[str]): The URL for fetching questions
        SESSION_TOKEN_API_URL (ClassVar[str]): The URL for fetching session tokens
        CATEGORIES_API_URL (str): The URL for fetching categories
        ERROR_MESSAGES (ClassVar[dict[int, str]]): Error messages for API response codes

    Args:
        timeout (int, optional): Timeout for requests. Defaults to 10.
        retries (int, optional): Number of retries for failed requests. Defaults to 3.

    Raises:
        TriviaAPIError: If an unknown error occurs
        NoResultsError: If there are not enough questions available
        InvalidParameterError: If invalid parameters are provided
        TokenError: If a session token is not found or is empty
        RateLimitError: If the rate limit is exceeded
    """

    QUESTIONS_API_URL: ClassVar[str] = "https://opentdb.com/api.php"
    SESSION_TOKEN_API_URL: ClassVar[str] = "https://opentdb.com/api_token.php"
    CATEGORIES_API_URL: ClassVar[str] = "https://opentdb.com/api_category.php"

    ERROR_MESSAGES: ClassVar[dict[int, str]] = {
        TriviaResponseCode.NO_RESULTS: "Not enough questions available for your query",
        TriviaResponseCode.INVALID_PARAMETER: "Invalid parameters provided",
        TriviaResponseCode.TOKEN_NOT_FOUND: "Session token not found",
        TriviaResponseCode.TOKEN_EMPTY: "Token has returned all possible questions",
        TriviaResponseCode.RATE_LIMIT: "Rate limit exceeded. Please wait 5 seconds",
    }

    HTTP_ERROR_MAPPING: ClassVar[dict[int, tuple[type[Exception], str]]] = {
        400: (InvalidParameterError, "Bad Request"),
        401: (TriviaAPIError, "Authentication required"),
        403: (TriviaAPIError, "Access denied"),
        404: (TriviaAPIError, "Resource not found"),
        429: (RateLimitError, "Rate limit exceeded"),
        500: (TriviaAPIError, "Internal Server Error"),
        502: (TriviaAPIError, "Bad Gateway"),
        503: (TriviaAPIError, "Service Unavailable"),
        504: (TriviaAPIError, "Gateway Timeout"),
    }

    REQUEST_ERROR_MAPPING: ClassVar[dict[type[Exception], tuple[type[Exception], str]]] = {
        requests.exceptions.ConnectionError: (TriviaAPIError, "Connection error"),
        requests.exceptions.Timeout: (TriviaAPIError, "Request timed out"),
        requests.exceptions.JSONDecodeError: (TriviaAPIError, "Invalid JSON response"),
        requests.exceptions.RequestException: (TriviaAPIError, "Generic error"),
    }

    def __init__(self, timeout: int = 10, retries: int = 3) -> None:
        """Initialize the TriviaAPIClient

        Args:
            timeout (int, optional): Timeout for requests. Defaults to 10.
            retries (int, optional): Number of retries for failed requests. Defaults to 3.

        Returns:
            None
        """

        self.timeout = timeout
        self._session_token: str | None = None
        self.session = self._create_session(retries)
        self._session_token = self.request_session_token()
        self.categories: dict[str, str] = {}

    def _create_session(self, retries: int) -> requests.Session:
        """Create and configure requests session

        Args:
            retries (int): Number of retries for failed requests

        Returns:
            requests.Session: The configured session
        """
        session: requests.Session = requests.Session()

        retry_strategy: Retry = Retry(
            total=retries,
            backoff_factor=5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _handle_response_code(self, data: dict[str, Any]) -> None:
        """Handle response code from Trivia API

        Args:
            data (dict[str, Any]): The JSON response data

        Raises:
            TriviaAPIError: If an unknown error occurs
            NoResultsError: If there are not enough questions available
            InvalidParameterError: If invalid parameters are provided
            TokenError: If a session token is not found or is empty
            RateLimitError: If the rate limit is exceeded

        Returns:
            None
        """
        response_code: int | None = data.get("response_code")

        if response_code is None:
            msg: str = "Response code not found in API response"
            raise TriviaAPIError(msg)

        if response_code == TriviaResponseCode.SUCCESS:
            return

        error_message = self.ERROR_MESSAGES.get(response_code, f"Unknown error occurred: {response_code}")

        if response_code == TriviaResponseCode.NO_RESULTS:
            raise NoResultsError(error_message)
        elif response_code == TriviaResponseCode.INVALID_PARAMETER:
            raise InvalidParameterError(error_message)
        elif response_code in (TriviaResponseCode.TOKEN_NOT_FOUND, TriviaResponseCode.TOKEN_EMPTY):
            raise TokenError(error_message)
        elif response_code == TriviaResponseCode.RATE_LIMIT:
            raise RateLimitError(error_message)
        else:
            raise TriviaAPIError(error_message)

    def _make_request(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make HTTP request with error handling"""

        try:
            response: requests.Response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            try:
                data: dict[str, Any] = response.json()
            except requests.exceptions.JSONDecodeError as e:
                error_msg: str = f"Invalid JSON response: {e!s}"
                raise TriviaAPIError(error_msg) from e

            if "response_code" in data:
                self._handle_response_code(data)

            if "token" in data and not data["token"]:
                token_err_msg: str = "Invalid token received"
                raise TokenError(token_err_msg)

        except requests.exceptions.HTTPError as e:
            status_code: int = e.response.status_code
            error_class, error_msg = self.HTTP_ERROR_MAPPING.get(status_code, (TriviaAPIError, f"HTTP {status_code}"))
            http_err_msg: str = f"Request failed: {error_msg}"
            raise error_class(http_err_msg) from e

        except tuple(self.REQUEST_ERROR_MAPPING.keys()) as e:
            error_class, error_msg = self.REQUEST_ERROR_MAPPING[type(e)]
            request_err_msg: str = f"Request failed: {error_msg}"
            raise error_class(request_err_msg) from e

        else:
            return data

    def request_session_token(self) -> str:
        """Request a session token from the API

        Raises:
            TriviaAPIError: If the request fails

        Returns:
            str: The session token value
        """
        params: dict[str, str] = {"command": "request"}
        data: dict[str, Any] = self._make_request(self.SESSION_TOKEN_API_URL, params=params)
        return cast(str, data["token"])

    def reset_session_token(self) -> str:
        """Reset the current session token.

        This will wipe all progress/question history for the current token
        but return the same token value. Use this when you've exhausted
        all questions for a given category/difficulty combination.

        Raises:
            TokenError: If no active session token exists
            TriviaAPIError: If the reset request fails

        Returns:
            str: The same token value, but with progress wiped
        """
        if not self._session_token:
            msg: str = "Cannot reset: No active session token"
            raise TokenError(msg)

        params: dict[str, str] = {"command": "reset", "token": self._session_token}
        data: dict[str, Any] = self._make_request(self.SESSION_TOKEN_API_URL, params=params)
        return cast(str, data["token"])

    def _validate_token(self, data: dict[str, Any]) -> None:
        """Validate the session token in the API response

        Args:
            data (dict[str, Any]): The API response data

        Raises:
            TokenError: If the token is invalid or empty

        Returns:
            None
        """
        if "token" in data and not data["token"]:
            msg: str = "Invalid token received"
            raise TokenError(msg)

    @staticmethod
    def _decode_text(text: str) -> str:
        """Decode URL-encoded text

        Args:
            text (str): The URL-encoded text

        Returns:
            str: The decoded text
        """
        return html.unescape(unquote(text))

    def _format_question(self, data: dict[str, Any]) -> Question:
        """Format and decode question data from API response

        Args:
            data (dict[str, Any]): The question data from the API

        Returns:
            Question: The formatted question object
        """
        difficulty: str = self._decode_text(data["difficulty"])

        if difficulty not in ("easy", "medium", "hard"):
            difficulty_err_msg: str = f"Invalid difficulty value: {difficulty}"
            raise InvalidParameterError(difficulty_err_msg)

        return Question(
            type=cast(QuestionType, self._decode_text(data["type"])),
            difficulty=cast(DifficultyType, difficulty),
            category=self._decode_text(data["category"]),
            question=self._decode_text(data["question"]),
            correct_answer=self._decode_text(data["correct_answer"]),
            incorrect_answers=[self._decode_text(answer) for answer in data["incorrect_answers"]],
        )

    def fetch_categories(self) -> dict[str, str]:
        """Fetch trivia categories from the API

        Raises:
            CategoryError: If the request fails or no categories are found

        Returns:
            dict[str, str]: The categories as a dict of name: id
        """

        try:
            data = self._make_request(self.CATEGORIES_API_URL)

            if not data.get("trivia_categories"):
                category_error_msg = "No categories found in API response"
                raise CategoryError(category_error_msg)

            self.categories = {
                category["name"]: str(category["id"])
                for category in data["trivia_categories"]
                if category.get("name") and category.get("id")
            }

        except TriviaAPIError as e:
            error_msg: str = f"Failed to fetch categories: {e!s}"
            raise CategoryError(error_msg) from e

        else:
            return self.categories

    def fetch_questions(
        self,
        amount: int = 10,
        category: str | None = None,
        difficulty: DifficultyType | None = None,
        question_type: QuestionType | None = None,
        _retry_count: int = 0,
        max_retries: int = 3,
    ) -> list[Question]:
        """Fetch trivia questions from the API.

        Args:
            amount (int, optional): The number of questions to fetch. Defaults to 10.
            category (str, optional): The category to fetch questions from. Defaults to None.
            difficulty (str, optional): The difficulty level of the questions. Defaults to None.
            question_type (str, optional): The type of questions to fetch. Defaults to None.
            _retry_count (int, optional): The current retry count for token reset. Defaults to 0.
            max_retries (int, optional): The maximum number of retries for token reset. Defaults to 3.
        Raises:
            InvalidParameterError: If invalid parameters are provided
            TokenError: If the session token is not found or is empty
            NoResultsError: If there are not enough questions available
            RateLimitError: If the rate limit is exceeded

        Returns:
            list[Question]: The list of formatted question objects
        """

        if amount < 1 or amount > 50:
            msg: str = "Amount must be between 1 and 50"
            raise InvalidParameterError(msg)

        params: dict[str, str | None] = {
            "amount": str(amount),
            "token": self._session_token,
        }

        if category:
            params["category"] = category
        if difficulty:
            params["difficulty"] = difficulty
        if question_type:
            params["type"] = question_type

        try:
            data: dict[str, Any] = self._make_request(self.QUESTIONS_API_URL, params=params)

        except TokenError as e:
            if "Token has returned all possible questions" not in str(e):
                raise

            if _retry_count >= max_retries:
                retry_count_err_msg: str = "Maximum retry attempts reached for token reset"
                raise TokenError(retry_count_err_msg) from e

            self._session_token = self.reset_session_token()

            return self.fetch_questions(
                amount=amount,
                category=category,
                difficulty=difficulty,
                question_type=question_type,
                _retry_count=_retry_count + 1,
                max_retries=max_retries,
            )

        else:
            return [self._format_question(question) for question in data["results"]]

    def __enter__(self) -> "TriviaAPIClient":
        """Enter context manager

        Returns:
            TriviaAPIClient: The client instance
        """
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None:
        """Close the session when exiting the context manager.

        Args:
            exc_type: The type of the exception that was raised
            exc_val: The instance of the exception that was raised
            exc_tb: The traceback of the exception that was raised

        Returns:
            None
        """
        self.session.close()
