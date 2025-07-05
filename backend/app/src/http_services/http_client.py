import httpx
import os
from typing import Optional, Dict, Any

class HttpClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        base_url = base_url or os.getenv("API_BASE_URL" , "http://localhost:8000")
        self.client: httpx.AsyncClient = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        return await self.client.get(url, params=params, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.client.post(url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self.client.put(url, **kwargs)

    async def delete(self, url: str) -> httpx.Response:
        return await self.client.delete(url)

    async def close(self) -> None:
        await self.client.aclose()
