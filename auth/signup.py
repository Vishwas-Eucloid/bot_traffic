# auth/signup.py

import time

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

    # Tiny pause to allow React state handlers to process the check event

    time.sleep(0.5)
 
    # Click submit and wait for the dashboard/landing state to load

    page.click('button[type="submit"]')

    page.wait_for_load_state("load", timeout=NAVIGATION_TIMEOUT)
 
    # Persist to SQLite state database

    save_user(

        user["email"],

        user["password"]

    )
 
    return True
 