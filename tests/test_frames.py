from trivia_game.view.frames.base_frame import BaseFrame


class TestBaseFrame:
    def test_init_calls_setup_methods(self, mocker, base_frame):
        """Test if initialization calls required setup methods"""
        mock_grid = mocker.patch.object(BaseFrame, "_setup_grid")
        mock_widgets = mocker.patch.object(BaseFrame, "_create_widgets")

        frame = BaseFrame(None, base_frame.controller)

        mock_grid.assert_called_once()
        mock_widgets.assert_called_once()


class TestMainMenuFrame:
    def test_button_mapping_commands(self, main_menu_frame, mock_controller):
        """Test if button commands are properly mapped"""
        # Test navigation buttons
        main_menu_frame.button_mapping["Start Game"]()
        mock_controller.show_frame.assert_called_with("StartGameFrame")

        main_menu_frame.button_mapping["High Scores"]()
        mock_controller.show_frame.assert_called_with("ScoreboardFrame")

        main_menu_frame.button_mapping["Settings"]()
        mock_controller.show_frame.assert_called_with("AppSettingsFrame")

        # Test quit button
        main_menu_frame.button_mapping["Exit"]()
        mock_controller.quit.assert_called_once()


class TestStartGameFrame:
    def test_init_variables_default_values(self, start_game_frame):
        """Test if variables are initialized with correct default values"""
        assert start_game_frame.category_var.get() == "Any Category"
        assert start_game_frame.difficulty_var.get() == "Any Difficulty"
        assert start_game_frame.type_var.get() == "Any Type"

    def test_create_option_menus_calls_quiz_brain(self, start_game_frame, mock_controller):
        """Test if option menus creation calls appropriate quiz_brain methods"""

        # Reset mock call counts since _create_option_menus is called during __init__
        mock_controller.quiz_brain.get_available_categories.reset_mock()

        mock_controller.quiz_brain.get_available_difficulties.reset_mock()
        mock_controller.quiz_brain.get_available_question_types.reset_mock()

        # Act
        start_game_frame._create_option_menus()

        # Assert
        mock_controller.quiz_brain.get_available_categories.assert_called_once()
        mock_controller.quiz_brain.get_available_difficulties.assert_called_once()
        mock_controller.quiz_brain.get_available_question_types.assert_called_once()

    def test_get_selected_values_calls_quiz_brain(self, start_game_frame, mock_controller):
        """Test if get_selected_values calls appropriate quiz_brain methods"""
        start_game_frame.get_selected_values()

        mock_controller.quiz_brain.get_category_id.assert_called_once_with("Any Category")
        mock_controller.quiz_brain.get_difficulty_value.assert_called_once_with("Any Difficulty")
        mock_controller.quiz_brain.get_question_type_value.assert_called_once_with("Any Type")

    def test_get_selected_values_returns_correct_tuple(self, start_game_frame, mock_controller):
        """Test if get_selected_values returns correct values"""
        mock_controller.quiz_brain.get_category_id.return_value = "9"
        mock_controller.quiz_brain.get_difficulty_value.return_value = "easy"
        mock_controller.quiz_brain.get_question_type_value.return_value = "multiple"

        result = start_game_frame.get_selected_values()
        assert result == ("9", "easy", "multiple")

    def test_start_game_loads_questions(self, start_game_frame, mock_controller):
        """Test if start_game calls load_questions with correct values"""
        mock_controller.quiz_brain.get_category_id.return_value = "9"
        mock_controller.quiz_brain.get_difficulty_value.return_value = "easy"
        mock_controller.quiz_brain.get_question_type_value.return_value = "multiple"

        start_game_frame._start_game()

        mock_controller.quiz_brain.load_questions.assert_called_once_with("9", "easy", "multiple")
