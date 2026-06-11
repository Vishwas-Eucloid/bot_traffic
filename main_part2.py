import os
import random
import time
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

from core.analytics import AnalyticsMonitor, wait_for_analytics_flush
from core.browser_runtime import build_context_options

from config import (
    MAX_PARALLEL_USERS, JOURNEY_RANGES,
    NEW_SIGNUP_RANGE, MWEB_PERCENTAGE_RANGE,
    LOGGED_OUT_RANGE, RETURNING_LOGGED_IN_RANGE
)
from auth.signup import perform_signup
from auth.login import perform_login

# Import ONLY Part 2 journeys
from journeys import (
    cart_abandon, checkout_abandon, successful_purchase, deal_hunter, deal_hunter_success
)

# Hardcoded Part 2 Map
JOURNEY_MAP = {
    "cart_abandon": cart_abandon,
    "checkout_abandon": checkout_abandon,
    "successful_purchase": successful_purchase,
    "deal_hunter": deal_hunter,
    "deal_hunter_success": deal_hunter_success
}

def generate_daily_distribution():
    pool = []
    for j_name in JOURNEY_MAP.keys():
        if j_name not in JOURNEY_RANGES:
            continue
            
        min_val, max_val = JOURNEY_RANGES[j_name]
        journey_total = random.randint(min_val, max_val)
        
        journey_mweb_pct = random.randint(MWEB_PERCENTAGE_RANGE[0], MWEB_PERCENTAGE_RANGE[1]) / 100.0
        journey_logged_in_pct = random.randint(RETURNING_LOGGED_IN_RANGE[0], RETURNING_LOGGED_IN_RANGE[1]) / 100.0
        journey_signup_pct = random.randint(NEW_SIGNUP_RANGE[0], NEW_SIGNUP_RANGE[1]) / 100.0

        mobile_count = int(round(journey_total * journey_mweb_pct))
        desktop_count = journey_total - mobile_count
        
        logged_in_count = int(round(journey_total * journey_logged_in_pct))
        signup_count = int(round(journey_total * journey_signup_pct))
        guest_count = journey_total - (logged_in_count + signup_count)

        # Fix rounding off-by-one errors
        while (logged_in_count + signup_count + guest_count) != journey_total:
            if (logged_in_count + signup_count + guest_count) > journey_total:
                guest_count -= 1
            else:
                guest_count += 1

        user_types_for_journey = (
            ["returning_logged_in"] * logged_in_count +
            ["new_signup"] * signup_count +
            ["guest"] * guest_count
        )
        random.shuffle(user_types_for_journey)
        
        devices_for_journey = [True] * mobile_count + [False] * desktop_count
        random.shuffle(devices_for_journey)

        for i in range(journey_total):
            pool.append({
                "journey_name": j_name,
                "is_mobile": devices_for_journey[i],
                "user_type": user_types_for_journey[i]
            })

    random.shuffle(pool)
    return pool

def print_distribution_summary(pool, title="SUMMARY"):
    if not pool:
        print("\n--------------------------------------------------")
        print(f"   {title}")
        print("--------------------------------------------------")
        print("   No records found.")
        print("--------------------------------------------------\n")
        return

    summary = defaultdict(lambda: {"total": 0, "mobile": 0, "desktop": 0, "returning": 0, "signup": 0, "guest": 0})
    for session in pool:
        j_name = session["journey_name"]
        summary[j_name]["total"] += 1
        if session["is_mobile"]: summary[j_name]["mobile"] += 1
        else: summary[j_name]["desktop"] += 1
        
        if session["user_type"] == "returning_logged_in": summary[j_name]["returning"] += 1
        elif session["user_type"] == "new_signup": summary[j_name]["signup"] += 1
        else: summary[j_name]["guest"] += 1

    print("\n--------------------------------------------------")
    print(f"   {title}")
    print("--------------------------------------------------")
    for j_name, stats in summary.items():
        print(f"[{j_name.upper()}]: {stats['total']} Total Runs")
        print(f"  -> Devices: {stats['mobile']} Mobile | {stats['desktop']} Desktop")
        print(f"  -> Users:   {stats['returning']} Returning | {stats['signup']} Signup | {stats['guest']} Guest\n")
    print("--------------------------------------------------\n")

