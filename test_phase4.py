import os
import time
from playwright.sync_api import sync_playwright

from journeys import search_discovery
from journeys import checkout_abandon
from journeys import returning_logged_in

from auth.login import perform_login


def attach_debug_listeners(page):

    page.on(
        "request",
        lambda request: print(f"REQUEST: {request.method} {request.url}")
    )

    page.on(
        "response",
        lambda response: print(f"RESPONSE: {response.status} {response.url}")
    )


def run_tests():

    print("==================================")
    print("   PHASE 4: JOURNEY SCRIPTS")
    print("==================================\n")

    cdp_url = os.environ.get("CHROME_CDP") or "http://127.0.0.1:9222"

    with sync_playwright() as p:

        print("--- Connecting to Real Chrome via CDP ---")

        browser = p.chromium.connect_over_cdp(cdp_url)

        # ---------------------------------------------------------
        # TEST 1
        # ---------------------------------------------------------

        print("\n--- Testing: Guest Journey (Search Discovery) ---")

        context1 = browser.new_context()
        page1 = context1.new_page()

        attach_debug_listeners(page1)

        try:

            search_discovery.run_journey(page1)

            print("[OK] Search Discovery completed.\n")

        except Exception as e:

            print(f"[FAIL] Search Discovery error: {e}\n")

        finally:

            context1.close()

        # ---------------------------------------------------------
        # TEST 2
        # ---------------------------------------------------------

        print("--- Testing: Guest Journey (Checkout Abandonment) ---")

        context2 = browser.new_context()
        page2 = context2.new_page()

        attach_debug_listeners(page2)

        try:

            checkout_abandon.run_journey(page2)

            print("[OK] Checkout Abandonment completed.\n")

        except Exception as e:

            print(f"[FAIL] Checkout Abandonment error: {e}\n")

        finally:

            context2.close()

        # ---------------------------------------------------------
        # TEST 3
        # ---------------------------------------------------------

        print("--- Testing: Logged-In Journey ---")

        context3 = browser.new_context()
        page3 = context3.new_page()

        attach_debug_listeners(page3)

        try:

            print("  -> Authenticating user first...")

            login_success = perform_login(page3)

            print("Current URL:", page3.url)

            cookies = context3.cookies()

            print("\n===== COOKIES AFTER LOGIN =====")
            for cookie in cookies:
                print(cookie)

            if login_success:

                if page3.locator("text=Incorrect email or password").count() > 0:

                    print("[FAIL] Backend rejected credentials.")

                else:

                    returning_logged_in.run_journey(page3)

                    print("[OK] Returning Logged-In journey completed.\n")

            else:

                print("[FAIL] Could not log in.\n")

        except Exception as e:

            print(f"[FAIL] Logged-In journey error: {e}\n")

        finally:

            context3.close()

        print("--- Closing Browser ---")

        browser.close()


if __name__ == "__main__":

    run_tests()