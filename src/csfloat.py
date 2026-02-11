import json
import os
import asyncio
import aiohttp
from playwright.async_api import async_playwright, expect
from src.db import Database, Cs2Skin
import time
class CsFloat:
    def __init__(self, min_price: float):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_login_try = 1
        self.max_login_tries = 5
        self.min_price = min_price
        self.steam_confirmation_timeout = 30000
        self.balance = 0
        import time
        self.sent_offer_ids = {}  # id: timestamp
        self.offer_id_expiry_seconds = 24 * 60 * 60  # 24 hours

    def getBalance(self) -> float:
        return self.balance

    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        if os.path.exists("./data/cookies.json"):
            with open("./data/cookies.json", "r") as f:
                print("Loading cookies")
                cookies = json.loads(f.read())
                await self.context.add_cookies(cookies)
        else:
            print("No cookies found, starting fresh")
    def getBalance(self) -> float:
        return self.balance

        
    async def start(self):
        
        await self.sign_in()
        await self.validate_login()
        await self.cancel_popups()

        cookies = await self.context.cookies()
        with open("./data/cookies.json", "w") as f:
            print("Saving cookies")
            f.write(json.dumps(cookies))

        print('loggedIn')

        await self.validate_login()
        await self.updateBalance()

        print("CsFloat started and ready.")
  # Keep the browser open for your work here
    
    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


    async def cancel_popups(self):
        print("Cancelling popups if any")
    
        await self.page.evaluate('window.location.reload();')
        await asyncio.sleep(2)
    
        try: 
            noThanks = self.page.get_by_role("button", name="No Thanks")
            await noThanks.wait_for(state="visible", timeout=5000)
            await noThanks.click()
            print("Clicked 'No Thanks' button")
            await asyncio.sleep(1)
        except:
            print("XX - No 'No Thanks' button found")
            pass
        
        await self.page.evaluate('window.location.reload();')
        await asyncio.sleep(2)
        
        try:
            remindMe = self.page.get_by_role("button", name="Remind me later")
            await remindMe.wait_for(state="visible", timeout=5000)
            await remindMe.click()
            print("Clicked 'Remind me later' button")
            await asyncio.sleep(1)
        except:
            print("XX - No 'Remind me later' button found")
            pass


    async def validate_login(self) -> bool:
        await self.page.evaluate('window.location.reload();')
        await asyncio.sleep(2)
        avatar = self.page.locator("img.avatar")
        try:
            await avatar.wait_for(state="visible", timeout=5000)
            self.current_login_try = 1
            return True
        except:
            print("Not logged in, retrying...")
            await self.sign_in()

    async def sign_in(self) -> None:
        await self.page.goto("https://csfloat.com/")
        signInBtn = self.page.get_by_role("button", name="Sign in")
        if await signInBtn.is_visible():
            await signInBtn.click()

        steamSignInBtn = self.page.locator("#imageLogin")
        try:
            await steamSignInBtn.wait_for(state="visible", timeout=5000)
            if await steamSignInBtn.is_visible():
                print("Steam session still valid")
                await steamSignInBtn.click()
                return
        except: 
            print("Steam session not valid, proceeding with login")

        await self.page.locator("form").filter(has_text="Sign in with account").locator("input[type=\"text\"]").click()
        await self.page.locator("form").filter(has_text="Sign in with account").locator("input[type=\"text\"]").fill("braskinissudas")
        await self.page.locator("input[type=\"password\"]").click()
        await self.page.locator("input[type=\"password\"]").fill("123Tugaidys")
        await self.page.get_by_role("button", name="Sign in").click()

        # Handle Steam Guard if prompted
        if self.current_login_try >= self.max_login_tries:
            print("Max login attempts reached. Exiting.")
            exit(1)

        self.current_login_try += 1
        user_confirmation_wait = self.current_login_try * self.steam_confirmation_timeout
        user_confirmation_done = self.page.get_by_role("button", name="Sign In")

        try:
            await user_confirmation_done.wait_for(state="visible", timeout=user_confirmation_wait)
            print("Waiting for Steam Guard confirmation...")
            await user_confirmation_done.click()
        except:
            print("No Steam Guard confirmation timeout reached.")
            print("Retrying login...")
            print("Current login attempt:", self.current_login_try)
            print("Waiting time for user confirmation (ms):", user_confirmation_wait)
            await self.sign_in()

        await self.validate_login()



    async def updateBalance(self) -> float:
        await self.validate_login()
        
        try:
            response = await self.page.request.fetch('https://csfloat.com/api/v1/me', method="GET")
            data = await response.json()
            csfloat_balance: float = data["user"]["balance"] / 100
            self.balance = data["user"]["balance"] 
            return csfloat_balance
        except Exception as e:
            print("Error fetching balance:", e)
        return 0.0
    


    async def fetch_deals(self):
        print("Fetching Deals...")
        print("Current Balance for fetching deals:", str(self.balance))
        NewOffersQeuryLink = "https://csfloat.com/api/v1/listings?limit=50&sort_by=most_recent&min_price=" + str(self.min_price) + "&max_price=" + str(self.balance) + "&type=buy_now"
        BestOffersQueryLink = "https://csfloat.com/api/v1/listings?limit=50&sort_by=best_deal&min_price=" + str(self.min_price) + "&max_price=" + str(self.balance) + "&type=buy_now"

        try:
            new_offers_response = await self.page.request.get(NewOffersQeuryLink)
            new_offers_data = await new_offers_response.json()
            best_offers_response = await self.page.request.get(BestOffersQueryLink)
            best_offers_data = await best_offers_response.json()

            # Remove expired IDs from sent_offer_ids
            now = time.time()
            expired_ids = [oid for oid, ts in self.sent_offer_ids.items() if now - ts > self.offer_id_expiry_seconds]
            for oid in expired_ids:
                del self.sent_offer_ids[oid]

            # Mesh arrays and deduplicate by 'id'
            all_offers = new_offers_data["data"] + best_offers_data["data"]
            unique_offers = {}
            for offer in all_offers:
                offer_id = offer.get("id")
                if offer_id not in unique_offers:
                    unique_offers[offer_id] = offer

            for offer in unique_offers.values():
                id          = offer["id"]
                # Skip if already sent (and not expired)
                if id in self.sent_offer_ids:
                    continue
                price       = offer["price"]
                wear_name   = ""
                item_name   = ""
                type_name   = ""
                float       = 0.0
                try:
                    wear_name   = offer["item"]["wear_name"]
                    item_name   = offer["item"]["item_name"]
                    type_name   = offer["item"]["type_name"]
                    float       =  offer["item"]["float_value"]
                except:
                    None

                full_name   = item_name
                if wear_name:
                    full_name = full_name + " (" + wear_name + ")"
                market_hash = offer["item"]["market_hash_name"]

                dbItem = await Database.get_skin_by_market_hash(market_hash)
                if not dbItem:
                    continue

                dbItemPrice = dbItem.price
                if not dbItemPrice and dbItemPrice < 0.1:
                    continue

                dbItemPrice = dbItemPrice * 100
                priceDiff = dbItemPrice - price
                priceDiffPercent = (priceDiff / dbItemPrice) * 100

                if priceDiffPercent > 65:
                    # Send notification to Discord webhook
                    webhook_url = "https://discord.com/api/webhooks/1470903534105919521/Vyo-gyR8Gr9DNT1E7jWZpq8Cg3EqbTld8IHbVPFs_K8JvY2eCuE0ZG8RSig-x-DXuBgn"
                    content = (
                        f"**New Offer Alert!**\n"
                        f"Market Hash: {market_hash}\n"
                        f"Price: {price}\n"
                        f"DB Price: {dbItemPrice}\n"
                        f"Diff: {priceDiff}\n"
                        f"Diff%: {priceDiffPercent:.2f}%\n"
                        f"Item: {full_name}\n"
                        f"Float: {float}\n"
                        f"Offer Link: https://csfloat.com/item/{id}"
                    )
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            await session.post(webhook_url, json={"content": content})
                        # Add to cache after sending, with timestamp
                        self.sent_offer_ids[id] = time.time()
                    except Exception as e:
                        print(f"Failed to send Discord webhook: {e}")
                #print(f"Offer: {market_hash} | Price: {price} | DB Price: {dbItemPrice} | Diff: {priceDiff} | Diff%: {priceDiffPercent:.2f}%")



                

                #print("id: ", id)
                #print("price: ", price)
                #print("wear_name: ", wear_name)
                #print("item_name: ", item_name)
                #print("type_name: ", type_name)
                #print("full_name: ", full_name)
                #print("market_hash: ", market_hash)
                #print("float: ", float)
                #print('-----------------------------')
                 
        except Exception as e:
            print(f"Error fetching deals: {e}")

        print(NewOffersQeuryLink)
        print(BestOffersQueryLink)
