from enum import IntEnum

class TriviaResponseCode(IntEnum):
    SUCCESS: int
    NO_RESULTS: int
    INVALID_PARAMETER: int
    TOKEN_NOT_FOUND: int
    TOKEN_EMPTY: int
    RATE_LIMIT: int
