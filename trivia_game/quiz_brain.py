from trivia_game import app_interface, trivia_api


class QuizBrain:
    def __init__(self, interface: "app_interface.AppInterface") -> None:
        """Create the quiz brain object

        Args:
            interface (app_interface.AppInterface): The main application interface

        Attributes:
            interface (app_interface.AppInterface): The main application interface
            self.api_client (trivia_api.TriviaAPIClient): The trivia API client
            self.categories (dict[str, str]): The trivia categories

        """
        self.interface = interface
        self.api_client: trivia_api.TriviaAPIClient = trivia_api.TriviaAPIClient()
        self.categories: dict[str, str] = self.api_client.fetch_categories()
        print(self.categories)
