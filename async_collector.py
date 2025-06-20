import asyncio
import aiohttp
import json
from typing import Dict, List

class AsyncCollector:
    def __init__(self, max_concurrent: int = 5, retries: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.retries = retries

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> dict:
        async with self.semaphore:
            for attempt in range(self.retries):
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", 3 ** attempt))
                            print(f"[429] {url} – retrying in {retry_after}s...")
                            await asyncio.sleep(retry_after)
                        else:
                            print(f"[{response.status}] {url}")
                            return {}
                except Exception as e:
                    print(f"[ERROR] {url}: {e}")
                    await asyncio.sleep(2 ** attempt)
            return {}

    async def collect(self, urls_per_file: Dict[str, List[str]]) -> Dict[str, List[dict]]:
            data_per_file: Dict[str, List[dict]] = {filename: [] for filename in urls_per_file}
            failed_requests = []

            async with aiohttp.ClientSession(headers={
                "User-Agent": "MyAsyncCollector/1.0",
                "Accept": "application/json"
            }) as session:
                tasks = []

                for filename, urls in urls_per_file.items():
                    for url in urls:
                        tasks.append(self._fetch_and_store(session, url, filename, data_per_file, failed_requests))

                await asyncio.gather(*tasks)

                # Retry failed URLs
                if failed_requests:
                    print(f"🔁 Retrying {len(failed_requests)} failed requests...")
                    retry_tasks = [
                        self._fetch_and_store(session, url, filename, data_per_file, [])
                        for filename, url in failed_requests
                    ]
                    await asyncio.gather(*retry_tasks)

            return data_per_file

    async def _fetch_and_store(self, session, url: str, filename: str, store: Dict[str, List[dict]], failed_requests: List):
        print(f"🔗 Fetching {url}")
        result = await self.fetch(session, url)

        # Determine if the request failed
        if not result:
            failed_requests.append((filename, url))
            return

        # Extract data correctly
        if "camara" in url and isinstance(result, dict) and "dados" in result:
            dados = result["dados"]
        else:
            dados = result

        # Store data correctly
        if isinstance(dados, list):
            store[filename].extend(dados)
        elif isinstance(dados, dict):
            store[filename].append(dados)
            
    def store_data(self, data: dict, filepath: str) -> None:
        json.dump(data, open(filepath, "w"))