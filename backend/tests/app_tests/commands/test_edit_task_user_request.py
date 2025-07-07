import pytest
from unittest.mock import AsyncMock, MagicMock
from app.src.commands.edit_task_user_request import EditTaskUserRequest

class MockCommunicator:
    def __init__(self):
        self.outputs = []

    async def input(self, prompt):
        return ""

    async def output(self, text):
        self.outputs.append(text)

@pytest.mark.asyncio
async def test_edit_task_user_request_handle_updates_task_and_vector_store():
    mock_task_service = AsyncMock()
    mock_vector_store = MagicMock()
    communicator = MockCommunicator()

    extracted_data = {
        "title": "Updated Task Title",
        "due_date": "2025-07-30"
    }

    request = EditTaskUserRequest(
        user_id=1,
        task_id=101,
        extracted_data=extracted_data,
        communicator=communicator
    )

    await request.handle(
        task_service=mock_task_service,
        vector_store=mock_vector_store,
        communicator=communicator
    )

    mock_task_service.update_task.assert_awaited_once_with(101, {
        "title": "Updated Task Title",
        "due_date": "2025-07-30"
    })

    mock_vector_store.add.assert_called_once_with(
        task_id=101,
        title="Updated Task Title",
        user_id=1,
        due_date="2025-07-30"
    )

    assert any("updated" in msg.lower() for msg in communicator.outputs)
