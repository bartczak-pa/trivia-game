import customtkinter as ctk

from trivia_game.view.frames.quiz_frames import BaseQuizFrame


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

        assert base_quiz_frame.question_frame.cget("fg_color") == "green"

        mock_controller.quiz_brain.check_answer.return_value = False
        base_quiz_frame._handle_answer("test")

        assert base_quiz_frame.question_frame.cget("fg_color") == "red"

    def test_display_question_updates_label(self, base_quiz_frame, mock_controller, mock_question):
        """Test if display_question updates label text"""
        mock_controller.quiz_brain.current_question = mock_question
        base_quiz_frame.display_question()

        assert base_quiz_frame.question_label.cget("text") == mock_question.question


class TestTrueFalseQuizFrame:
    def test_create_answer_buttons_with_question(self, true_false_frame, mock_controller, mock_question):
        """Test if True/False buttons are created when question exists"""
        mock_controller.quiz_brain.current_question = mock_question
        true_false_frame._create_answer_buttons()

        # Get all widgets recursively
        buttons = []
        for widget in true_false_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != true_false_frame.question_frame:
                buttons.extend(w for w in widget.winfo_children() if isinstance(w, ctk.CTkButton))

        assert len(buttons) == 2
        button_texts = sorted(b.cget("text") for b in buttons)
        assert button_texts == ["False", "True"]

    def test_create_answer_buttons_without_question(self, true_false_frame, mock_controller):
        """Test if no buttons are created when no question exists"""
        mock_controller.quiz_brain.current_question = None
        true_false_frame._create_answer_buttons()

        buttons = [w for w in true_false_frame.winfo_children() if isinstance(w, ctk.CTkButton)]
        assert not buttons


class TestMultipleChoiceQuizFrame:
    def test_create_answer_buttons_with_question(self, multiple_choice_frame, mock_controller, mock_question):
        """Test if multiple choice buttons are created when question exists"""
        mock_controller.quiz_brain.current_question = mock_question
        mock_question.all_answers.return_value = ["A", "B", "C", "D"]

        multiple_choice_frame._create_answer_buttons()

        # Get all widgets recursively
        buttons = []
        for widget in multiple_choice_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != multiple_choice_frame.question_frame:
                buttons.extend(w for w in widget.winfo_children() if isinstance(w, ctk.CTkButton))

        assert len(buttons) == 4
        button_texts = [b.cget("text") for b in buttons]
        assert all(text in ["A", "B", "C", "D"] for text in button_texts)

    def test_create_answer_buttons_without_question(self, multiple_choice_frame, mock_controller):
        """Test if no buttons are created when no question exists"""
        mock_controller.quiz_brain.current_question = None
        multiple_choice_frame._create_answer_buttons()

        buttons = [w for w in multiple_choice_frame.winfo_children() if isinstance(w, ctk.CTkButton)]
        assert not buttons
