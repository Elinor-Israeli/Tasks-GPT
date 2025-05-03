import pytest
from dotenv import load_dotenv
from genai import AICommandInterpreter
import os

@pytest.fixture
def genai_client():
    load_dotenv()
    return AICommandInterpreter(os.environ['GEMINI_API_KEY'])


@pytest.mark.parametrize(
    ("user_input", "option"),
    (
        ("Show me all the tasks that I've completed so far", "1"),
        ("Show me all my incomplete tasks", "2")
    ),
)
def test_view_command(
    genai_client,
    user_input: str,
    option: str,
):
    view_option = """
    1. Completed Tasks
    2. Incomplete Tasks
    3. Overdue Tasks
    4. Upcoming Tasks
    5. All Tasks
    """

    assert genai_client.interpret_view_task_command(user_input, view_option) == option