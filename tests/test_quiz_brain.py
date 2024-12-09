from unittest.mock import Mock

import pytest

from trivia_game.base_types import AppControllerProtocol
from trivia_game.exceptions import CategoryError


class TestQuizBrain:
    @pytest.fixture(autouse=True)
    def setup(self, trivia_client, mock_categories_response):
        """Setup test environment"""
        self.mock_controller = Mock(spec=AppControllerProtocol)

        from trivia_game.quiz_brain import QuizBrain

        self.quiz_brain = QuizBrain(self.mock_controller)

        # Expected categories from mock response
        self.expected_categories = {"General Knowledge": "9", "Entertainment: Books": "10", "Entertainment: Film": "11"}

    def test_load_categories_success(self, mock_categories_response):
        """Test successful category loading"""
        # Arrange
        self.quiz_brain.api_client.fetch_categories = Mock(return_value=self.expected_categories)

        # Act
        self.quiz_brain._load_categories()

        # Assert
        assert self.quiz_brain.categories == self.expected_categories
        self.quiz_brain.api_client.fetch_categories.assert_called_once()
        self.mock_controller.show_error.assert_not_called()

    def test_load_categories_handles_error(self):
        """Test category loading error handling"""
        # Arrange
        error_message = "API Error"
        self.quiz_brain.api_client.fetch_categories = Mock(side_effect=CategoryError(error_message))

        # Act
        self.quiz_brain._load_categories()

        # Assert
        self.mock_controller.show_error.assert_called_once_with(
            f"Error loading categories: {error_message}. Please try again later."
        )
