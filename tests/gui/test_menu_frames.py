import pytest


@pytest.mark.gui
class TestMainMenuFrame:
    def test_setup_grid(self, main_menu_frame, mocker):
        mock_rowconfigure = mocker.patch.object(main_menu_frame, "grid_rowconfigure")
        mock_columnconfigure = mocker.patch.object(main_menu_frame, "grid_columnconfigure")

        main_menu_frame._setup_grid()

        assert mock_rowconfigure.call_count == 2
        mock_columnconfigure.assert_called_once()

    def test_create_widgets(self, main_menu_frame, mocker):
        mock_button = mocker.Mock()
        mocker.patch("customtkinter.CTkButton", return_value=mock_button)

        main_menu_frame._create_widgets()

        assert len(main_menu_frame.button_mapping) == 4
        assert mock_button.grid.call_count == 4


@pytest.mark.gui
class TestAppSettingsFrame:
    def test_setup_grid(self, app_settings_frame, mocker):
        mock_rowconfigure = mocker.patch.object(app_settings_frame, "grid_rowconfigure")
        mock_columnconfigure = mocker.patch.object(app_settings_frame, "grid_columnconfigure")

        app_settings_frame._setup_grid()

        assert mock_rowconfigure.call_count == 2
        mock_columnconfigure.assert_called_once()

    def test_create_widgets(self, app_settings_frame, mocker):
        mock_label = mocker.Mock()
        mock_button = mocker.Mock()
        mocker.patch("customtkinter.CTkLabel", return_value=mock_label)
        mocker.patch("customtkinter.CTkButton", return_value=mock_button)

        app_settings_frame._create_widgets()

        mock_label.grid.assert_called_once()
        mock_button.grid.assert_called_once()


@pytest.mark.gui
class TestStartGameFrame:
    def test_setup_grid(self, start_game_frame, mocker):
        mock_rowconfigure = mocker.patch.object(start_game_frame, "grid_rowconfigure")
        mock_columnconfigure = mocker.patch.object(start_game_frame, "grid_columnconfigure")

        start_game_frame._setup_grid()

        assert mock_rowconfigure.call_count == 3
        assert mock_columnconfigure.call_count == 2

    def test_create_option_menus(self, start_game_frame, mocker):
        mock_label = mocker.Mock()
        mock_menu = mocker.Mock()
        mocker.patch("customtkinter.CTkLabel", return_value=mock_label)
        mocker.patch("customtkinter.CTkOptionMenu", return_value=mock_menu)

        start_game_frame._create_option_menus()

        assert mock_label.grid.call_count == 3
        assert mock_menu.grid.call_count == 3

    def test_get_selected_values(self, start_game_frame, mock_quiz_brain):
        values = start_game_frame.get_selected_values()

        assert values == ("9", "easy", "multiple")
        mock_quiz_brain.get_category_id.assert_called_once()
        mock_quiz_brain.get_difficulty_value.assert_called_once()
        mock_quiz_brain.get_question_type_value.assert_called_once()

    def test_start_game(self, start_game_frame, mock_quiz_brain):
        start_game_frame._start_game()

        mock_quiz_brain.load_questions.assert_called_once_with("9", "easy", "multiple")
