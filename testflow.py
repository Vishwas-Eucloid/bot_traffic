import os
from playwright.sync_api import sync_playwright

from auth.signup import perform_signup
from auth.login import perform_login
from database import create_tables

CDP_URL = os.environ.get("CHROME_CDP", "http://127.0.0.1:9222")

def main():
    # Ensure the DB file and tables exist before we start
    create_tables()
    print("Initializing SQLite Database Test Sequence...")
    
    with sync_playwright() as p:
        try:
            print(f"Connecting to Chrome via CDP at {CDP_URL}...")
            browser = p.chromium.connect_over_cdp(CDP_URL)
            context = browser.contexts[0]
            
            # ==========================================
            # TEST 1: Perform Signup (Writes to DB)
            # ==========================================
            print("\n--- TEST 1: SIGNUP & DATABASE INJECTION ---")
            page1 = context.new_page()
            
            signup_result = perform_signup(page1)
            page1.close()
            
            if signup_result:
                new_email, _ = signup_result
                print(f"  -> [Success] Signup completed. {new_email} should now be in database.db")
            else:
                print("  -> [Fatal Error] Signup failed. Aborting test.")
                return

            # ==========================================
            # TEST 2: Perform Login (Reads from DB)
            # ==========================================
            print("\n--- TEST 2: DATABASE FETCH & RETURNING LOGIN ---")
            page2 = context.new_page()
            
            # 🚨 Calling this without arguments forces it to use get_random_user() from SQLite
            login_result = perform_login(page2)
            page2.close()
            
            if login_result:
                print("  -> [Success] Successfully fetched a user from database.db and logged in!")
            else:
                print("  -> [Error] Failed to log in returning user.")

        except Exception as e:
            print(f"\n[Fatal Error] Could not complete tests: {e}")
            print("Ensure Chrome is currently running with '--remote-debugging-port=9222'")
        finally:
            if 'browser' in locals():
                browser.close()
            print("\nSQLite Test Sequence Complete.")

if __name__ == "__main__":
    main()