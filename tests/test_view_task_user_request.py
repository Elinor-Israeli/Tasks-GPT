import pytest
from backend.request.view_tasks_user_request import ViewTasksUserRequest

class MockTaskService:
    def __init__(self):
        self.tasks = [
            {"id": 1, "title": "Task 1", "done": True, "due_date": "2025-06-01"},
            {"id": 2, "title": "Task 2", "done": False, "due_date": "2025-06-10"},
            {"id": 3, "title": "Task 3", "done": True, "due_date": None},
        ]

    async def get_tasks(self, user_id, done=None):
        if done is None:
            return self.tasks
        else:
            return [task for task in self.tasks if task["done"] == done]

class MockGenAIClient:
    def interpret_view_task_command(self, user_input, view_option):
        return "1" 

@pytest.mark.asyncio
async def test_view_tasks_user_request_handle(capfd):
    mock_task_service = MockTaskService()
    mock_genai_client = MockGenAIClient()
    user_id = 123
    user_input = "view completed tasks"

    request = ViewTasksUserRequest.create(
        user_id,
        mock_task_service,
        mock_genai_client,
        user_input
    )

    await request.handle()

    out, err = capfd.readouterr()

    assert "--- TASKS ---" in out
    assert "Task 1" in out
    assert "✅" in out
