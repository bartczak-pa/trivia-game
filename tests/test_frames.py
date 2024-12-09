from unittest.mock import Mock

import customtkinter as ctk
import pytest

from trivia_game.base_types import AppControllerProtocol


class TestStartGameFrame:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        # Create mock controller with quiz_brain
        self.mock_controller = Mock(spec=AppControllerProtocol)
        self.mock_controller.quiz_brain = Mock()

        # Create parent frame mock with tk attribute
        self.mock_parent = Mock(spec=ctk.CTkFrame)
        self.mock_parent.tk = Mock()

        # Setup quiz brain mock with categories
        self.mock_controller.quiz_brain.categories = {"History": "1", "Science": "2"}

        from trivia_game.view.frames import StartGameFrame

        self.frame = StartGameFrame(self.mock_parent, self.mock_controller)

    def test_get_selected_values(self):
        """Test getting all selected values"""
        # Arrange
        test_cases = [
            {
                "category": "Any Category",
                "difficulty": "Any Difficulty",
                "type": "Any Type",
                "expected": (None, None, None),
            },
            {
                "category": "History",
                "difficulty": "Easy",
                "type": "Multiple Choice",
                "expected": ("1", "easy", "multiple"),
            },
        ]

        # Act & Assert
        for case in test_cases:
            self.frame.category_var.set(case["category"])
            self.frame.difficulty_var.set(case["difficulty"])
            self.frame.type_var.set(case["type"])

            result = self.frame.get_selected_values()
            assert result == case["expected"]
