from playwright.sync_api import sync_playwright, TimeoutError

import time
 
# --- 1. SET YOUR TARGET URL HERE ---

TARGET_URL = "https://new-poc.duckdns.org/"
 
# --- 2. PASTE YOUR SELECTORS TO TEST HERE ---

# Tweak these strings until they work perfectly!

CATEGORY_SELECTOR = "role=link[name='Tablets Tablets'i]"

ADD_TO_CART_TEXT = "button:has-text('Add to Cart'), button:has-text('ADD TO CART')"

BUY_NOW_TEXT = "button:has-text('Proceed to Checkout'), button:has-text('Buy Now')"
 
def run_test():

    with sync_playwright() as p:

        # headless=False opens a visible browser on your screen!

        browser = p.chromium.launch(headless=False, slow_mo=500)

        context = browser.new_context()

        page = context.new_page()
 
        print(f"🌍 Navigating to {TARGET_URL}...")

        page.goto(TARGET_URL)
 
        print("🔍 Looking for a product category link...")

        try:

            page.wait_for_selector(CATEGORY_SELECTOR, timeout=5000)

            page.locator(CATEGORY_SELECTOR).first.click()

        except TimeoutError:

            print("❌ FAILED: Could not find Category Link.")

            print("⏸️ Pausing browser. Use the Playwright Inspector to find the right selector!")

            page.pause() # Freezes execution here

            return
 
        print("🔍 Looking for 'Add to Cart' button...")

        try:

            # Wait up to 5 seconds for the button to appear

            btn = page.locator(ADD_TO_CART_TEXT).first

            btn.wait_for(state="visible", timeout=5000)

            btn.click()

            print("✅ SUCCESS: Clicked 'Add to Cart'")

        except TimeoutError:

            print(f"❌ FAILED: Could not find '{ADD_TO_CART_TEXT}'")

            print("⏸️ Pausing browser. Click the 'Explore' button in the Playwright Inspector!")

            page.pause()

            return
 
        print("🔍 Looking for 'Checkout' button...")

        try:

            buy_btn = page.locator(BUY_NOW_TEXT).first

            buy_btn.wait_for(state="visible", timeout=5000)

            buy_btn.click()

            print("✅ SUCCESS: Clicked 'Checkout'")

        except TimeoutError:

            print(f"❌ FAILED: Could not find '{BUY_NOW_TEXT}'")

            print("⏸️ Pausing browser. Find the correct text!")

            page.pause()

            return

        print("🎉 All selectors worked perfectly! You are ready to update the server.")

        time.sleep(3)

        browser.close()
 
if __name__ == "__main__":

    run_test()
 