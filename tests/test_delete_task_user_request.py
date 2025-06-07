import pytest
from backend.request.delete_task_user_request import DeleteTaskUserRequest

class MockTaskService:
    def __init__(self):
        self.deleted_tasks = []

    async def delete_task(self, task_id):
        self.deleted_tasks.append(task_id)

class MockGenAIClient:
    def extract_task_id(self, user_input):
        return 4   

@pytest.mark.asyncio
async def test_delete_task_user_request_handle():
    mock_task_service = MockTaskService()
    mock_genai_client = MockGenAIClient()
    user_id = 123
    user_input = "delete task 4"

    request = DeleteTaskUserRequest.create(
        user_id,
        mock_task_service,
        mock_genai_client,
        user_input
    )

    await request.handle()

    assert len(mock_task_service.deleted_tasks) == 1
    assert mock_task_service.deleted_tasks[0] == 4
