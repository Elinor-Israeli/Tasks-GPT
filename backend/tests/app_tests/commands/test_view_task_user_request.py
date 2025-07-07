import pytest
from unittest.mock import AsyncMock
from app.src.commands.view_tasks_user_request import ViewTasksUserRequest

class MockCommunicator:
    def __init__(self):
        self.outputs = []

    async def input(self, prompt: str = ""):
        return ""

    async def output(self, text: str):
        self.outputs.append(text)

@pytest.mark.asyncio
async def test_view_tasks_user_request_handle_shows_completed_tasks():
    user_id = 1
    choice = "1"  
    communicator = MockCommunicator()

    mock_task_service = AsyncMock()
    mock_task_service.get_tasks.return_value = [
        {"id": 2, "title": "Task 2", "done": True, "due_date": "2025-07-10"},
        {"id": 1, "title": "Task 1", "done": True, "due_date": None},
    ]

    request = ViewTasksUserRequest(
        user_id=user_id,
        choice=choice,
        communicator=communicator
    )

    await request.handle(mock_task_service)

    mock_task_service.get_tasks.assert_awaited_once_with(user_id=user_id, done=True)
    assert "--- TASKS ---" in communicator.outputs[0]
    assert "2. Task 2 (Due: 2025-07-10) - ✅" in communicator.outputs[1]
    assert "1. Task 1  - ✅" in communicator.outputs[2]
