import pytest
from unittest.mock import AsyncMock, MagicMock
from app.src.commands.delete_task_user_request import DeleteTaskUserRequest

@pytest.mark.asyncio
async def test_delete_task_by_id():
    mock_task_service = AsyncMock()
    mock_vector_searcher = MagicMock()
    mock_genai_client = MagicMock()

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
        task_service=mock_task_service,
        vector_searcher=mock_vector_searcher
    )

    await request.handle(mock_task_service)

    mock_task_service.delete_task.assert_awaited_once_with(42)
    mock_vector_searcher.remove.assert_called_once_with(task_id=42, user_id=1)