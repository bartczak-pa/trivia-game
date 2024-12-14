import pytest

from trivia_game.view.frames.quiz_frames import BaseQuizFrame, TrueFalseQuizFrame


@pytest.mark.usefixtures("mock_ctk")
class TestBaseQuizFrame:
    def test_create_widgets_calls_required_methods(self, mocker, base_quiz_frame):
        """Test if _create_widgets calls all required methods"""
        mock_clear = mocker.patch.object(BaseQuizFrame, "_clear_previous_widgets")
        mock_frame = mocker.patch.object(BaseQuizFrame, "_create_question_frame")
        mock_label = mocker.patch.object(BaseQuizFrame, "_create_question_label")
        mock_display = mocker.patch.object(BaseQuizFrame, "display_question")

        base_quiz_frame._create_widgets()

        mock_clear.assert_called_once()
        mock_frame.assert_called_once()
        mock_label.assert_called_once()
        mock_display.assert_called_once()

    def test_handle_answer_changes_frame_color(self, mocker, base_quiz_frame, mock_controller):
        """Test if _handle_answer changes frame color based on answer correctness"""
        mock_controller.quiz_brain.check_answer.return_value = True
        base_quiz_frame._handle_answer("test")
        base_quiz_frame.question_frame.configure.assert_called_with(fg_color="green")

        mock_controller.quiz_brain.check_answer.return_value = False
        base_quiz_frame._handle_answer("test")
        base_quiz_frame.question_frame.configure.assert_called_with(fg_color="red")

    def test_display_question_updates_label(self, base_quiz_frame, mock_controller, mock_question):
        """Test if display_question updates label text"""
        mock_controller.quiz_brain.current_question = mock_question
        base_quiz_frame.display_question()
        base_quiz_frame.question_label.configure.assert_called_with(text=mock_question.question)

    def test_refresh_calls_required_methods(self, mocker, base_quiz_frame):
        """Test if refresh calls display_question and _create_answer_buttons"""
        mock_display = mocker.patch.object(BaseQuizFrame, "display_question")
        mock_buttons = mocker.patch.object(BaseQuizFrame, "_create_answer_buttons")

        base_quiz_frame.refresh()

        mock_display.assert_called_once()
        mock_buttons.assert_called_once()

    def test_reset_and_continue(self, mocker, base_quiz_frame):
        """Test if _reset_and_continue resets color and shows next question"""
        mock_configure = mocker.patch.object(base_quiz_frame.question_frame, "configure")
        mock_show_next = mocker.patch.object(base_quiz_frame.controller.quiz_brain, "show_next_question")

        base_quiz_frame._reset_and_continue()

        mock_configure.assert_called_with(fg_color=("gray85", "gray25"))
        mock_show_next.assert_called_once()

    def test_create_answer_buttons_raises_error(self, base_quiz_frame):
        """Test if _create_answer_buttons raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            base_quiz_frame._create_answer_buttons()

    def test_update_score(self, mocker, base_quiz_frame):
        """Test if update_score updates label with current score"""
        base_quiz_frame.controller.quiz_brain.score = 500
        mock_configure = mocker.patch.object(base_quiz_frame.score_label, "configure")

        base_quiz_frame.update_score()

        mock_configure.assert_called_with(text="Score: 500")

    def test_create_widgets_calls_parent_and_buttons(self, mocker, true_false_frame):
        """Test if _create_widgets calls parent method and creates buttons"""
        mock_parent = mocker.patch.object(BaseQuizFrame, "_create_widgets")
        mock_buttons = mocker.patch.object(TrueFalseQuizFrame, "_create_answer_buttons")

        true_false_frame._create_widgets()

        mock_parent.assert_called_once()
        mock_buttons.assert_called_once()


@pytest.mark.usefixtures("mock_ctk")
class TestTrueFalseQuizFrame:
    def test_create_answer_buttons_with_question(self, mocker, true_false_frame, mock_controller, mock_question):
        """Test if True/False buttons are created when question exists"""
        mock_controller.quiz_brain.current_question = mock_question

        # Create a mock button frame to store buttons
        button_frame = mocker.Mock()
        button_frame.winfo_children.return_value = []

        # Mock CTkButton creation
        mock_buttons = []

        def mock_button(*args, **kwargs):
            mock_button = mocker.Mock()
            mock_button.cget = lambda x: kwargs.get("text")
            mock_buttons.append(mock_button)
            return mock_button

        mocker.patch("customtkinter.CTkButton", side_effect=mock_button)

        true_false_frame._create_answer_buttons()

        assert len(mock_buttons) == 2
        button_texts = sorted(b.cget("text") for b in mock_buttons)
        assert button_texts == ["False", "True"]


@pytest.mark.usefixtures("mock_ctk")
class TestMultipleChoiceQuizFrame:
    def test_create_answer_buttons_with_question(self, mocker, multiple_choice_frame, mock_controller, mock_question):
        """Test if multiple choice buttons are created when question exists"""
        # Setup mock question and answers
        mock_controller.quiz_brain.current_question = mock_question
        mock_question.all_answers.return_value = ["A", "B", "C", "D"]

        # Mock button creation
        mock_buttons = []

        def mock_button(*args, **kwargs):
            mock_button = mocker.Mock()
            mock_button.cget = lambda x: kwargs.get("text")
            mock_buttons.append(mock_button)
            return mock_button

        mocker.patch("customtkinter.CTkButton", side_effect=mock_button)

        # Create buttons
        multiple_choice_frame._create_answer_buttons()

        # Verify buttons
        assert len(mock_buttons) == 4
        assert all(b.cget("text") in ["A", "B", "C", "D"] for b in mock_buttons)
