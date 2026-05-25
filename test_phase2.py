import os

from playwright.sync_api import sync_playwright
 
# Import your Phase 2 modules

from auth.user_generator import generate_user

from auth.signup import perform_signup

from auth.login import perform_login
 
def run_tests():

    print("==================================")

    print("   PHASE 2: AUTHENTICATION SYSTEM")

    print("==================================\n")
 
    # 1. Test Fake User Generation (No Browser Needed)

    print("--- 1. Testing User Generator ---")

    try:

        dummy_user = generate_user()

        print(f"[OK] Generated User:")

        print(f"     Name: {dummy_user['firstname']} {dummy_user['lastname']}")

        print(f"     Email: {dummy_user['email']}")

        print(f"     Address: {dummy_user['addressline']}, {dummy_user['city']}\n")

    except Exception as e:

        print(f"[FAIL] User Generator error: {e}\n")

        return # Stop testing if generation fails
 
    # Start Playwright for the Web Tests

    print("--- Starting Browser Engine ---")

    with sync_playwright() as p:

        # Launching with headless=False so you can watch it happen!

        browser = p.chromium.launch(headless=False)

        context = browser.new_context()

        page = context.new_page()
 
        # 2. Test the Signup Flow

        print("\n--- 2. Testing Automated Signup ---")

        try:

            print("Navigating and filling signup form...")

            signup_success = perform_signup(page)

            if signup_success:

                print("[OK] Signup completed and user saved to SQLite.\n")

            else:

                print("[FAIL] Signup function returned False.\n")

        except Exception as e:

            print(f"[FAIL] Automated Signup error: {e}\n")
 
        # Clear the cookies/session so we are fully logged out before testing login

        context.clear_cookies()
 
        # 3. Test the Login Flow

        print("--- 3. Testing Automated Login ---")

        try:

            print("Fetching user from SQLite and attempting login...")

            login_success = perform_login(page)

            if login_success:

                print("[OK] Login completed successfully.\n")

            else:

                print("[FAIL] Login function returned False.\n")

        except Exception as e:

            print(f"[FAIL] Automated Login error: {e}\n")
 
        print("--- Closing Browser Engine ---")

        browser.close()
 
if __name__ == "__main__":

    run_tests()
 