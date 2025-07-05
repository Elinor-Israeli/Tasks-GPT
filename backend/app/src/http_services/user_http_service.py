from typing import Optional, Dict, Any
from .http_client import HttpClient

class UserHttpService:
    def __init__(self, client: Optional[HttpClient] = None) -> None:
        self.client: HttpClient = client or HttpClient()

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        response = await self.client.get(f"/users/by-username/{username}")
        if response.status_code == 200:
            return response.json()
        return None

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        response = await self.client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.post("/users/", json=user_data)
        response.raise_for_status()
        return response.json()

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.put(f"/users/{user_id}", json=user_data)
        response.raise_for_status()
        return response.json()

    async def delete_user(self, user_id: int) -> bool:
        response = await self.client.delete(f"/users/{user_id}")
        response.raise_for_status()
        return response.status_code == 204

    async def close(self) -> None:
        await self.client.aclose()