import sys
import time
from playwright.sync_api import sync_playwright

from auth.signup import perform_signup
from database import create_tables, get_random_user
from config import BASE_URL


def run_test():
    print("==================================")
    print("   SIGNUP TEST")
    print("==================================\n")

    # --- Check 1: DB Initialization ---
    print("--- 1. Initializing Database ---")
    try:
        create_tables()
        print("[OK] Database ready.\n")
    except Exception as e:
        print(f"[FAIL] Could not initialize database: {e}\n")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(
            viewport={"width": 1365, "height": 900},
            locale="en-US",
        )
        page = context.new_page()
        page.is_mobile = False

        # --- Check 2: Signup form submits successfully ---
        print("--- 2. Running Signup Flow ---")
        result = perform_signup(page)

        if result and isinstance(result, tuple) and len(result) == 2:
            signed_up_email, signed_up_password = result
            print(f"[OK] perform_signup() returned credentials for: {signed_up_email}\n")
        else:
            print(f"[FAIL] perform_signup() did not return valid credentials. Got: {result}\n")
            browser.close()
            sys.exit(1)

        # --- Check 3: URL has left /register ---
        print("--- 3. Verifying URL Redirect ---")
        current_url = page.url
        if "register" not in current_url:
            print(f"[OK] Successfully redirected away from /register. Current URL: {current_url}\n")
        else:
            print(f"[FAIL] Still on registration page. URL: {current_url}\n")

        time.sleep(1)
        browser.close()

    # --- Check 4: User persisted to SQLite ---
    print("--- 4. Verifying Database Persistence ---")
    try:
        # Fetch all users and check our email is in there
        import sqlite3
        from pathlib import Path
        conn = sqlite3.connect(Path("storage/bot_users.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM bot_users WHERE email = ?", (signed_up_email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            print(f"[OK] User '{row[0]}' confirmed in database.\n")
        else:
            print(f"[FAIL] User '{signed_up_email}' was NOT found in the database.\n")
    except Exception as e:
        print(f"[FAIL] Database verification error: {e}\n")

    print("==================================")
    print("   SIGNUP TEST COMPLETE")
    print("==================================")


if __name__ == "__main__":
    run_test()
