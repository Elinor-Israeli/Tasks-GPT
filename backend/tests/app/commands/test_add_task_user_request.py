import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.src.commands.add_task_user_request import AddTaskUserRequest


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
async def test_add_task_user_request_handle():
    mock_task_service = AsyncMock()
    mock_task_service.create_task.return_value = {
        "id": 1,
        "title": "Buy milk",
        "due_date": "2025-06-20",
        "user_id": 123
    }

    mock_vector_store = MagicMock()
    
    mock_genai_client = MagicMock()
    mock_genai_client.extract_task_data.return_value = {
        "name": "Buy milk", "date": "2025-06-20"
    }
    
    communicator = MockCommunicator(inputs=[])

    request = await AddTaskUserRequest.create(
        user_id=123,
        genai_client=mock_genai_client,
        user_input="Buy milk next Thursday",
        communicator=communicator
    )

    await request.handle(
        mock_task_service,
        vector_adder=mock_vector_store,
        communicator=communicator
    )

    mock_task_service.create_task.assert_awaited_once_with({
        "title": "Buy milk",
        "due_date": "2025-06-20",
        "user_id": 123
    })
    mock_vector_store.add.assert_called_once_with(
        task_id=1,
        title="Buy milk",
        user_id=123
    )

    assert "[Output] Task 'Buy milk' added with due date 2025-06-20!" in communicator.outputs



