from typing import Any, ClassVar

import requests

class TriviaAPIClient:
    QUESTIONS_API_URL: ClassVar[str]
    SESSION_TOKEN_API_URL: ClassVar[str]
    CATEGORIES_API_URL: ClassVar[str]

    ERROR_MESSAGES: ClassVar[dict[int, str]]

    def __init__(self, timeout: int = 10, retries: int = 3) -> None: ...
    def _create_session(self, retries: int) -> requests.Session: ...
    def _handle_response_code(self, data: dict[str, Any]) -> None: ...
    def _make_request(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]: ...
    def request_session_token(self) -> str: ...
    def reset_session_token(self) -> str: ...
    def fetch_categories(self) -> dict[str, str]: ...
    def fetch_questions(
        self,
        amount: int = 10,
        category: str | None = None,
        difficulty: str | None = None,
        question_type: str | None = None,
    ) -> list[Any]: ...
    @staticmethod
    def _decode_text(text: str) -> str: ...
    def _format_question(self, data: dict[str, Any]) -> Any: ...
