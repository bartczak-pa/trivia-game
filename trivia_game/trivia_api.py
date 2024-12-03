"""Module for interacting with the trivia API."""

from dataclasses import dataclass
from typing import Any, TypedDict


class TriviaResponse(TypedDict):
    response_code: int
    results: list[dict[str, Any]]


@dataclass(frozen=True)
class ResponseType:
    success: bool
    data: dict[str, Any]
    error: str | None = None
