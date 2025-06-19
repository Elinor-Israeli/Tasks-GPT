import pytest
from unittest.mock import AsyncMock, MagicMock
from app.src.commands.edit_task_user_request import EditTaskUserRequest

@pytest.mark.asyncio
async def test_edit_task_user_request_handle(monkeypatch):
    mock_task_service = AsyncMock()
    mock_vector_searcher = MagicMock()
    mock_genai_client = MagicMock()

    mock_genai_client.extract_task_id_or_title_to_edit.return_value = {
        "task_id": 42,
        "task_title": None
    }

    mock_task_service.get_task_by_id.return_value = {
        "id": 42,
        "title": "Buy groceries",
        "user_id": 1
    }

    monkeypatch.setattr("builtins.input", lambda _: "Change title to Buy bread and due date to 2025-07-10")

    mock_genai_client.extract_edit_task_data.return_value = {
        "title": "Buy bread",
        "due_date": "2025-07-10"
    }

    request = await EditTaskUserRequest.create(
        user_id=1,
        task_service=mock_task_service,
        genai_client=mock_genai_client,
        user_input="edit task 42",
        vector_searcher=mock_vector_searcher
    )

    await request.handle(mock_task_service)

    mock_task_service.update_task.assert_awaited_once_with(
        42,
        {"title": "Buy bread", "due_date": "2025-07-10"}
    )