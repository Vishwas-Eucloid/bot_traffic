import os
import requests
from config import BASE_URL, NAVIGATION_TIMEOUT
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Securely grab the secret from the GitHub Actions environment
BOT_API_SECRET = os.environ.get("BOT_API_SECRET")
API_URL = f"{BASE_URL}/api/bot-users"

def fetch_user_from_api():
    """Securely fetches a random bot user from the Next.js API."""
    print("  -> [API] Fetching persistent bot credentials from EC2...")
    
    if not BOT_API_SECRET:
        print("  -> [API] ERROR: BOT_API_SECRET is missing from environment variables!")
        return None

    headers = {"Authorization": f"Bearer {BOT_API_SECRET}"}
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data["email"], data["password"]
        else:
            print(f"  -> [API] Server rejected fetch request: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  -> [API] Network error reaching backend: {e}")
        return None

def perform_login(page, custom_email=None, custom_password=None):
    """Logs a user in, either from newly passed credentials or fetching from the DB."""
    
    if custom_email and custom_password:
        print(f"  -> [Auth] Using newly created credentials for: {custom_email}")
        email = custom_email
        password = custom_password
    else:
        print("  -> [Auth] Fetching credentials from EC2 database...")
        credentials = fetch_user_from_api()
        if not credentials:
            print("  -> [Auth] ERROR: No users found in the API database. Please run a signup flow first!")
            return False
        email, password = credentials

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