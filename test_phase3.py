import time

from playwright.sync_api import sync_playwright
 
# Import your Phase 3 navigation module

from core import navigation
 
def run_tests():

    print("==================================")

    print("   PHASE 3: NAVIGATION UTILITIES")

    print("==================================\n")
 
    print("--- Starting Browser Engine ---")

    with sync_playwright() as p:

        # Launching with headless=False so you can watch the human_delays in real-time

        browser = p.chromium.launch(headless=False)

        context = browser.new_context()

        page = context.new_page()
 
        # 1. Test the Category exploration path

        print("\n--- Testing: Category Browse Flow ---")

        try:

            navigation.goto_homepage(page)

            navigation.click_random_category(page)

            navigation.view_random_product(page)

            print("[OK] Category -> Product flow successful.\n")

        except Exception as e:

            print(f"[FAIL] Category flow error: {e}\n")
 
        # 2. Test the Search and Checkout path

        print("--- Testing: Search & Checkout Flow ---")

        try:

            # Go back to the homepage to reset

            navigation.goto_homepage(page)

            navigation.execute_search(page)

            navigation.view_random_product(page)

            navigation.add_to_cart(page)

            navigation.proceed_to_checkout(page)

            print("[OK] Search -> Cart -> Checkout flow successful.\n")

        except Exception as e:

            print(f"[FAIL] Search flow error: {e}\n")
 
        print("--- Closing Browser Engine ---")

        browser.close()
 
if __name__ == "__main__":

    run_tests()
 