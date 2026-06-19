import sys
import time
import sqlite3
from pathlib import Path
from playwright.sync_api import sync_playwright

from auth.signup import perform_signup
from database import create_tables, get_random_user
from config import BASE_URL

# --- CONFIGURATION ---
TARGET_USERS = 50000
# ---------------------

def view_db():
    print("\n--- 5. Viewing Database Contents (Last 50 rows) ---")
    db_path = Path("storage/bot_users.db")
    
    if not db_path.exists():
        print(f"[ERROR] Database not found at: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM bot_users")
    total_rows = cursor.fetchone()[0]
    
    # Get last 50 rows to prevent terminal crash
    cursor.execute("SELECT * FROM bot_users ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    # Reverse the rows so they print in chronological order
    rows.reverse()

    print(f"DB: {db_path}")
    print(f"Total rows in database: {total_rows}\n")
    print(f"{'ID':<5} {'Email':<40} {'Password':<12} {'Created At'}")
    print("-" * 85)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<40} {row[2]:<12} {row[3]}")
    print("\n")


def run_test():
    print("==================================")
    print(f"   MASS SIGNUP TEST ({TARGET_USERS} USERS)")
    print("==================================\n")

    # --- Check 1: DB Initialization ---
    print("--- 1. Initializing Database ---")
    try:
        create_tables()
        print("[OK] Database ready.\n")
    except Exception as e:
        print(f"[FAIL] Could not initialize database: {e}\n")
        sys.exit(1)

    successful_signups = 0

    with sync_playwright() as p:
        # NOTE: For 50,000 runs, consider setting headless=True and removing slow_mo!
        browser = p.chromium.launch(headless=False, slow_mo=300)
        
        for i in range(1, TARGET_USERS + 1):
            print(f"\n>>> Running User {i} of {TARGET_USERS} <<<")
            
            # Create a fresh context for each user to ensure clear cookies/cache
            context = browser.new_context(
                viewport={"width": 1365, "height": 900},
                locale="en-US",
            )
            page = context.new_page()
            page.is_mobile = False

            try:
                # --- Check 2: Signup form submits successfully ---
                result = perform_signup(page)

                if result and isinstance(result, tuple) and len(result) == 2:
                    signed_up_email, signed_up_password = result
                    print(f"[OK] perform_signup() returned credentials for: {signed_up_email}")
                else:
                    print(f"[FAIL] perform_signup() did not return valid credentials. Got: {result}")
                    context.close()
                    continue # Skip to the next user instead of exiting the whole script

                # --- Check 3: URL has left /register ---
                current_url = page.url
                if "register" not in current_url:
                    print(f"[OK] Successfully redirected away from /register. Current URL: {current_url}")
                else:
                    print(f"[FAIL] Still on registration page. URL: {current_url}")

                # --- Check 4: User persisted to SQLite ---
                # Fetch all users and check our email is in there
                conn = sqlite3.connect(Path("storage/bot_users.db"))
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM bot_users WHERE email = ?", (signed_up_email,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    print(f"[OK] User '{row[0]}' confirmed in database.")
                    successful_signups += 1
                else:
                    print(f"[FAIL] User '{signed_up_email}' was NOT found in the database.")

            except Exception as e:
                print(f"[ERROR] An unexpected error occurred during user {i}: {e}")
            
            finally:
                # Always close the context to free up memory before the next loop
                context.close()

        browser.close()

    # --- Check 5: View Database Contents ---
    view_db()

    print("==================================")
    print(f"   MASS SIGNUP COMPLETE")
    print(f"   Successfully signed up: {successful_signups}/{TARGET_USERS}")
    print("==================================")


if __name__ == "__main__":
    run_test()