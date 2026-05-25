import os

from pathlib import Path
 
# Import from your new Phase 1 modules

from config import BASE_URL, TOTAL_DAILY_USERS, JOURNEY_RANGES

from database import create_tables, save_user, get_random_user
 
def run_tests():

    print("==================================")

    print("   PHASE 1: SYSTEM DIAGNOSTICS")

    print("==================================\n")
 
    # 1. Test Config Loading

    print("--- 1. Testing Configuration ---")

    try:

        print(f"Targeting: {BASE_URL}")

        print(f"Total Daily Users: {TOTAL_DAILY_USERS}")

        print(f"Checkout Abandonment Range: {JOURNEY_RANGES['checkout_abandon']}")

        print("[OK] Config loaded successfully.\n")

    except Exception as e:

        print(f"[FAIL] Config error: {e}\n")
 
    # 2. Test Database Initialization

    print("--- 2. Testing Database Initialization ---")

    try:

        create_tables()

        db_path = Path("storage/bot_users.db")

        if db_path.exists():

            print(f"[OK] Database created at: {db_path.absolute()}\n")

        else:

            print("[FAIL] Database file not found!\n")

    except Exception as e:

        print(f"[FAIL] DB Init error: {e}\n")
 
    # 3. Test Database Writes

    print("--- 3. Testing Database Writes ---")

    try:

        save_user("loadtest1@singitronic.com", "Test@123")

        save_user("loadtest2@singitronic.com", "Test@123")

        # Test the UNIQUE constraint (this shouldn't crash due to INSERT OR IGNORE)

        save_user("loadtest1@singitronic.com", "Test@123") 

        print("[OK] Test users written to SQLite (duplicates safely ignored).\n")

    except Exception as e:

        print(f"[FAIL] DB Write error: {e}\n")
 
    # 4. Test Database Reads

    print("--- 4. Testing Database Reads ---")

    try:

        user = get_random_user()

        if user:

            print(f"[OK] Fetched Random User -> Email: {user[0]} | Password: {user[1]}")

        else:

            print("[FAIL] Query succeeded, but no user was returned.")

    except Exception as e:

        print(f"[FAIL] DB Read error: {e}\n")
 
if __name__ == "__main__":

    run_tests()
 