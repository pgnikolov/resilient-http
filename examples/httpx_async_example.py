import asyncio
from resilient_http.httpx_async import ResilientAsyncClient

async def main():
    client = ResilientAsyncClient()

    print("Trying retry against 503 endpoint...")

    resp = await client.get("https://httpbin.org/status/503")
    print("Status:", resp.status_code)

asyncio.run(main())
