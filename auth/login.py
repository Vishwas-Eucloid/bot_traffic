# auth/login.py

from database import get_random_user

from config import BASE_URL, NAVIGATION_TIMEOUT

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
 
def perform_login(page):

    """Fetches a saved user from the local SQLite DB and logs them into the site."""

    print("  -> [Auth] Fetching credentials from local database...")

    user = get_random_user()

    if not user:

        print("  -> [Auth] ERROR: No users found in the local SQLite database. Please run a signup flow first!")

        return False

    email, password = user

    print(f"  -> [Auth] Attempting login for user: {email}")

    try:

        # Navigate directly to your login route

        page.goto(f"{BASE_URL}/login", wait_until="load", timeout=NAVIGATION_TIMEOUT)

        # Fill out credentials using standard input selectors

        page.fill('input[type="email"]', email)

        page.fill('input[name="password"]', password)

        # Click the submit action

        print("  -> [Auth] Submitting login credentials...")

        page.click('button[type="submit"]')

        # --- THE HARDENING FIX ---

        # Instead of just waiting for the page to load, we wait for the network to go completely quiet.

        # This guarantees React has received the auth token response and written it to localStorage/cookies.

        page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)

        # --- THE GNB DEBUGGING STEP ---

        # We check to see if your header changed states dynamically (hiding the login links).

        # This is a safe way to verify if the login session was cleanly initiated.

        login_cta = page.locator('a[href*="login"], button:has-text("Login")').first

        if login_cta.count() > 0 and login_cta.is_visible():

            print("  -> [Debug] Post-Login Warning: Form submitted, but Login CTA is still visible in the GNB.")

        else:

            print("  -> [Debug] Post-Login Success: Login CTA has disappeared from GNB. Session is active!")

        return True
 
    except PlaywrightTimeoutError:

        print("  -> [Auth] ERROR: Login execution timed out.")

        return False

    except Exception as e:

        print(f"  -> [Auth] ERROR: An unexpected login failure occurred: {e}")

        return False
 