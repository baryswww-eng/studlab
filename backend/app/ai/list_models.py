"""Print Gemini models available for the configured key (names only, never the key).

Usage (from backend/):  python -m app.ai.list_models
"""

import asyncio

import httpx

from app.ai.gemini import API_BASE
from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.ai_available or settings.gemini_api_key is None:
        print("GEMINI_API_KEY is not configured")
        return
    headers = {"x-goog-api-key": settings.gemini_api_key.get_secret_value()}
    names: list[str] = []
    async with httpx.AsyncClient(timeout=20) as client:
        page_token = ""
        while True:
            response = await client.get(
                f"{API_BASE}/models",
                params={"pageSize": 200, **({"pageToken": page_token} if page_token else {})},
                headers=headers,
            )
            if response.status_code != 200:
                print(f"HTTP {response.status_code}")
                return
            data = response.json()
            names += [
                m["name"].removeprefix("models/")
                for m in data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            page_token = data.get("nextPageToken", "")
            if not page_token:
                break
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    asyncio.run(main())
