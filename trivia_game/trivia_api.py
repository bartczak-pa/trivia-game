"""Module for interacting with the trivia API."""

from dataclasses import dataclass
from typing import Any, ClassVar, TypedDict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import InvalidParameterError, NoResultsError, RateLimitError, TokenError, TriviaAPIError
from .models import TriviaResponseCode


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
        self.session = self._create_session(retires)

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
