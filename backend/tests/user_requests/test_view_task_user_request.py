import pytest
from unittest.mock import AsyncMock, MagicMock
from app.requests.view_tasks_user_request import ViewTasksUserRequest

@pytest.mark.asyncio
async def test_view_tasks_user_request_completed(monkeypatch, capsys):
    mock_task_service = AsyncMock()
    mock_genai_client = MagicMock()

    mock_genai_client.interpret_view_task_command.return_value = "1"

    mock_task_service.get_tasks.return_value = [
        {"id": 2, "title": "Finish homework", "done": True, "due_date": "2025-07-01"},
        {"id": 1, "title": "Submit report", "done": True, "due_date": None}
    ]

    request = ViewTasksUserRequest.create(
        user_id=1,
        genai_client=mock_genai_client,
        user_input="Show me completed tasks"
    )

    assert request is not None
    assert request.choice == "1"

    await request.handle(mock_task_service)

    captured = capsys.readouterr()
    assert "--- TASKS ---" in captured.out
    assert "2. Finish homework (Due: 2025-07-01) - ✅" in captured.out
    assert "1. Submit report  - ✅" in captured.out

    mock_task_service.get_tasks.assert_awaited_once_with(user_id=1, done=True)