def run_single_bot(session_id, session_config):
    journey_name = session_config["journey_name"]
    is_mobile = session_config["is_mobile"]
    user_type = session_config["user_type"]
    
    cdp_url = os.environ.get("CHROME_CDP", "http://127.0.0.1:9222")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
            context_kwargs = build_context_options()
            
            if is_mobile:
                print(f"[Session #{session_id}] 📱 Mobile | Type: {user_type} | Route: {journey_name}")
                context_kwargs.update(p.devices['iPhone 13'])
                context = browser.new_context(**context_kwargs)
            else:
                print(f"[Session #{session_id}] 💻 Desktop | Type: {user_type} | Route: {journey_name}")
                context_kwargs.update({
                    'viewport': {'width': 1920, 'height': 1080},
                    'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
                })
                context = browser.new_context(**context_kwargs)

            page = context.new_page()
            page.is_mobile = is_mobile
            analytics_monitor = AnalyticsMonitor(f"Session #{session_id}")
            analytics_monitor.attach(page)

            if user_type == "returning_logged_in":
                print(f"  -> [Session #{session_id}] Authenticating returning user...")
                if not perform_login(page):
                    print(f"  -> [Session #{session_id}] Login pipeline dropped. Aborting.")
                    return None
            elif user_type == "new_signup":
                print(f"  -> [Session #{session_id}] Executing initial Guest Signup...")
                signup_credentials = perform_signup(page)
                if signup_credentials:
                    new_email, new_pwd = signup_credentials
                    print(f"  -> [Session #{session_id}] Signup complete! Transitioning to Login...")
                    if not perform_login(page, custom_email=new_email, custom_password=new_pwd):
                        print(f"  -> [Session #{session_id}] Post-signup login failed. Proceeding as Guest.")

            journey_module = JOURNEY_MAP.get(journey_name)
            if journey_module:
                journey_module.run_journey(page)
                
                # Timestamp log after successful completion
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[Session #{session_id}] ⏱️ Journey '{journey_name}' completed at {timestamp}")
                
                return session_config
            else:
                print(f"[Session #{session_id}] Error: Route identifier missing: {journey_name}")
                return None

        except Exception as e:
            print(f"[Session #{session_id}] Critical Failure Encountered: {e}")
            return None
        finally:
            if 'page' in locals():
                wait_for_analytics_flush(page, f"Session #{session_id}")
                time.sleep(3.0) 
            if 'analytics_monitor' in locals(): analytics_monitor.print_summary()
            if 'context' in locals(): context.close()
            if 'browser' in locals(): browser.close()
            print(f"[Session #{session_id}] Cleanly disconnected.\n")

def main():
    print("==================================================")
    print("   SINGITRONIC TRAFFIC ENGINE: PART 2")
    print("==================================================\n")

    target_traffic_pool = generate_daily_distribution()
    print_distribution_summary(target_traffic_pool, "PLANNED TARGET DISTRIBUTION - PART 2")

    print(f"Total Target Runs for Part 2: {len(target_traffic_pool)}")
    time.sleep(2)

    futures = []

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_USERS) as executor:
        for index, session_config in enumerate(target_traffic_pool, start=1):
            futures.append(executor.submit(run_single_bot, index, session_config))
            time.sleep(random.uniform(1.0, 2.5))

    successful_runs = []
    for f in futures:
        result = f.result()
        if result is not None:
            successful_runs.append(result)

    print("\n==================================================")
    print("   EXECUTION COMPLETE - FINAL REPORT (PART 2)")
    print("==================================================")
    
    # This prints the exact same split summary, but only for the bots that succeeded
    print_distribution_summary(successful_runs, "ACTUAL SUCCESSFUL RUNS - PART 2")

if __name__ == "__main__":
    main()