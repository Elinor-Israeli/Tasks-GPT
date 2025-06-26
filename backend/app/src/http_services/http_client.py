import httpx
import os

class HttpClient:
    def __init__(self, base_url: str = None):
        base_url = base_url or os.getenv("API_BASE_URL" , "http://localhost:8000")
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def get(self, url: str, params: dict = None, **kwargs):
        return await self.client.get(url, params=params, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.client.post(url, **kwargs)

    async def put(self, url: str, **kwargs):
        return await self.client.put(url, **kwargs)

    async def delete(self, url: str):
        return await self.client.delete(url)

    async def close(self):
        await self.client.aclose()
