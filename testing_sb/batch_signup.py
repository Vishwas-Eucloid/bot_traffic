import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Allow imports from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth.signup import perform_signup
from database import create_tables

TOTAL_ACCOUNTS = 150


def run_batch_signup():
    print("==================================================")
    print("   BATCH SIGNUP: Creating {} Real Accounts".format(TOTAL_ACCOUNTS))
    print("==================================================\n")

    create_tables()

    success_count = 0
    fail_count = 0
    created_emails = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)

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
                    print(f"[FAIL] Signup #{i} did not complete. Skipping.\n")

            except Exception as e:
                fail_count += 1
                print(f"[FAIL] Signup #{i} crashed: {e}\n")

            finally:
                context.close()
                time.sleep(1.0)  # brief pause between signups

        browser.close()

    print("\n==================================================")
    print("   BATCH SIGNUP COMPLETE")
    print("==================================================")
    print(f"  Successful : {success_count}")
    print(f"  Failed     : {fail_count}")
    print(f"  Total      : {TOTAL_ACCOUNTS}")
    print(f"\n  DB location: storage/bot_users.db")

    if created_emails:
        print(f"\n  First 5 created accounts:")
        for email in created_emails[:5]:
            print(f"    - {email}")
        if len(created_emails) > 5:
            print(f"    ... and {len(created_emails) - 5} more.")

    print("==================================================\n")


if __name__ == "__main__":
    run_batch_signup()
