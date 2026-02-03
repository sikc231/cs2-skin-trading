from asyncio import sleep
from playwright.sync_api import Page
from playwright.sync_api import Playwright, sync_playwright, expect
import json

current_login_try = 1
max_login_tries = 5
steam_confirmation_timeout = 30000 

def validate_login(page: Page) -> bool:
    global current_login_try
    page.evaluate('window.location.reload();')
    sleep(2)
    avatar = page.locator("img.avatar")
    try:
        avatar.wait_for(state="visible", timeout=5000)
        current_login_try = 1
        return True
    except:
        print("Not logged in, retrying...")
        sign_in(page)

def sign_in(page: Page) -> None:
    global current_login_try, max_login_tries, user_confirmation_wait
    page.goto("https://csfloat.com/")
    signInBtn = page.get_by_role("button", name="Sign in")
    if signInBtn.is_visible():
        signInBtn.click()

    steamSignInBtn = page.locator("#imageLogin")
    try:
        steamSignInBtn.wait_for(state="visible", timeout=5000)
        if steamSignInBtn.is_visible():
            print("Steam session still valid")
            steamSignInBtn.click()
            return
    except: 
        print("Steam session not valid, proceeding with login")



    page.locator("form").filter(has_text="Sign in with account").locator("input[type=\"text\"]").click()
    page.locator("form").filter(has_text="Sign in with account").locator("input[type=\"text\"]").fill("braskinissudas")
    page.locator("input[type=\"password\"]").click()
    page.locator("input[type=\"password\"]").fill("123Tugaidys")
    page.get_by_role("button", name="Sign in").click()



    # Handle Steam Guard if prompted
    if current_login_try >= max_login_tries:
        print("Max login attempts reached. Exiting.")
        exit(1)

    current_login_try += 1
    user_confirmation_wait = current_login_try * steam_confirmation_timeout
    user_confirmation_done = page.get_by_role("button", name="Sign In")

    try:
        user_confirmation_done.wait_for(state="visible", timeout=user_confirmation_wait)
        print("Waiting for Steam Guard confirmation...")
        user_confirmation_done.click()
    except:
        print("No Steam Guard confirmation timeout reached.")
        print("Retrying login...")
        print("Current login attempt:", current_login_try)
        print("Waiting time for user confirmation (ms):", user_confirmation_wait)
        sign_in(page)

    validate_login(page)



