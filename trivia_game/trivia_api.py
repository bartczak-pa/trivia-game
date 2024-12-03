"""Module for interacting with the trivia API."""

from dataclasses import dataclass
from typing import Any, ClassVar, TypedDict


class TriviaResponse(TypedDict):
    response_code: int
    results: list[dict[str, Any]]


@dataclass(frozen=True)
class ResponseType:
    success: bool
    data: dict[str, Any]
    error: str | None = None


class TriviaAPIClient:
    """Client for interacting with the trivia API."""

    ERROR_MESSAGES: ClassVar[dict[int, str]] = {
        1: "No Results: The API doesn't have enough questions for your query.",
        2: "Invalid Parameter: Arguments passed in aren't valid.",
        3: "Token Not Found: Session Token does not exist.",
        4: "Token Empty: Session Token is empty.",
        5: "Rate Limit Exceeded: Too many requests.",
    }

    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self.base_url = base_url
        self.timeout = timeout
