"""Module for Trivia API exceptions"""


class TriviaAPIError(Exception):
    """Base exception for Trivia API errors"""

    pass


class NoResultsError(TriviaAPIError):
    """Not enough questions available"""

    pass


class InvalidParameterError(TriviaAPIError):
    """Invalid parameters provided"""

    pass


class TokenError(TriviaAPIError):
    """Token-related errors"""

    pass


class RateLimitError(TriviaAPIError):
    """Rate limit exceeded"""

    pass


class CategoryError(TriviaAPIError):
    """Exception for category-related errors"""

    pass
