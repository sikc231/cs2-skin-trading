import json
import os
import time
from playwright.sync_api import Playwright, sync_playwright, expect

class CsFloat:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.current_login_try = 1
        self.max_login_tries = 5
        self.steam_confirmation_timeout = 30000
        if os.path.exists("cookies.json"):
            with open("cookies.json", "r") as f:
                print("Loading cookies")
                cookies = json.loads(f.read())
                self.context.add_cookies(cookies)
        else:
            print("No cookies found, starting fresh")
        
    def start(self):
        
        self.sign_in()
        self.validate_login()
        self.cancel_popups()

        with open("cookies.json", "w") as f:
            print("Saving cookies")
            f.write(json.dumps(self.context.cookies()))

        print('loggedIn')

        self.validate_login()

        print("CsFloat started and ready.")

        time.sleep(1000000)  # Keep the browser open for your work here
    
    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


    def cancel_popups(self):
        print("Cancelling popups if any")
    
        self.page.evaluate('window.location.reload();')
        time.sleep(2)
    
        try: 
            noThanks = self.page.get_by_role("button", name="No Thanks")
            noThanks.wait_for(state="visible", timeout=5000)
            noThanks.click()
            print("Clicked 'No Thanks' button")
            time.sleep(1)
        except:
            print("XX - No 'No Thanks' button found")
            pass
        
        self.page.evaluate('window.location.reload();')
        time.sleep(2)
        
        try:
            remindMe = self.page.get_by_role("button", name="Remind me later")
            remindMe.wait_for(state="visible", timeout=5000)
            remindMe.click()
            print("Clicked 'Remind me later' button")
            time.sleep(1)
        except:
            print("XX - No 'Remind me later' button found")
            pass


    def validate_login(self) -> bool:
        self.page.evaluate('window.location.reload();')
        time.sleep(2)
        avatar = self.page.locator("img.avatar")
        try:
            avatar.wait_for(state="visible", timeout=5000)
            self.current_login_try = 1
            return True
        except:
            print("Not logged in, retrying...")
            self.sign_in()

    def sign_in(self) -> None:
        self.page.goto("https://csfloat.com/")
        signInBtn = self.page.get_by_role("button", name="Sign in")
        if signInBtn.is_visible():
            signInBtn.click()

        steamSignInBtn = self.page.locator("#imageLogin")
        try:
            steamSignInBtn.wait_for(state="visible", timeout=5000)
            if steamSignInBtn.is_visible():
                print("Steam session still valid")
                steamSignInBtn.click()
                return
        except: 
            print("Steam session not valid, proceeding with login")

        self.page.locator("form").filter(has_text="Sign in with account").locator("input[type=\"text\"]").click()
        self.page.locator("form").filter(has_text="Sign in with account").locator("input[type=\"text\"]").fill("braskinissudas")
        self.page.locator("input[type=\"password\"]").click()
        self.page.locator("input[type=\"password\"]").fill("123Tugaidys")
        self.page.get_by_role("button", name="Sign in").click()

        # Handle Steam Guard if prompted
        if self.current_login_try >= self.max_login_tries:
            print("Max login attempts reached. Exiting.")
            exit(1)

        self.current_login_try += 1
        user_confirmation_wait = self.current_login_try * self.steam_confirmation_timeout
        user_confirmation_done = self.page.get_by_role("button", name="Sign In")

        try:
            user_confirmation_done.wait_for(state="visible", timeout=user_confirmation_wait)
            print("Waiting for Steam Guard confirmation...")
            user_confirmation_done.click()
        except:
            print("No Steam Guard confirmation timeout reached.")
            print("Retrying login...")
            print("Current login attempt:", self.current_login_try)
            print("Waiting time for user confirmation (ms):", user_confirmation_wait)
            self.sign_in()

        self.validate_login()
