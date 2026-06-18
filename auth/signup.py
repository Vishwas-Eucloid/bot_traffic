import os
import time
import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from auth.user_generator import generate_user
from config import BASE_URL, NAVIGATION_TIMEOUT

# Securely grab the secret from the environment (with your hardcoded fallback just in case)
BOT_API_SECRET = os.environ.get("BOT_API_SECRET", "singitronic_bot_secure_key_9948abc")
API_URL = f"{BASE_URL}/api/bot-users"

def save_new_bot_user(email, password):
    """Securely pushes new bot credentials to the Next.js API."""
    print("  -> [API] Saving new credentials to persistent EC2 database...")
    
    headers = {
        "Authorization": f"Bearer {BOT_API_SECRET}",
        "Content-Type": "application/json"
    }
    payload = {"email": email, "password": password}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            print("  -> [API] Success! Credentials securely stored.")
            return True
        else:
            print(f"  -> [API] Server rejected save request: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  -> [API] Network error saving to backend: {e}")
        return False

def perform_signup(page):
    user = generate_user()
    print(f"  -> [Auth] Attempting fresh signup for: {user['email']}")

    try:
        page.goto(f"{BASE_URL}/register", wait_until="load", timeout=NAVIGATION_TIMEOUT)

        # YOUR EXACT ORIGINAL SELECTORS (Unchanged)
        page.fill('input[name="name"]', user["firstname"])
        page.fill('input[name="lastname"]', user["lastname"])
        page.fill('input[type="email"]', user["email"])
        page.fill('input[name="password"]', user["password"])
        page.fill('input[name="confirmpassword"]', user["password"])
        page.fill('input[name="addressLine"]', user["addressline"])
        page.fill('input[name="apartment"]', user["apartment"])
        page.fill('input[name="company"]', user["company"])
        page.fill('input[name="city"]', user["city"])
        page.fill('input[name="country"]', user["country"])
        page.fill('input[name="postalCode"]', user["postalcode"])

        # Check the terms and conditions checkbox
        page.check('input[type="checkbox"]')
        time.sleep(0.5)

        # Click submit
        print("  -> [Auth] Submitting registration form...")
        page.click('button[type="submit"]')

        # 🚨 THE FIX: Force Playwright to wait for Next.js to navigate away from the register page
        try:
            # We wait up to 10 seconds for the URL to NOT contain "register"
            page.wait_for_url(lambda url: "register" not in url, timeout=10000)
        except PlaywrightTimeoutError:
            # If 10 seconds pass and we are still here, it actually failed
            pass 

        # Now we can accurately check if we are still stuck on the register page
        if "register" in page.url:
            print("  -> [Auth] ERROR: Signup failed. Still on registration page.")
            return False

        print("  -> [Auth] Signup successful in UI!")

        # Push to your EC2 database via API
        save_new_bot_user(user["email"], user["password"])
        
        # Return both so the main script can instantly perform the login handoff
        return user["email"], user["password"]

    except PlaywrightTimeoutError:
        print("  -> [Auth] ERROR: Signup execution timed out.")
        return False
    except Exception as e:
        print(f"  -> [Auth] ERROR: An unexpected signup failure occurred: {e}")
        return False