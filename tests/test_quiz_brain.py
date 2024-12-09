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

    def test_get_available_categories_success(self):
        """Test successful retrieval of categories with 'Any Category' option"""
        # Arrange
        self.quiz_brain.categories = {"History": "1", "Animals": "2", "Geography": "3"}

        # Act
        result = self.quiz_brain.get_available_categories()

        # Assert
        assert result[0] == "Any Category"
        assert result[1:] == ["Animals", "Geography", "History"]
        assert len(result) == len(self.quiz_brain.categories) + 1

    def test_get_available_categories_empty_categories(self):
        """Test retrieval with empty categories dictionary"""
        # Arrange
        self.quiz_brain.categories = {}

        # Act
        result = self.quiz_brain.get_available_categories()

        # Assert
        assert result == ["Any Category"]
        assert len(result) == 1

    def test_get_category_id_returns_none_for_any_category(self):
        """Test that 'Any Category' returns None"""
        # Arrange
        self.quiz_brain.categories = {"History": "1", "Science": "2"}

        # Act
        result = self.quiz_brain.get_category_id("Any Category")

        # Assert
        assert result is None

    def test_get_category_id_returns_correct_id(self):
        """Test that correct category ID is returned"""
        # Arrange
        self.quiz_brain.categories = {"History": "1", "Science": "2"}

        # Act
        result = self.quiz_brain.get_category_id("History")

        # Assert
        assert result == "1"

    def test_get_category_id_invalid_category(self):
        """Test that invalid category raises KeyError"""
        # Arrange
        self.quiz_brain.categories = {"History": "1", "Science": "2"}

        # Act & Assert
        with pytest.raises(KeyError):
            self.quiz_brain.get_category_id("Invalid Category")

    def test_get_available_difficulties(self):
        """Test getting difficulty levels"""
        # Act
        result = self.quiz_brain.get_available_difficulties()

        # Assert
        expected = ["Any Difficulty", "Easy", "Medium", "Hard"]
        assert result == expected
        assert len(result) == 4
        assert result[0] == "Any Difficulty"

    def test_get_available_question_types(self):
        """Test getting question types"""
        # Act
        result = self.quiz_brain.get_available_question_types()

        # Assert
        expected = ["Any Type", "Multiple Choice", "True / False"]
        assert result == expected
        assert len(result) == 3
        assert result[0] == "Any Type"

    def test_get_difficulty_value_returns_none_for_any(self):
        """Test that 'Any Difficulty' returns None"""
        # Act
        result = self.quiz_brain.get_difficulty_value("Any Difficulty")

        # Assert
        assert result is None

    def test_get_difficulty_value_returns_lowercase(self):
        """Test that difficulty values are returned in lowercase"""
        # Arrange
        test_cases = {"Easy": "easy", "Medium": "medium", "Hard": "hard"}

        # Act & Assert
        for input_value, expected in test_cases.items():
            result = self.quiz_brain.get_difficulty_value(input_value)
            assert result == expected

    def test_get_question_type_value_returns_correct_type(self):
        """Test that question types are correctly mapped"""
        # Arrange
        test_cases = {"Multiple Choice": "multiple", "True/False": "boolean"}

        # Act & Assert
        for input_value, expected in test_cases.items():
            result = self.quiz_brain.get_question_type_value(input_value)
            assert result == expected

    def test_get_question_type_value_invalid_type(self):
        """Test that invalid question type raises KeyError"""
        # Act & Assert
        with pytest.raises(KeyError):
            self.quiz_brain.get_question_type_value("Invalid Type")
