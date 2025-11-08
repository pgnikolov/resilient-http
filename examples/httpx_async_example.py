import asyncio
from resilient_http.resilient_async_client import ResilientAsyncClient


async def main():
    async with ResilientAsyncClient() as client:
        print("Trying retry against 503 endpoint...")
        resp = await client.get("https://httpbin.org/status/503")
        print("Status:", resp.status_code)


asyncio.run(main())
