import os

import random

import time

from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import sync_playwright

from core.analytics import AnalyticsMonitor, wait_for_analytics_flush

from core.browser_runtime import build_context_options
 
# Import parameters from your configuration

from config import TOTAL_DAILY_USERS, MAX_PARALLEL_USERS, JOURNEY_RANGES, NEW_SIGNUP_RANGE

from auth.signup import perform_signup

from auth.login import perform_login
 
# Import all built journey modules from Phase 4

from journeys import (

    bounce, category_browse, search_discovery, search_discovery_success,

    product_explore, cart_abandon, checkout_abandon, successful_purchase,

    returning_logged_in, deal_hunter, deal_hunter_success

)
 
# Explicitly map config dictionary names to active python modules

JOURNEY_MAP = {

    "bounce": bounce,

    "category_browse": category_browse,

    "search_discovery": search_discovery,

    "search_discovery_success": search_discovery_success,

    "product_explore": product_explore,

    "cart_abandon": cart_abandon,

    "checkout_abandon": checkout_abandon,

    "successful_purchase": successful_purchase,

    "returning_logged_in": returning_logged_in,

    "deal_hunter": deal_hunter,

    "deal_hunter_success": deal_hunter_success

}
 
def generate_daily_distribution():

    """Calculates exactly how many of each user journey to simulate today."""

    pool = []

    for j_name, (min_val, max_val) in JOURNEY_RANGES.items():

        count = random.randint(min_val, max_val)

        pool.extend([j_name] * count)
 
    random.shuffle(pool)
 
    if len(pool) > TOTAL_DAILY_USERS:

        pool = pool[:TOTAL_DAILY_USERS]

    elif len(pool) < TOTAL_DAILY_USERS:

        pool.extend(["bounce"] * (TOTAL_DAILY_USERS - len(pool)))
 
    return pool
 
def run_single_bot(session_id, journey_name):

    """The isolated thread worker executing a full user lifecycle via CDP."""

    cdp_url = os.environ.get("CHROME_CDP", "http://127.0.0.1:9222")

    print(f"[Session #{session_id}] Connecting via CDP -> Route: {journey_name}")

    with sync_playwright() as p:

        try:

            # Connect to the remote Chrome instance instead of launching a new one

            browser = p.chromium.connect_over_cdp(cdp_url)

            # new_context creates an isolated session (cookies/storage) within that Chrome instance

            context = browser.new_context(**build_context_options())

            page = context.new_page()

            analytics_monitor = AnalyticsMonitor(f"Session #{session_id}")

            analytics_monitor.attach(page)
 
            # --- PRE-ROUTING AUTH SELECTION ---

            if journey_name == "returning_logged_in":

                authenticated = perform_login(page)

                if not authenticated:

                    print(f"[Session #{session_id}] Login pipeline dropped. Aborting.")

                    return

            else:

                signup_chance = random.uniform(*NEW_SIGNUP_RANGE)

                if random.uniform(0, 100) <= signup_chance:

                    print(f"[Session #{session_id}] Random trigger hit: Guest is signing up first...")

                    perform_signup(page)
 
            # --- JOURNEY PATHWAY EXECUTION ---

            journey_module = JOURNEY_MAP.get(journey_name)

            if journey_module:

                journey_module.run_journey(page)

            else:

                print(f"[Session #{session_id}] Error: Route identifier missing: {journey_name}")
 
        except Exception as e:

            print(f"[Session #{session_id}] Critical Failure Encountered: {e}")

        finally:

            # Securely cleanup all memory scopes at thread termination

            if 'page' in locals():

                wait_for_analytics_flush(page, f"Session #{session_id}")

            if 'analytics_monitor' in locals():

                analytics_monitor.print_summary()

            if 'context' in locals():

                context.close()

            if 'browser' in locals():

                # For connect_over_cdp, browser.close() disconnects the websocket. 

                # It does NOT close the actual Chrome application you attached to.

                browser.close() 

            print(f"[Session #{session_id}] Cleanly disconnected.")
 
def main():

    print("==================================================")

    print("   SINGITRONIC CDP TRAFFIC GENERATOR   ")

    print("==================================================\n")

    daily_traffic_pool = generate_daily_distribution()

    print(f"Total Target Simulation Runs Scheduled: {len(daily_traffic_pool)}")

    print(f"Configured Concurrency Capacity: {MAX_PARALLEL_USERS} browsers\n")

    print("Initializing ThreadPoolExecutor...\n")

    time.sleep(2)
 
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_USERS) as executor:

        for index, journey_name in enumerate(daily_traffic_pool, start=1):

            executor.submit(run_single_bot, index, journey_name)

            # Important: When connecting via CDP to a single browser, adding a slightly 

            # larger stagger prevents overwhelming the Chrome debugging websocket port.

            time.sleep(random.uniform(1.0, 2.5))

    print("\n==================================================")

    print("   SUCCESS: ALL SIMULATED TRAFFIC PATHS REPLICA COMPLETE")

    print("==================================================")

if __name__ == "__main__":

    main()
