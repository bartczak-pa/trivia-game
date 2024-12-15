import json
from unittest.mock import Mock, patch

import pytest


@pytest.mark.gui
class TestScoreboardFrame:
    def test_setup_grid(self, scoreboard_frame):
        with (
            patch.object(scoreboard_frame, "grid_rowconfigure") as mock_row,
            patch.object(scoreboard_frame, "grid_columnconfigure") as mock_col,
        ):
            scoreboard_frame._setup_grid()
            assert mock_row.call_count == 2
            assert mock_col.call_count == 1

    def test_create_widgets(self, scoreboard_frame):
        with patch("customtkinter.CTkScrollableFrame"), patch("customtkinter.CTkButton"):
            scoreboard_frame._create_widgets()
            assert hasattr(scoreboard_frame, "scores_frame")

    def test_load_scores_file_not_exists(self, scoreboard_frame):
        with (
            patch("pathlib.Path.exists", return_value=False),
            patch.object(scoreboard_frame, "_display_no_scores") as mock_display,
        ):
            scoreboard_frame.load_scores()
            mock_display.assert_called_once()

    def test_load_scores_empty_file(self, scoreboard_frame):
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "pathlib.Path.open", return_value=Mock(__enter__=Mock(return_value=Mock(read=Mock(return_value="[]"))))
            ),
            patch.object(scoreboard_frame, "_display_no_scores") as mock_display,
        ):
            scoreboard_frame.load_scores()
            mock_display.assert_called_once()

    def test_load_scores_success(self, scoreboard_frame, mocker):
        """Test successful loading of scores"""
        mock_scores = [{"player": "Test", "score": 100, "date": "2023-01-01T12:00:00"}]

        mock_open = mocker.mock_open(read_data=json.dumps(mock_scores))
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("pathlib.Path.open", mock_open)

        mock_display = mocker.patch.object(scoreboard_frame, "_display_scores")

        scoreboard_frame.load_scores()

        mock_display.assert_called_once_with(mock_scores)

    def test_display_scores(self, scoreboard_frame):
        mock_scores = [{"player": "Test", "score": 100, "date": "2023-01-01T12:00:00"}]
        with patch.object(scoreboard_frame, "_create_score_row") as mock_create_row:
            scoreboard_frame._display_scores(mock_scores)
            assert mock_create_row.call_count == 2  # Header + 1 score

    def test_format_date(self, scoreboard_frame):
        date_str = "2023-01-01T12:00:00"
        formatted = scoreboard_frame._format_date(date_str)
        assert formatted == "01 January 2023 12:00"

    def test_refresh(self, scoreboard_frame):
        with patch.object(scoreboard_frame, "load_scores") as mock_load:
            scoreboard_frame.refresh()
            mock_load.assert_called_once()
