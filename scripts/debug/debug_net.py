import asyncio
import httpx
import sys

async def check():
    print("Testing connectivity...")
    targets = ["https://www.google.com", "https://1.1.1.1"]
    async with httpx.AsyncClient(timeout=5.0) as client:
        for url in targets:
            try:
                r = await client.head(url)
                print(f"{url}: {r.status_code}")
            except Exception as e:
                print(f"{url}: FAILED - {e}")

if __name__ == "__main__":
    try:
        asyncio.run(check())
    except Exception as e:
        print(f"Main Loop Error: {e}")
