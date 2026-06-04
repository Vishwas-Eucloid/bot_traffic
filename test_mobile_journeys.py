import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth.login import perform_login
from core.analytics import AnalyticsMonitor

from journeys import (
    bounce, category_browse, search_discovery, search_discovery_success,
    product_explore, cart_abandon, checkout_abandon, successful_purchase,
    returning_logged_in, deal_hunter, deal_hunter_success
)

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

def test_mobile_journey_over_cdp(journey_name):
    """Executes an isolated mobile web journey connecting via an active Chrome CDP bridge."""
    cdp_url = os.environ.get("CHROME_CDP", "http://127.0.0.1:9222")
    print(f"\n==================================================")
    print(f" 🧪 TESTING MWEB VIA CDP: {journey_name.upper()}")
    print(f"==================================================")

    with sync_playwright() as p:
        try:
            # Reverted to your trusted CDP connection method
            browser = p.chromium.connect_over_cdp(cdp_url)
            
            # Extract and inject the official iPhone 13 profile context
            iphone_profile = p.devices['iPhone 13']
            context = browser.new_context(**iphone_profile)
            
            page = context.new_page()
            page.is_mobile = True  # Activates the mobile scroll & menu pathways

            analytics_monitor = AnalyticsMonitor(f"CDP-Test-{journey_name}")
            analytics_monitor.attach(page)

            if journey_name == "returning_logged_in":
                print("  -> [Auth] Pre-authenticating returning mobile user...")
                authenticated = perform_login(page)
                if not authenticated:
                    print("  ❌ [Auth] Login failed. Skipping journey.")
                    return

            journey_module = JOURNEY_MAP.get(journey_name)
            if journey_module:
                journey_module.run_journey(page)
                print(f"\n  ✅ [SUCCESS] {journey_name.upper()} executed over CDP successfully.")
            else:
                print(f"\n  ❌ Error: Route identifier missing: {journey_name}")

            # Crucial: Give PostHog tracking events an extra moment to leave before closing context
            print("  -> [PostHog] Pausing briefly to allow analytic queue to drain...")
            time.sleep(5.0)

        except Exception as e:
            print(f"\n  ❌ [CRASH] Unhandled exception in {journey_name}: {e}")
            
        finally:
            if 'context' in locals():
                context.close()
            print("  -> Context closed cleanly. Leaving background Chrome process alive.")

def run_all_mobile_tests_via_cdp():
    print("==================================================")
    print("   SINGITRONIC CDP MOBILE JOURNEY TEST ENGINE")
    print("==================================================")
    
    all_journeys = list(JOURNEY_MAP.keys())
    
    for idx, journey in enumerate(all_journeys, start=1):
        print(f"\nProgress: [{idx}/{len(all_journeys)}]")
        test_mobile_journey_over_cdp(journey)
        
        if idx < len(all_journeys):
            time.sleep(2)

    print("\n==================================================")
    print("   🏁 ALL MOBILE CDP TESTS COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    run_all_mobile_tests_via_cdp()