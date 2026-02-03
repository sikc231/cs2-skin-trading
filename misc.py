from playwright.sync_api import Page
from time import sleep

#def change_currency_to_usd(page: Page):
#    page.query_selector('#mat-select-value-1').query_selector('div').click()
#    page.get_by_role("option", name="USD ($)").click()
#    return


def cancel_popups(page: Page):
    print("Cancelling popups if any")

    page.evaluate('window.location.reload();')
    sleep(2)

    try: 
        noThanks = page.get_by_role("button", name="No Thanks")
        noThanks.wait_for(state="visible", timeout=5000)
        noThanks.click()
        print("Clicked 'No Thanks' button")
        sleep(1)
    except:
        print("XX - No 'No Thanks' button found")
        pass

    page.evaluate('window.location.reload();')
    sleep(2)
    
    try:
        remindMe = page.get_by_role("button", name="Remind me later")
        remindMe.wait_for(state="visible", timeout=5000)
        remindMe.click()
        print("Clicked 'Remind me later' button")
        sleep(1)
    except:
        print("XX - No 'Remind me later' button found")
        pass
#def get_cash_balance(page: Page) -> float:

