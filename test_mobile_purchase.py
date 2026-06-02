import os
import sys
import random
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
 
# Ensure core packages can be imported if running directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
 
from config import BASE_URL, NAVIGATION_TIMEOUT
from core.navigation import (
    goto_homepage,
    click_random_category,
    view_random_product,
    add_to_cart,
    proceed_to_checkout,
    fill_checkout_form,
    place_order
)
 
def run_mobile_test_manually():
    """Executes a single, isolated mobile web transaction flow for verification."""
    cdp_url = os.environ.get("CHROME_CDP", "http://127.0.0.1:9222")
   
    print("==================================================")
    print("   SINGITRONIC MANUAL MOBILE PURCHASE TESTER")
    print("==================================================")
    print(f"Connecting via CDP to: {cdp_url}\n")
 
    with sync_playwright() as p:
        try:
            # Connect to your headless browser service
            browser = p.chromium.connect_over_cdp(cdp_url)
           
            # Fetch the device profile for iPhone 13 (handles viewport, user-agent, touch emulation)
            iphone_profile = p.devices['iPhone 13']
            print(f"[Mobile Device Profile Configured]: {iphone_profile['user_agent']}\n")
           
            # Instantiate an isolated context matching an iPhone device signature
            context = browser.new_context(**iphone_profile)
            page = context.new_page()
           
            # Explicitly flag this page instance as a mobile browser session
            page.is_mobile = True
 
            # -------------------------------------------------------------
            # --- START STEP-BY-STEP FUNNEL EXECUTION ---
            # -------------------------------------------------------------
           
            # Step 1: Open Home Page
            goto_homepage(page)
            time.sleep(1.5)
           
            # Step 2: Open Hamburger Menu & Select Category
            click_random_category(page)
            time.sleep(1.5)
           
            # Step 3: Browse to a Product Page (PDP)
            view_random_product(page)
            time.sleep(1.5)
           
            # Step 4: Add to Basket / Cart
            add_to_cart(page)
            time.sleep(1.5)
           
            # Step 5: Advance to Checkout Stage
            proceed_to_checkout(page)
            time.sleep(1.5)
           
            # Step 6: Populate Form Input Elements
            fill_checkout_form(page)
            time.sleep(1.5)
           
            # Step 7: Place Order & Confirm Successful Redirect
            place_order(page)
           
            print("\n==================================================")
            print("   ✅ SUCCESS: Mobile end-to-end checkout verified.")
            print("==================================================")
 
        except PlaywrightTimeoutError as te:
            print(f"\n❌ TIMEOUT FAILURE: Action exceeded expected timeline limit.\nDetails: {te}")
        except Exception as e:
            print(f"\n❌ UNEXPECTED CRITICAL EXCEPTION ENCOUNTERED:\nDetails: {e}")
        finally:
            if 'context' in locals():
                context.close()
            if 'browser' in locals():
                browser.close()
            print("[Test Finished] Disconnected cleanly.")
 
if __name__ == "__main__":
    run_mobile_test_manually()
 