import pytest
from backend.request.mark_done_user_request import MarkDoneUserRequest

class MockTaskService:
    def __init__(self):
        self.tasks = {7: {"id": 7, "title": "Test Task", "done": False}}
        self.updated_tasks = {}

    async def get_task_by_id(self, task_id):
        return self.tasks.get(int(task_id))

    async def update_task(self, task_id, data):
        self.updated_tasks[int(task_id)] = data
class MockGenAIClient:
    def extract_task_id(self, user_input):
        return 7  

@pytest.mark.asyncio
async def test_mark_done_user_request_handle():
    mock_task_service = MockTaskService()
    mock_genai_client = MockGenAIClient()
    user_id = 123
    user_input = "mark task 7 as done"

    request = MarkDoneUserRequest.create(
        user_id,
        mock_task_service,
        mock_genai_client,
        user_input
    )

    await request.handle()

    assert 7 in mock_task_service.updated_tasks
    updated_data = mock_task_service.updated_tasks[7]
    assert updated_data["done"] is True        