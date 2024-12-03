from typing import Any

import requests

class TriviaAPIClient:
    QUESTIONS_API_URL: str
    SESSION_TOKEN_API_URL: str
    ERROR_MESSAGES: dict[int, str]

    def __init__(self, timeout: int = 10, retries: int = 3) -> None: ...
    def _create_session(self, retries: int) -> requests.Session: ...
    def _handle_response_code(self, data: dict[str, Any]) -> None: ...
    def _make_request(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]: ...
