import asyncio
from src.csfloat import CsFloat
from src.proxy import ProxyService
from src.db import Database
from dotenv import load_dotenv
load_dotenv()

async def run() -> None:
    print("Starting Program...")

    await Database.init()

    cs = CsFloat(10)
    await cs.initialize()
    await cs.start()

    await cs.fetch_deals()

    #ProxyService.initialize()
    #print("Total Proxies Loaded:", ProxyService.get_proxy_count())
    #oldest_proxy = ProxyService.get_oldest_used_proxy()
    #print("Oldest Used Proxy:", oldest_proxy)


if __name__ == "__main__":
    asyncio.run(run())


