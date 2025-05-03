import httpx
from .http_client import HttpClient
from typing import Optional


class TaskHttpService:
    def __init__(self, client: HttpClient):
        self.client = client

    async def get_tasks(self, user_id: int, done: Optional[bool] = None, due_date: Optional[str] = None):
        params = {}
        if user_id is not None:
            params["user_id"] = user_id
        if done is not None:
            params["done"] = done
        if due_date:
            params["due_date"] = due_date

        response = await self.client.get(f"/tasks/", params=params)
        response.raise_for_status()
        return response.json()

    async def get_task_by_id(self, task_id: int):
        response = await self.client.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()

    async def create_task(self, task_data: dict):
        response = await self.client.post("/tasks/", json=task_data)
        # response.raise_for_status()
        return response.json()

    async def update_task(self, task_id: int, task_data: dict):
        response = await self.client.put(f"/tasks/{task_id}", json=task_data)
        response.raise_for_status()
        return response.json()

    async def delete_task(self, task_id: int):
        response = await self.client.delete(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.status_code == 204

    async def close(self):
        await self.client.aclose()

