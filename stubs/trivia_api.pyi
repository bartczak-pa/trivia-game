from dataclasses import dataclass
from typing import Any, ClassVar, TypedDict

import requests

class TriviaResponse(TypedDict):
    response_code: int
    results: list[dict[str, Any]]

@dataclass(frozen=True)
class ResponseType:
    success: bool
    data: dict[str, Any]
    error: str | None = None

class TriviaAPIClient:
    ERROR_MESSAGES: ClassVar[dict[int, str]]

    def __init__(self, base_url: str, timeout: int = 10) -> None: ...
    def _create_session(self) -> requests.Session: ...
