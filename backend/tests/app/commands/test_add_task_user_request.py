import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from backend.app.src.commands.add_task_user_request import AddTaskUserRequest


class MockGenAI:
    def __init__(self, title="Test Task", date="2025-12-31"):
        self.title = title
        self.date = date

    def extract_task_data(self, user_input):
        return {"name": self.title, "date": self.date}


class MockCommunicator:
    def __init__(self):
        self.inputs = []
        self.outputs = []

    async def input(self, prompt):
        self.inputs.append(prompt)
        return "Test Task due next month"

    async def output(self, message):
        self.outputs.append(message)


class MockTaskService:
    async def create_task(self, task_data):
        return {
            "id": 123,
            "title": task_data["title"],
            "due_date": task_data["due_date"],
            "user_id": task_data["user_id"]
        }


class MockVectorAdder:
    def add(self, task_id, title, user_id):
        assert isinstance(task_id, int)
        assert isinstance(title, str)
        assert isinstance(user_id, int)


@pytest.mark.asyncio
async def test_add_task_user_request_create_and_handle():
    user_id = 1
    user_input = "Buy milk tomorrow"
    communicator = MockCommunicator()
    genai_client = MockGenAI()
    task_service = MockTaskService()
    vector_adder = MockVectorAdder()

    request = await AddTaskUserRequest.create(
        user_id=user_id,
        genai_client=genai_client,
        user_input=user_input,
        communicator=communicator
    )

    assert request is not None
    assert request.title == "Test Task"
    assert request.due_date == "2025-12-31"

    await request.handle(task_service, vector_adder, communicator)

    assert communicator.outputs[0] == "Task 'Test Task' added with due date 2025-12-31!"

