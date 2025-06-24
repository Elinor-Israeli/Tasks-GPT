import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.src.commands.view_tasks_user_request import ViewTasksUserRequest


class MockCommunicator:
    def __init__(self, inputs):
        self.inputs = inputs
        self.outputs = []
        self.index = 0

    async def input(self, text):
        self.outputs.append(f"[Prompted] {text}")
        val = self.inputs[self.index]
        self.index += 1
        return val

    async def output(self, text):
        self.outputs.append(f"[Output] {text}")

@pytest.mark.asyncio
async def test_view_tasks_user_request_completed(monkeypatch, capsys):
    mock_task_service = AsyncMock()
    mock_genai_client = MagicMock()
    communicator = MockCommunicator(inputs=[])

    mock_genai_client.interpret_view_task_command.return_value = "1"

    mock_task_service.get_tasks.return_value = [
        {"id": 2, "title": "Finish homework", "done": True, "due_date": "2025-07-01"},
        {"id": 1, "title": "Submit report", "done": True, "due_date": None}
    ]

    request = await ViewTasksUserRequest.create(
        user_id=1,
        genai_client=mock_genai_client,
        user_input="Show me completed tasks",
        communicator=communicator
    )

    assert request is not None
    assert request.choice == "1"

    await request.handle(mock_task_service)

    assert any("--- TASKS ---" in line for line in communicator.outputs)
    assert any("2. Finish homework (Due: 2025-07-01) - ✅" in line for line in communicator.outputs)
    assert any("1. Submit report  - ✅" in line for line in communicator.outputs)
    
    mock_task_service.get_tasks.assert_awaited_once_with(user_id=1, done=True)
