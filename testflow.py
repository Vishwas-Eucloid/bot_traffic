import os
import time
from playwright.sync_api import sync_playwright
from auth.signup import perform_signup
from auth.login import perform_login
from database import create_tables

CDP_URL = os.environ.get("CHROME_CDP", "http://127.0.0.1:9222")
TARGET_USERS = 150
BATCH_SIZE = 10  # Processes 10 users, then restarts the browser connection

def process_batch(p, start_index, end_index):
    print(f"\n>>> Connecting to Chrome for Batch {start_index} to {end_index-1}...")
    browser = p.chromium.connect_over_cdp(CDP_URL)
    
    try:
        for i in range(start_index, end_index):
            print(f"\n==========================================")
            print(f"  RUNNING USER {i} OF {TARGET_USERS}")
            print(f"==========================================")
            
            signup_context = browser.new_context()
            signup_page = signup_context.new_page()
            
            try:
                # --- 1. SIGNUP FLOW ---
                print(f"--- [Phase 1] Signup ---")
                signup_result = perform_signup(signup_page)
                signup_context.close()
                
                if not signup_result:
                    print(f"  -> [Warning] Iteration {i} signup failed.")
                    continue
                    
                time.sleep(2)
                
                # --- 2. LOGIN FLOW ---
                login_context = browser.new_context()
                login_page = login_context.new_page()
                
                print(f"--- [Phase 2] Returning Login ---")
                login_result = perform_login(login_page)
                login_context.close()
                
                if not login_result:
                    print(f"  -> [Warning] Iteration {i} login failed.")
                    
            except Exception as e:
                print(f"  -> [Error] Crash on iteration {i}: {e}")
            finally:
                if 'signup_context' in locals():
                    try: signup_context.close()
                    except: pass
                if 'login_context' in locals():
                    try: login_context.close()
                    except: pass

            time.sleep(1) 
            
    finally:
        print(f">>> Closing Chrome connection to flush memory...")
        browser.close()

def main():
    create_tables()
    print(f"Initializing SQLite Mass Generation for {TARGET_USERS} users...")
    
    with sync_playwright() as p:
        for current_start in range(1, TARGET_USERS + 1, BATCH_SIZE):
            current_end = min(current_start + BATCH_SIZE, TARGET_USERS + 1)
            process_batch(p, current_start, current_end)
            
            if current_end <= TARGET_USERS:
                print(f"\n[Cooldown] Giving the server 5 seconds to clear database pool...")
                time.sleep(5)

    print("\nMass Generation Sequence Complete.")

if __name__ == "__main__":
    main()