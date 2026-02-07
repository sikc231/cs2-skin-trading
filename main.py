import asyncio
from src.csfloat import CsFloat
from src.proxy import ProxyService
from dotenv import load_dotenv
from src.csfloatItems import csfloatItems
load_dotenv()

async def run() -> None:
    print("Starting Program...")

    #cs = CsFloat()
    #await cs.initialize()
    #await cs.start()
    #print("Current Balance:", await cs.updateBalance())
    #print("Balance via getBalance():", cs.getBalance())

    ProxyService.initialize()
    print("Total Proxies Loaded:", ProxyService.get_proxy_count())
    oldest_proxy = ProxyService.get_oldest_used_proxy()
    print("Oldest Used Proxy:", oldest_proxy)


    csfloatScrape = csfloatItems(100, 10)
    csfloatScrape.fetch_deals()


if __name__ == "__main__":
    asyncio.run(run())


