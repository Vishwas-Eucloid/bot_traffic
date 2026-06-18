import sys
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth.signup import perform_signup
from database import create_tables

TOTAL_ACCOUNTS = 10
MIN_DELAY_BETWEEN = 4.0   # seconds between each signup
MAX_DELAY_BETWEEN = 7.0   # seconds between each signup
COOLDOWN_EVERY = 5        # after every N signups, take a longer break
COOLDOWN_DURATION = 15.0  # seconds for the longer break


def run_batch_signup():
    print("==================================================")
    print(f"   BATCH SIGNUP TEST: {TOTAL_ACCOUNTS} Accounts")
    print("==================================================\n")

    create_tables()

    success_count = 0
    fail_count = 0
    created_emails = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)

        for i in range(1, TOTAL_ACCOUNTS + 1):
            print(f"--- [{i}/{TOTAL_ACCOUNTS}] Starting signup ---")
            context = browser.new_context(
                viewport={"width": 1365, "height": 900},
                locale="en-US",
            )
            page = context.new_page()
            page.is_mobile = False

            try:
                result = perform_signup(page)

                if result and isinstance(result, tuple):
                    email, password = result
                    success_count += 1
                    created_emails.append(email)
                    print(f"[OK] ({success_count} success) → {email}\n")
                else:
                    fail_count += 1
                    print(f"[FAIL] Signup #{i} did not complete.\n")

            except Exception as e:
                fail_count += 1
                print(f"[FAIL] Signup #{i} crashed: {e}\n")

            finally:
                context.close()

            # Cooldown every N signups
            if i % COOLDOWN_EVERY == 0 and i < TOTAL_ACCOUNTS:
                print(f"  [Cooldown] Completed {i} signups. Pausing {COOLDOWN_DURATION}s to avoid rate limits...\n")
                time.sleep(COOLDOWN_DURATION)
            elif i < TOTAL_ACCOUNTS:
                delay = random.uniform(MIN_DELAY_BETWEEN, MAX_DELAY_BETWEEN)
                print(f"  [Delay] Waiting {delay:.1f}s before next signup...")
                time.sleep(delay)

        browser.close()

    print("\n==================================================")
    print("   BATCH SIGNUP TEST COMPLETE")
    print("==================================================")
    print(f"  Successful : {success_count}")
    print(f"  Failed     : {fail_count}")
    print(f"  Total      : {TOTAL_ACCOUNTS}")
    print(f"\n  DB location: storage/bot_users.db")

    if created_emails:
        print(f"\n  Accounts created:")
        for email in created_emails:
            print(f"    - {email}")

    print("==================================================\n")


if __name__ == "__main__":
    run_batch_signup()
