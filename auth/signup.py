import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from auth.user_generator import generate_user
from database import save_user
from config import BASE_URL, NAVIGATION_TIMEOUT

def perform_signup(page):
    user = generate_user()

    # Centralized URL using config
    page.goto(f"{BASE_URL}/register", wait_until="load", timeout=NAVIGATION_TIMEOUT)

    # Filling inputs using your exact target selectors
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

    # 🚨 THE VITAL NEXT.JS FIX: Wait for the URL to change away from /register
    try:
        page.wait_for_url(lambda url: "register" not in url, timeout=10000)
    except PlaywrightTimeoutError:
        pass # If it times out, the next if-statement will catch the failure

    if "register" in page.url:
        print("  -> [Auth] ERROR: Signup failed. Still on registration page.")
        return False

    # Persist to SQLite state database
    save_user(user["email"], user["password"])

    print(f"  -> [Auth] Signup successful and saved for: {user['email']}")
    
    # Return both the email and the generated password!
    return user["email"], user["password"]