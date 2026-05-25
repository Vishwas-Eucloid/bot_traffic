# core/navigation.py
 
import random

import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
 
from config import BASE_URL, NAVIGATION_TIMEOUT, SEARCH_TERMS

from core import selectors

from auth.user_generator import generate_user
 
def human_delay(min_sec=1.0, max_sec=3.0):

    """Simulates a human reading or hesitating before clicking."""

    time.sleep(random.uniform(min_sec, max_sec))
 
def wait_for_page(page):

    """Wait for network load state, catching timeouts gracefully."""

    try:

        page.wait_for_load_state("load", timeout=NAVIGATION_TIMEOUT)

    except PlaywrightTimeoutError:

        print("  -> [Nav] Page load timeout exceeded, continuing anyway.")
 
def goto_homepage(page):

    """Navigates to the homepage."""

    print("  -> [Nav] Opening Homepage")

    try:

        page.goto(BASE_URL, wait_until="load", timeout=NAVIGATION_TIMEOUT)

    except PlaywrightTimeoutError:

        print("  -> [Nav] Timeout opening homepage, continuing anyway.")

    human_delay(1.5, 2.5)
 
def click_random_category(page):
    """Finds all categories and clicks a random one, waiting for attachment."""
    print("  -> [Nav] Clicking a random category")
    try:
        # Hardening: Wait up to 5 seconds for at least one category link to exist
        page.wait_for_selector(selectors.CATEGORY_SELECTOR, state="attached", timeout=5000)
        categories = page.locator(selectors.CATEGORY_SELECTOR)
        if categories.count() > 0:
            idx = random.randint(0, min(categories.count() - 1, 5))
            categories.nth(idx).click()
            wait_for_page(page)
            human_delay(1.5, 3)
        else:
            print("  -> [Nav] Warning: No categories found after counting.")
    except Exception:
        print("  -> [Nav] Warning: Timeout waiting for categories to attach to DOM.")
 
def execute_search(page):

    """Types a random search term from config and presses Enter."""

    term = random.choice(SEARCH_TERMS)

    print(f"  -> [Nav] Searching for: {term}")

    # Grab the selector, but explicitly tell Playwright to use the FIRST one it finds

    search_input = page.locator(selectors.SEARCH_INPUT_SELECTOR).first

    # Fill and press Enter on that specific input

    search_input.fill(term)

    search_input.press("Enter")

    wait_for_page(page)

    human_delay(2, 4)
 
 
def view_random_product(page):
    """Clicks 'View Product' on a random item, waiting for content to render."""
    print("  -> [Nav] Viewing a random product (PDP)")
    try:
        # Hardening: Wait up to 5 seconds for product cards to load from the API
        page.wait_for_selector(selectors.PRODUCT_CARD_SELECTOR, state="visible", timeout=5000)
        cards = page.locator(selectors.PRODUCT_CARD_SELECTOR)
        if cards.count() > 0:
            idx = random.randint(0, min(cards.count() - 1, 9))
            selected_card = cards.nth(idx)
            view_btn = selected_card.locator(selectors.VIEW_PRODUCT_TEXT).first
            if view_btn.count() > 0:
                view_btn.click()
            else:
                selected_card.click()
            wait_for_page(page)
            human_delay(2, 5)
        else:
            print("  -> [Nav] Warning: Zero product cards found on page layout.")
    except Exception:
        print("  -> [Nav] Warning: Timeout waiting for product cards to become visible.")

def add_to_cart(page):

    """Clicks the Add to Cart button on a product page."""

    print("  -> [Nav] Adding item to cart")

    try:

        btn = page.locator(selectors.ADD_TO_CART_TEXT).first

        if btn.count() > 0:

            btn.click()

            human_delay(1, 2)

        else:

            print("  -> [Nav] Warning: 'Add to Cart' button not found.")

    except Exception as e:

        print(f"  -> [Nav] Add to cart error: {e}")
 
