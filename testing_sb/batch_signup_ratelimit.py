import sys
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth.signup import perform_signup
from database import create_tables

# -------------------------------------------------------
# Rate limit on /api/register: 5 requests per 15 minutes
# per IP (in-memory Map, resets 15 min after first hit).
# Strategy: run 5 signups per batch, wait 16 min between.
# -------------------------------------------------------
TOTAL_ACCOUNTS    = 10
BATCH_SIZE        = 5        # max allowed before rate limit triggers
BATCH_WAIT_SEC    = 16 * 60  # 16 minutes — just over the 15-min window
BETWEEN_DELAY_MIN = 8.0      # seconds between signups within a batch
BETWEEN_DELAY_MAX = 14.0     # seconds between signups within a batch


def countdown(seconds, label):
    for remaining in range(int(seconds), 0, -1):
        mins, secs = divmod(remaining, 60)
        print(f"  [{label}] {mins:02d}:{secs:02d} remaining...   ", end="\r")
        time.sleep(1)
    print()


def run_batch(browser, batch_num, batch_size, success_list, fail_list):
    print(f"\n========== BATCH {batch_num} ({batch_size} signups) ==========")
    for i in range(1, batch_size + 1):
        global_idx = (batch_num - 1) * BATCH_SIZE + i
        print(f"--- [{global_idx}/{TOTAL_ACCOUNTS}] Signup #{i} of batch {batch_num} ---")

        context = browser.new_context(
            viewport={"width": 1365, "height": 900},
            locale="en-US",
        )
        page = context.new_page()
        page.is_mobile = False

        try:
            result = perform_signup(page)
            if result and isinstance(result, tuple):
                email, _ = result
                success_list.append(email)
                print(f"[OK] → {email}\n")
            else:
                fail_list.append(global_idx)
                print(f"[FAIL] Signup #{global_idx} did not complete.\n")
        except Exception as e:
            fail_list.append(global_idx)
            print(f"[FAIL] Signup #{global_idx} crashed: {e}\n")
        finally:
            context.close()

        if i < batch_size:
            delay = random.uniform(BETWEEN_DELAY_MIN, BETWEEN_DELAY_MAX)
            print(f"  [Delay] {delay:.0f}s until next signup in this batch...")
            countdown(delay, "Next signup")


def run():
    print("==================================================")
    print(f"   BATCH SIGNUP — Rate-Limit Aware")
    print(f"   Target  : {TOTAL_ACCOUNTS} accounts")
    print(f"   Strategy: {BATCH_SIZE} signups / batch, {BATCH_WAIT_SEC//60} min between batches")
    print("==================================================\n")

    create_tables()

    successes = []
    failures  = []

    total_batches = -(-TOTAL_ACCOUNTS // BATCH_SIZE)  # ceiling division

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)

        for batch_num in range(1, total_batches + 1):
            remaining = TOTAL_ACCOUNTS - (batch_num - 1) * BATCH_SIZE
            this_batch_size = min(BATCH_SIZE, remaining)

            run_batch(browser, batch_num, this_batch_size, successes, failures)

            if batch_num < total_batches:
                print(f"\n  [Rate Limit] Batch {batch_num} done. "
                      f"Waiting {BATCH_WAIT_SEC // 60} min for rate limit window to reset...")
                countdown(BATCH_WAIT_SEC, "Next batch")

        browser.close()

    print("\n==================================================")
    print("   ALL BATCHES COMPLETE")
    print("==================================================")
    print(f"  Successful : {len(successes)}")
    print(f"  Failed     : {len(failures)}")
    if successes:
        print(f"\n  Created accounts:")
        for email in successes:
            print(f"    - {email}")
    print(f"\n  DB: storage/bot_users.db")
    print("==================================================\n")


if __name__ == "__main__":
    run()
