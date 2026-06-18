import sys
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth.signup import perform_signup
from database import create_tables

TOTAL_ACCOUNTS = 10
MIN_DELAY_BETWEEN = 45.0   # seconds between each signup
MAX_DELAY_BETWEEN = 75.0   # seconds between each signup
COOLDOWN_EVERY = 3         # take a long break every N signups
COOLDOWN_DURATION = 180.0  # 3 minutes cooldown


def countdown(seconds, label):
    for remaining in range(int(seconds), 0, -1):
        print(f"  [{label}] {remaining}s remaining...", end="\r")
        time.sleep(1)
    print()


def run_batch_signup():
    print("==================================================")
    print(f"   BATCH SIGNUP (SLOW): {TOTAL_ACCOUNTS} Accounts")
    print(f"   Delay: {MIN_DELAY_BETWEEN}-{MAX_DELAY_BETWEEN}s between signups")
    print(f"   Cooldown: {COOLDOWN_DURATION}s every {COOLDOWN_EVERY} signups")
    print("==================================================\n")

    create_tables()

    success_count = 0
    fail_count = 0
    created_emails = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)

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

            if i >= TOTAL_ACCOUNTS:
                break

            # Long cooldown every N signups
            if i % COOLDOWN_EVERY == 0:
                print(f"  [Cooldown] {i} done. Waiting {int(COOLDOWN_DURATION)}s to reset rate limit window...")
                countdown(COOLDOWN_DURATION, "Cooldown")
                print()
            else:
                delay = random.uniform(MIN_DELAY_BETWEEN, MAX_DELAY_BETWEEN)
                print(f"  [Delay] Waiting {delay:.0f}s before next signup...")
                countdown(delay, "Next signup in")
                print()

        browser.close()

    print("\n==================================================")
    print("   BATCH SIGNUP COMPLETE")
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
