import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from trivia_game.exceptions import CategoryError
from trivia_game.models import Question, ScoreboardEntry
from trivia_game.quiz_brain import QuizBrain
from trivia_game.trivia_api import TriviaAPIClient


class TestQuizBrainInitialization:
    def test_init(self, mock_controller):
        quiz_brain = QuizBrain(mock_controller)
        assert quiz_brain.controller == mock_controller
        assert quiz_brain.score == 0
        assert quiz_brain.current_question is None
        assert quiz_brain.questions == []
        assert isinstance(quiz_brain.api_client, TriviaAPIClient)


class TestQuizBrainCategories:
    def test_load_categories_success(self, quiz_brain):
        expected_categories = {"General Knowledge": "9", "Entertainment: Books": "10"}
        quiz_brain.api_client.fetch_categories = Mock(return_value=expected_categories)

        quiz_brain._load_categories()

        assert quiz_brain.categories == expected_categories
        quiz_brain.api_client.fetch_categories.assert_called_once()
        quiz_brain.controller.show_error.assert_not_called()

    def test_load_categories_handles_error(self, quiz_brain):
        error_message = "API Error"
        quiz_brain.api_client.fetch_categories = Mock(side_effect=CategoryError(error_message))

        quiz_brain._load_categories()

        quiz_brain.controller.show_error.assert_called_once_with(
            f"Error loading categories: {error_message}. Please try again later."
        )

    def test_get_available_categories(self, quiz_brain):
        quiz_brain.categories = {"History": "1", "Science": "2"}
        result = quiz_brain.get_available_categories()
        assert result == ["Any Category", "History", "Science"]

    def test_get_category_id_returns_none_for_any_category(self, quiz_brain):
        quiz_brain.categories = {"History": "1", "Science": "2"}
        result = quiz_brain.get_category_id("Any Category")
        assert result is None

    def test_get_category_id_returns_correct_id(self, quiz_brain):
        quiz_brain.categories = {"History": "1", "Science": "2"}
        result = quiz_brain.get_category_id("History")
        assert result == "1"

    def test_get_category_id_invalid_category(self, quiz_brain):
        quiz_brain.categories = {"History": "1", "Science": "2"}
        with pytest.raises(KeyError):
            quiz_brain.get_category_id("Invalid Category")


