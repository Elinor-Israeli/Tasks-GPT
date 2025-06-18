import pytest
from unittest.mock import AsyncMock, MagicMock
from app.requests.mark_done_user_request import MarkDoneUserRequest

@pytest.mark.asyncio
async def test_mark_done_by_id():
    mock_task_service = AsyncMock()
    mock_vector_searcher = MagicMock()
    mock_genai_client = MagicMock()

    mock_genai_client.extract_task_id_or_title.return_value = {
        "task_id": 101,
        "task_title": None
    }

    mock_task_service.get_task_by_id.return_value = {
        "id": 101,
        "title": "Finish report",
        "done": False
    }

    request = MarkDoneUserRequest.create(
        user_id=1,
        genai_client=mock_genai_client,
        user_input="mark task 101 as done",
        vector_searcher=mock_vector_searcher
    )

    await request.handle(mock_task_service)

    mock_task_service.update_task.assert_awaited_once_with(101, {"done": True})