import pytest
from backend.request.edit_task_user_request import EditTaskUserRequest

class MockTaskService:
    def __init__(self):
        self.updated_tasks = {}

    async def get_task_by_id(self, task_id):
        return {"id": int(task_id), "title": "Old title", "due_date": "2025-06-01"}

    async def update_task(self, task_id, data):
        self.updated_tasks[task_id] = data

class MockGenAIClient:
    def extract_task_id(self, user_input):
        return 5 

    def interpret_edit_task_command(self, user_input, edit_options):
        return "1"

@pytest.mark.asyncio
async def test_edit_task_user_request_handle(monkeypatch):
    mock_task_service = MockTaskService()
    mock_genai_client = MockGenAIClient()
    user_id = 123
    user_input = "edit task 5"

    monkeypatch.setattr("builtins.input", lambda prompt: "New Task Title")

    request = await EditTaskUserRequest.create(
        user_id,
        mock_task_service,
        mock_genai_client,
        user_input
    )

    assert request is not None

    await request.handle()

    assert 5 in mock_task_service.updated_tasks
    updated_data = mock_task_service.updated_tasks[5]
    assert updated_data["title"] == "New Task Title"
