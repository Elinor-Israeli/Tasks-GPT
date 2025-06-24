import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.src.commands.delete_task_user_request import DeleteTaskUserRequest

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
async def test_delete_task_by_id():
    mock_task_service = AsyncMock()
    mock_vector_searcher = MagicMock()
    mock_genai_client = MagicMock()
    communicator = MockCommunicator(inputs=[])

    mock_genai_client.extract_task_id_or_title.return_value = {
        "task_id": 42,
        "task_title": None
    }

    mock_task_service.get_task_by_id.return_value = {
        "id": 42,
        "title": "Take out trash",
        "user_id": 1
    }

    request = await DeleteTaskUserRequest.create(
        user_id=1,
        genai_client=mock_genai_client,
        user_input="delete task 42",
        vector_searcher=mock_vector_searcher,
        communicator=communicator
    )

    await request.handle(
        task_service=mock_task_service,
        vector_remover=mock_vector_searcher,
    )

    mock_task_service.delete_task.assert_awaited_once_with(42)
    mock_vector_searcher.remove.assert_called_once_with(task_id=42, user_id=1)
    assert any("deleted" in line.lower() for line in communicator.outputs)