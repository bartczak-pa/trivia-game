"""Module for interacting with the trivia API."""

from dataclasses import dataclass
from typing import Any, ClassVar, TypedDict, cast

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from trivia_game.exceptions import InvalidParameterError, NoResultsError, RateLimitError, TokenError, TriviaAPIError
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

    ERROR_MESSAGES: ClassVar[dict[int, str]] = {
        TriviaResponseCode.NO_RESULTS: "Not enough questions available for your query",
        TriviaResponseCode.INVALID_PARAMETER: "Invalid parameters provided",
        TriviaResponseCode.TOKEN_NOT_FOUND: "Session token not found",
        TriviaResponseCode.TOKEN_EMPTY: "Token has returned all possible questions",
        TriviaResponseCode.RATE_LIMIT: "Rate limit exceeded. Please wait 5 seconds",
    }

    def __init__(self, timeout: int = 10, retires: int = 3) -> None:
        self.timeout = timeout
        self._session_token: str | None = None
        self.session = self._create_session(retires)
        self._session_token = self.request_session_token()

    def _create_session(self, retries: int) -> requests.Session:
        """Create and configure requests session"""
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
        """Handle response code from Trivia API"""
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
            data: dict[str, Any] = response.json()

            # Validate response code
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
        """Request a session token from the API"""
        params: dict[str, str] = {"command": "request"}
        data: dict[str, Any] = self._make_request(self.SESSION_TOKEN_API_URL, params=params)
        return cast(str, data["token"])
