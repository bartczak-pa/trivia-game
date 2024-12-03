from enum import IntEnum


class TriviaResponseCode(IntEnum):
    SUCCESS: int = 0
    NO_RESULTS: int = 1
    INVALID_PARAMETER: int = 2
    TOKEN_NOT_FOUND: int = 3
    TOKEN_EMPTY: int = 4
    RATE_LIMIT: int = 5
