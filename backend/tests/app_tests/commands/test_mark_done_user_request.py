import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.src.commands.mark_done_user_request import MarkDoneUserRequest

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
async def test_mark_done_by_id():
    mock_task_service = AsyncMock()
    mock_vector_searcher = MagicMock()
    mock_genai_client = MagicMock()
    communicator = MockCommunicator(inputs=[])

    mock_genai_client.extract_task_id_or_title.return_value = {
        "task_id": 101,
        "task_title": None
    }

    mock_task_service.get_task_by_id.return_value = {
        "id": 101,
        "title": "Finish report",
        "done": False
    }

    request = await MarkDoneUserRequest.create(
        user_id=1,
        genai_client=mock_genai_client,
        user_input="mark task 101 as done",
        vector_searcher=mock_vector_searcher,
        communicator=communicator
    )

    await request.handle(mock_task_service)

    mock_task_service.update_task.assert_awaited_once_with(101, {"done": True})