def proceed_to_checkout(page):

    """Clicks Buy Now and waits for the checkout form."""

    print("  -> [Nav] Proceeding to checkout")

    try:

        buy_btn = page.locator(selectors.BUY_NOW_TEXT).first

        if buy_btn.count() > 0:

            buy_btn.click()

            wait_for_page(page)

            human_delay(2, 3)

        else:

            print("  -> [Nav] Warning: 'Buy Now' button not found.")

    except Exception as e:

        print(f"  -> [Nav] Checkout error: {e}")
 
def fill_checkout_form(page):

    """Generates fake data and waits for the checkout form using precise selectors.

    Dynamically skips auto-filled values for logged-in users while ensuring 

    the missing mobile number is always populated.

    """

    print("  -> [Nav] Waiting for checkout form to become visible and interactive...")

    try:

        # Explicitly wait up to 15 seconds for your actual first name field to render

        page.wait_for_selector('input[name="name-input"]', state="visible", timeout=15000)

        print("  -> [Nav] React checkout form rendered! Processing fields...")

        # Give React state a fraction of a second to bind to the inputs/finish auto-filling

        human_delay(0.5, 1.0)

    except PlaywrightTimeoutError:

        print("  -> [Nav] ERROR: Checkout form elements did not become visible within the timeout limit.")

        return

    user = generate_user()

    try:

        # 1. ALWAYS fill the phone number since it does not auto-fill for logged-in users

        if page.locator('input[name="phone-input"]').count() > 0:

            page.fill('input[name="phone-input"]', "9400000000")

            print("  -> [Nav] Populated missing phone number field.")
 
        # 2. DEFENSIVELY fill out the remaining fields only if they are currently empty

        if page.locator('input[name="name-input"]').count() > 0:

            if page.locator('input[name="name-input"]').input_value() == "":

                page.fill('input[name="name-input"]', user["firstname"])

        if page.locator('input[name="lastname-input"]').count() > 0:

            if page.locator('input[name="lastname-input"]').input_value() == "":

                page.fill('input[name="lastname-input"]', user["lastname"])

        if page.locator('input[name="email-address"]').count() > 0:

            if page.locator('input[name="email-address"]').input_value() == "":

                page.fill('input[name="email-address"]', user["email"])

        if page.locator('input[name="company"]').count() > 0:

            if page.locator('input[name="company"]').input_value() == "":

                page.fill('input[name="company"]', user["company"])

        if page.locator('input[name="address"]').count() > 0:

            if page.locator('input[name="address"]').input_value() == "":

                page.fill('input[name="address"]', user["addressline"])

        if page.locator('input[name="apartment"]').count() > 0:

            if page.locator('input[name="apartment"]').input_value() == "":

                page.fill('input[name="apartment"]', user["apartment"])

        if page.locator('input[name="city"]').count() > 0:

            if page.locator('input[name="city"]').input_value() == "":

                page.fill('input[name="city"]', user["city"])

        if page.locator('input[name="region"]').count() > 0:

            if page.locator('input[name="region"]').input_value() == "":

                page.fill('input[name="region"]', "United States") # Overriding with valid country text

        if page.locator('input[name="postal-code"]').count() > 0:

            if page.locator('input[name="postal-code"]').input_value() == "":

                page.fill('input[name="postal-code"]', user["postalcode"])

        print("  -> [Nav] Checkout form validation complete.")

        human_delay(2, 4)

    except Exception as e:

        print(f"  -> [Nav] Checkout form fill error: {e}")
 
  
def place_order(page):

    """Clicks Place Order to complete a purchase."""

    print("  -> [Nav] Placing order")

    try:

        place_btn = page.locator(selectors.PLACE_ORDER_TEXT).first

        if place_btn.count() > 0:

            place_btn.click()

            # Wait for the thank you page redirect

            page.wait_for_url("**/thank-you*", timeout=NAVIGATION_TIMEOUT)

            human_delay(1, 2)

        else:

            print("  -> [Nav] Warning: 'Place Order' button not found.")

    except Exception as e:

        print(f"  -> [Nav] Place order error: {e}")
 