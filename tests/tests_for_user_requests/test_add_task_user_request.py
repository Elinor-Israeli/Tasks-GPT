import pytest
from unittest.mock import AsyncMock, MagicMock
from client.genai import AICommandInterpreter
from backend.request.add_task_user_request import AddTaskUserRequest

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
    mock_genai_client.extract_task_data.side_effect = [
        {"name": "Buy milk", "date": "2025-06-20"}
    ]

    request = AddTaskUserRequest.create(
        user_id=123,
        genai_client=mock_genai_client,
        user_input="Buy milk next Thursday",
        vector_store=mock_vector_store
    )

    await request.handle(mock_task_service)

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

