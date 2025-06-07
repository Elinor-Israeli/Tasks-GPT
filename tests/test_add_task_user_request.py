import pytest
from backend.request.add_task_user_request import AddTaskUserRequest

class MockTaskService:
    def __init__(self):
        self.created_tasks = []

    async def create_task(self, task_data):
        self.created_tasks.append(task_data)
        return {"id": 1, **task_data}

class MockGenAIClient:
    def extract_task_data(self, user_input):
        return {
            "name": "Buy milk", 
            "date": "2025-06-30"
        }

@pytest.mark.asyncio
async def test_add_task_user_request_handle():
    mock_task_service = MockTaskService()
    mock_genai_client = MockGenAIClient()
    user_id = 123
    user_input = "Buy milk"

    request = AddTaskUserRequest.create(
        user_id=user_id,
        task_service=mock_task_service,
        genai_client=mock_genai_client,
        user_input=user_input
    )

    await request.handle()

    assert len(mock_task_service.created_tasks) == 1
    created_task = mock_task_service.created_tasks[0]
    assert created_task["title"] == "Buy milk"
    assert created_task["user_id"] == user_id
