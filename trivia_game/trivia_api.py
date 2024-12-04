"""Module for interacting with the trivia API."""

from dataclasses import dataclass
from typing import Any, ClassVar, TypedDict, cast
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
from trivia_game.models import TriviaResponseCode


class TriviaResponse(TypedDict):
    response_code: int
    results: list[dict[str, Any]]


@dataclass(frozen=True)
class ResponseType:
    success: bool
    data: dict[str, Any]
    error: str | None = None


class TriviaAPIClient:
    """Client for handling Trivia API interactions"""

    QUESTIONS_API_URL: ClassVar[str] = "https://opentdb.com/api.php"
    SESSION_TOKEN_API_URL: ClassVar[str] = "https://opentdb.com/api_token.php"
    CATEGORIES_API_URL: str = "https://opentdb.com/api_category.php"

    ERROR_MESSAGES: ClassVar[dict[int, str]] = {
        TriviaResponseCode.NO_RESULTS: "Not enough questions available for your query",
        TriviaResponseCode.INVALID_PARAMETER: "Invalid parameters provided",
        TriviaResponseCode.TOKEN_NOT_FOUND: "Session token not found",
        TriviaResponseCode.TOKEN_EMPTY: "Token has returned all possible questions",
        TriviaResponseCode.RATE_LIMIT: "Rate limit exceeded. Please wait 5 seconds",
    }

    def __init__(self, timeout: int = 10, retires: int = 3) -> None:
        """Initialize the TriviaAPIClient

        Args:
            timeout (int, optional): Timeout for requests. Defaults to 10.
            retires (int, optional): Number of retries for failed requests. Defaults to 3.

        Returns:
            None
        """

        self.timeout = timeout
        self._session_token: str | None = None
        self.session = self._create_session(retires)
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
        """Make HTTP request with error handling

        Args:
            url (str): The URL to make the request to
            params (dict[str, Any], optional): Query parameters for the request. Defaults to None.

        Raises:
            TriviaAPIError: If the request fails

        Returns:
            dict[str, Any]: The JSON response data
        """

        try:
            response: requests.Response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data: dict[str, Any] = response.json()

            # Only check response code for endpoints that return it
            if "response_code" in data:
                self._handle_response_code(data)

        except requests.exceptions.HTTPError as e:
            status_code: int = e.response.status_code
            error_msg: str = {
                400: "Bad Request",
                401: "Authentication required",
                403: "Access denied",
                404: "Resource not found",
                429: "Rate limit exceeded",
                500: "Internal Server Error",
                502: "Bad Gateway",
                503: "Service Unavailable",
                504: "Gateway Timeout",
            }.get(status_code, f"HTTP {status_code}")

            msg = f"Request failed: {error_msg}"
            raise TriviaAPIError(msg) from e

        except requests.exceptions.ConnectionError as e:
            connection_error_msg: str = "Request failed: Connection error"
            raise TriviaAPIError(connection_error_msg) from e

        except requests.exceptions.Timeout as e:
            timeout_error_msg: str = "Request failed: Request timed out"
            raise TriviaAPIError(timeout_error_msg) from e

        except requests.exceptions.RequestException as e:
            exception_error_msg: str = f"Request failed: {e!s}"
            raise TriviaAPIError(exception_error_msg) from e

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

    @staticmethod
    def _decode_text(text: str) -> str:
        """Decode URL-encoded text

        Args:
            text (str): The URL-encoded text

        Returns:
            str: The decoded text
        """
        return unquote(text)

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
