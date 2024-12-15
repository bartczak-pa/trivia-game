import pytest

from trivia_game.trivia_api import TriviaAPIClient


@pytest.mark.integration
class TestTriviaAPIIntegration:
    def test_real_categories_fetch(self):
        """Test fetching categories from actual API"""
        client = TriviaAPIClient()
        try:
            categories = client.fetch_categories()
            assert len(categories) > 0
            assert all(isinstance(name, str) and isinstance(id_, str) for name, id_ in categories.items())
        finally:
            client.session.close()

    @pytest.mark.integration
    def test_real_questions_fetch(self):
        """Test fetching questions from actual API"""
        client = TriviaAPIClient()
        try:
            questions = client.fetch_questions(amount=10)
            assert len(questions) == 10
            for question in questions:
                assert question.question
                assert question.correct_answer
                assert question.incorrect_answers
        finally:
            client.session.close()
