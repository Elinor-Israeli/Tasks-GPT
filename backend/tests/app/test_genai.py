import unittest
from unittest.mock import MagicMock
from datetime import date
from app.src.utils.menus import MenuChoice
from app.src.genai import AICommandInterpreter

class TestAICommandInterpreter(unittest.TestCase):
    def setUp(self):
        self.api_key = "fake-key"
        self.ai = AICommandInterpreter(api_key=self.api_key)
        self.mock_model = MagicMock()
        self.ai.client.models.generate_content = self.mock_model

    def test_interpret_command_valid(self):
        self.mock_model.return_value.text = "2"
        choice = self.ai.interpret_command("add", "1. View Tasks\n2. Add Task")
        self.assertEqual(choice, MenuChoice.ADD_TASK)

    def test_interpret_command_invalid_option(self):
        self.mock_model.return_value.text = "invalid"
        choice = self.ai.interpret_command("blah", "1. Add\n2. View")
        self.assertEqual(choice, MenuChoice.NONE)

    def test_interpret_command_exception_handling(self):
        self.mock_model.side_effect = Exception("API error")
        choice = self.ai.interpret_command("add", "1. Add\n2. View")
        self.assertEqual(choice, MenuChoice.NONE)
        self.mock_model.side_effect = None

    def test_interpret_view_task_command(self):
        self.mock_model.return_value.text = "2"
        result = self.ai.interpret_view_task_command("show completed", "1. All\n2. Completed")
        self.assertEqual(result, "2")

    def test_interpret_edit_task_command(self):
        self.mock_model.return_value.text = "1"
        result = self.ai.interpret_edit_task_command("change title", "1. Title\n2. Date")
        self.assertEqual(result, "1")

    def test_extract_task_data_valid(self):
        today = date.today().strftime("%Y-%m-%d")
        self.mock_model.return_value.text = f"""```json
        {{
            "name": "Buy milk",
            "date": "{today}"
        }}
        ```"""
        result = self.ai.extract_task_data("Buy milk today")
        self.assertEqual(result["name"], "Buy milk")
        self.assertEqual(result["date"], today)

    def test_extract_task_data_invalid_json(self):
        self.mock_model.return_value.text = "not json"
        data = self.ai.extract_task_data("nonsense")
        self.assertEqual(data, {"name": None, "date": None})

    def test_extract_task_data_api_failure(self):
        self.mock_model.side_effect = Exception("Data API error")
        data = self.ai.extract_task_data("Buy milk today")
        self.assertEqual(data, {"name": None, "date": None})
        self.mock_model.side_effect = None

    def test_extract_task_id_or_title_valid(self):
        self.mock_model.return_value.text = '{"task_id": 123, "task_title": "Clean"}'
        result = self.ai.extract_task_id_or_title("Mark task 123 done")
        self.assertEqual(result["task_id"], 123)
        self.assertEqual(result["task_title"], "Clean")

    def test_extract_task_id_or_title_invalid_json(self):
        self.mock_model.return_value.text = "invalid"
        result = self.ai.extract_task_id_or_title("nonsense")
        self.assertEqual(result, {"task_id": None, "task_title": None})

    def test_extract_task_id_or_title_api_failure(self):
        self.mock_model.side_effect = Exception("ID API fail")
        result = self.ai.extract_task_id_or_title("Finish task")
        self.assertEqual(result, {"task_id": None, "task_title": None})
        self.mock_model.side_effect = None

    def test_interpret_command_add_task_exact(self):
        self.mock_model.return_value.text = "2"
        result = self.ai.interpret_command("add a task", "1. View Tasks\n2. Add Task")
        self.assertEqual(result, MenuChoice.ADD_TASK)

    def test_interpret_command_typo(self):
        self.mock_model.return_value.text = "None"
        result = self.ai.interpret_command("create a tesl", "1. View Tasks\n2. Add Task")
        self.assertEqual(result, MenuChoice.NONE)
        


if __name__ == '__main__':
    unittest.main()
