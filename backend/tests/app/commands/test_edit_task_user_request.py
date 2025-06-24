import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.src.commands.edit_task_user_request import EditTaskUserRequest

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
async def test_edit_task_user_request_handle():
    mock_task_service = AsyncMock()
    mock_vector_store = AsyncMock()
    communicator = MockCommunicator(inputs=[])

    extracted_data = {
        "title": "Buy bread",
        "due_date": "2025-07-10"
    }

    request = EditTaskUserRequest(
        user_id=1,
        task_id=42,
        extracted_data=extracted_data,
        communicator=communicator
    )

    await request.handle(
        task_service=mock_task_service,
        vector_store=mock_vector_store
    )

    mock_task_service.update_task.assert_awaited_once_with(42, {
        "title": "Buy bread",
        "due_date": "2025-07-10"
    })

    mock_vector_store.add.assert_awaited_once_with(
        task_id=42,
        title="Buy bread",
        user_id=1
    )

    assert any("Task updated" in out for out in communicator.outputs)