class TestQuizBrainDifficulties:
    def test_get_available_difficulties(self, quiz_brain):
        result = quiz_brain.get_available_difficulties()
        assert result == ["Any Difficulty", "Easy", "Medium", "Hard"]

    def test_get_difficulty_value_returns_none_for_any(self, quiz_brain):
        result = quiz_brain.get_difficulty_value("Any Difficulty")
        assert result is None

    @pytest.mark.parametrize("input_value,expected", [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")])
    def test_get_difficulty_value_returns_lowercase(self, quiz_brain, input_value, expected):
        result = quiz_brain.get_difficulty_value(input_value)
        assert result == expected


class TestQuizBrainQuestionTypes:
    def test_get_available_question_types(self, quiz_brain):
        result = quiz_brain.get_available_question_types()
        assert result == ["Any Type", "Multiple Choice", "True / False"]

    @pytest.mark.parametrize("input_value,expected", [("Multiple Choice", "multiple"), ("True / False", "boolean")])
    def test_get_question_type_value_returns_correct_type(self, quiz_brain, input_value, expected):
        result = quiz_brain.get_question_type_value(input_value)
        assert result == expected

    def test_get_question_type_value_invalid_type(self, quiz_brain):
        with pytest.raises(KeyError):
            quiz_brain.get_question_type_value("Invalid Type")


class TestQuizBrainQuestions:
    def test_load_questions_success(self, quiz_brain, mock_questions_success):
        expected_questions = [
            Question(
                type="multiple",
                difficulty="medium",
                category="Test",
                question="Test1?",
                correct_answer="A",
                incorrect_answers=["B", "C", "D"],
            )
        ]
        quiz_brain.api_client.fetch_questions = Mock(return_value=expected_questions)

        quiz_brain.load_questions(category="9", difficulty="easy", question_type="multiple")

        assert quiz_brain.questions == expected_questions
        assert quiz_brain.score == 0
        quiz_brain.api_client.fetch_questions.assert_called_once_with(
            category="9", difficulty="easy", question_type="multiple"
        )

    def test_load_questions_handles_error(self, quiz_brain):
        error_message = "API Error"
        quiz_brain.api_client.fetch_questions = Mock(side_effect=Exception(error_message))

        quiz_brain.load_questions(None, None, None)

        quiz_brain.controller.show_error.assert_called_once_with(f"Error loading questions: {error_message}")

    def test_show_next_question_with_questions(self, quiz_brain):
        test_questions = [
            Question(
                type="boolean",
                difficulty="easy",
                category="Test",
                question="Test1?",
                correct_answer="True",
                incorrect_answers=["False"],
            ),
            Question(
                type="multiple",
                difficulty="medium",
                category="Test",
                question="Test2?",
                correct_answer="A",
                incorrect_answers=["B", "C", "D"],
            ),
        ]
        quiz_brain.questions = test_questions.copy()

        quiz_brain.show_next_question()

        assert quiz_brain.current_question == test_questions[0]
        assert len(quiz_brain.questions) == 1
        quiz_brain.controller.show_frame.assert_called_once_with("TrueFalseQuizFrame")

    def test_show_next_question_empty_questions(self, quiz_brain):
        quiz_brain.questions = []
        quiz_brain.end_game = Mock()

        quiz_brain.show_next_question()

        quiz_brain.end_game.assert_called_once()


class TestQuizBrainScoring:
    def test_check_answer_correct(self, quiz_brain, mock_question):
        quiz_brain.current_question = mock_question
        quiz_brain.score = 0
        mock_question.correct_answer = "True"
        mock_question.difficulty = "medium"

        result = quiz_brain.check_answer("True")

        assert result is True
        assert quiz_brain.score == 200

    def test_check_answer_incorrect(self, quiz_brain, mock_question):
        quiz_brain.current_question = mock_question
        quiz_brain.score = 0
        mock_question.correct_answer = "True"
        mock_question.difficulty = "medium"

        result = quiz_brain.check_answer("False")

        assert result is False
        assert quiz_brain.score == 0

    @pytest.mark.parametrize("difficulty,expected_score", [("easy", 100), ("medium", 200), ("hard", 300)])
    def test_calculate_score(self, quiz_brain, difficulty, expected_score):
        assert quiz_brain._calculate_score(difficulty) == expected_score

    def test_calculate_score_unknown_difficulty(self, quiz_brain):
        multiplier = quiz_brain.DIFFICULTY_MULTIPLIER.get("unknown", 1)
        assert multiplier == 1


class TestQuizBrainGameFlow:
    @pytest.mark.gui
    def test_end_game_logic(self, quiz_brain, mocker):
        """Test end game logic without GUI dependencies"""
        # Mock save_score to avoid file operations
        mock_save = mocker.patch.object(quiz_brain, "save_score")
        initial_score = quiz_brain.score = 500

        # Mock show_frame to avoid GUI
        mock_show_frame = mocker.patch.object(quiz_brain.controller, "show_frame")

        quiz_brain.end_game()

        # Verify core logic
        assert quiz_brain.score == 0  # Score should be reset
        mock_show_frame.assert_called_once_with("ScoreboardFrame")

    def test_end_game_no_name(self, quiz_brain, mocker):
        mock_dialog = mocker.patch("trivia_game.view.dialogs.score_dialog.ScoreDialog")
        mock_dialog.return_value.get_input.return_value = None
        mock_save = mocker.patch.object(quiz_brain, "save_score")

        quiz_brain.end_game()

        mock_save.assert_not_called()
        quiz_brain.controller.show_frame.assert_called_once_with("ScoreboardFrame")
        assert quiz_brain.score == 0

    def test_save_to_json(self, quiz_brain, tmp_path, mocker):
        """Test saving score entry to JSON with temp file"""
        # Create temporary scores file
        scores_dir = tmp_path / "scores"
        scores_dir.mkdir(parents=True, exist_ok=True)
        scores_file = scores_dir / "scores.json"
        scores_file.write_text("[]")  # Initialize with empty array

        # Patch Path to return our temp file
        mocker.patch("trivia_game.quiz_brain.Path", return_value=scores_file)

        # Create test entry
        entry = ScoreboardEntry(player_name="Player1", score=500, date=datetime(2024, 12, 15, 16, 57))

        # Test saving to file
        quiz_brain._save_to_json(entry)

        # Verify saved data
        with scores_file.open() as f:
            scores = json.load(f)

        assert len(scores) == 1
        assert scores[0]["player"] == "Player1"
        assert scores[0]["score"] == 500
        assert scores[0]["date"] == "2024-12-15T16:57:00"
