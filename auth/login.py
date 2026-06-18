from database import get_random_user

from config import BASE_URL, NAVIGATION_TIMEOUT

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError



def perform_login(page, custom_email=None, custom_password=None):

    """Logs a user in, either from newly passed credentials or fetching from the DB."""

   

    if custom_email and custom_password:

        print(f"  -> [Auth] Using newly created credentials for: {custom_email}")

        email = custom_email

        password = custom_password

    else:

        print("  -> [Auth] Fetching credentials from local database...")

        user = get_random_user()

        if not user:

            print("  -> [Auth] ERROR: No users found in the local SQLite database. Please run a signup flow first!")

            return False

        email, password = user



    print(f"  -> [Auth] Attempting login for user: {email}")



    try:

        page.goto(f"{BASE_URL}/login", wait_until="load", timeout=NAVIGATION_TIMEOUT)



        page.fill('input[type="email"]', email)

        page.fill('input[name="password"]', password)



        print("  -> [Auth] Submitting login credentials...")

        page.click('button[type="submit"]')



        page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)



        login_cta = page.locator('a[href*="login"], button:has-text("Login")').first

        if login_cta.count() > 0 and login_cta.is_visible():

            print("  -> [Debug] Post-Login Warning: Form submitted, but Login CTA is still visible in the GNB.")

            return False # <--- THE FIX: It now accurately reports the failure to main.py

        else:

            print("  -> [Debug] Post-Login Success: Login CTA has disappeared from GNB. Session is active!")



        return True



    except PlaywrightTimeoutError:

        print("  -> [Auth] ERROR: Login execution timed out.")

        return False

    except Exception as e:

        print(f"  -> [Auth] ERROR: An unexpected login failure occurred: {e}")

        return False