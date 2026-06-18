import random
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import BASE_URL, NAVIGATION_TIMEOUT, SEARCH_TERMS
from core import selectors
from auth.user_generator import generate_user

# =====================================================================
# --- CORE HUMAN SIMULATION HELPERS (WITH SMOOTH SCROLLING) ---
# =====================================================================

def human_delay(min_sec=2.0, max_sec=5.0):
    """Simulates a human reading or hesitating before an action."""
    time.sleep(random.uniform(min_sec, max_sec))

def human_scroll_down(page, total_distance=600, steps=6):
    """Simulates a human smoothly dragging/scrolling down a mobile viewport."""
    print(f"  -> [Action] Smooth scrolling down viewport...")
    try:
        for _ in range(steps):
            increment = total_distance // steps
            variance = random.randint(-15, 15)
            page.evaluate(f"window.scrollBy(0, {increment + variance})")
            time.sleep(random.uniform(0.3, 0.6))  # Human pace between drags
        human_delay(1.0, 2.0)
    except Exception as e:
        # We don't raise here because a minor scroll glitch shouldn't fail the whole run
        print(f"  -> [Action] Warning: Scroll action ran into a minor issue: {e}")

def human_click_element(element):
    """Simulates a realistic human click with micro and macro delays."""
    element.scroll_into_view_if_needed()
    human_delay(1.5, 3.0)  # Human reading/thinking time
    element.click(delay=random.randint(80, 300))  # Slower physical mouse press

def human_type_element(element, text):
    """Simulates realistic human typing with absolute focus and delays."""
    element.scroll_into_view_if_needed()
    human_delay(1.5, 3.0)
    element.click(delay=random.randint(80, 200))
    element.focus()  # Force absolute focus on input element before typing
    element.fill("") 
    element.type(text, delay=random.randint(100, 250)) # Slower typing speed

def wait_for_page(page):
    """Wait for network load state, catching timeouts gracefully."""
    try:
        page.wait_for_load_state("load", timeout=NAVIGATION_TIMEOUT)
    except PlaywrightTimeoutError:
        print("  -> [Nav] Page load timeout exceeded, continuing anyway.")

# =====================================================================
# --- NAVIGATION & JOURNEYS ---
# =====================================================================

def goto_homepage(page):
    """Navigates to the homepage."""
    print("  -> [Nav] Opening Homepage")
    try:
        page.goto(BASE_URL, wait_until="load", timeout=NAVIGATION_TIMEOUT)
    except PlaywrightTimeoutError as e:
        print("  -> [Nav] Timeout opening homepage.")
        raise e  # Fails the bot
    human_delay(2.0, 4.0)

def click_random_category(page):
    """Finds all categories and clicks a random one, scrolling to them on mobile."""
    print("  -> [Nav] Clicking a random category")
    try:
        if getattr(page, 'is_mobile', False):
            print("  -> [Nav] Mobile detected: Scrolling down to category cards...")
            human_scroll_down(page, total_distance=300, steps=3)

        page.wait_for_selector(selectors.CATEGORY_SELECTOR, state="attached", timeout=15000)
        categories = page.locator(selectors.CATEGORY_SELECTOR)
        
        if categories.count() > 0:
            idx = random.randint(0, min(categories.count() - 1, 5))
            human_click_element(categories.nth(idx))
            wait_for_page(page)
        else:
            print("  -> [Nav] Warning: No categories found after counting.")
            raise Exception("No categories found to click.")
    except Exception as e:
        print("  -> [Nav] ERROR: Failed to interact with categories.")
        raise e  # Fails the bot

def execute_search(page):
    """Opens the mobile menu if necessary, targets the visible input by placeholder, and searches."""
    term = random.choice(SEARCH_TERMS)
    print(f"  -> [Nav] Preparing to search for: {term}")
    
    try:
        if getattr(page, 'is_mobile', False):
            print("  -> [Nav] Mobile detected: Opening hamburger menu to expose search bar...")
            mobile_menu_btn = page.get_by_role("button").first
            
            if mobile_menu_btn.count() > 0:
                human_click_element(mobile_menu_btn)
                time.sleep(2.0) 
            else:
                print("  -> [Nav] Warning: Hamburger menu button not found.")
                raise Exception("Mobile menu button missing.")
                
            search_input = page.get_by_placeholder("Search products...").filter(visible=True).first
        else:
            page.wait_for_selector(selectors.SEARCH_INPUT_SELECTOR, state="visible", timeout=15000)
            search_input = page.locator(selectors.SEARCH_INPUT_SELECTOR).first
        
        search_input.wait_for(state="visible", timeout=10000)
        search_input.click()
        time.sleep(0.5)
        
        human_type_element(search_input, term)
        search_input.press("Enter", delay=random.randint(80, 200))
        
        wait_for_page(page)
        human_delay(3.0, 5.0)
        
    except Exception as e:
        print(f"  -> [Nav] Search execution error: {e}")
        raise e  # Fails the bot

def view_random_product(page):
    """Clicks 'View Product' on a random item, waiting for content to render."""
    print("  -> [Nav] Viewing a random product (PDP)")
    
    try:
        human_scroll_down(page, total_distance=400, steps=4)

        page.wait_for_selector(selectors.PRODUCT_CARD_SELECTOR, state="visible", timeout=45000)
        cards = page.locator(selectors.PRODUCT_CARD_SELECTOR)
        
        if cards.count() > 0:
            idx = random.randint(0, min(cards.count() - 1, 9))
            selected_card = cards.nth(idx)
            
            view_btn = selected_card.locator(selectors.VIEW_PRODUCT_TEXT).first
            if view_btn.count() > 0:
                human_click_element(view_btn)
            else:
                human_click_element(selected_card)
                
            wait_for_page(page)
        else:
            print("  -> [Nav] Warning: Zero product cards found on page layout.")
            raise Exception("Zero product cards rendered.")
            
    except Exception as e:
        print(f"  -> [Nav] Warning: Timeout waiting for product cards to become visible: {e}")
        raise e  # Fails the bot

def add_to_cart(page):
    """Clicks the Add to Cart button on a product page after smooth viewport adjustment."""
    print("  -> [Nav] Adding item to cart")
    try:
        human_scroll_down(page, total_distance=500, steps=5)

        page.wait_for_selector(selectors.ADD_TO_CART_TEXT, state="visible", timeout=15000)
        btn = page.locator(selectors.ADD_TO_CART_TEXT).first
        human_click_element(btn)
        
    except Exception as e:
        print("  -> [Nav] Warning: Timeout waiting for 'Add to Cart' button.")
        raise e  # Fails the bot

def proceed_to_checkout(page):
    """Clicks Buy Now and waits for the checkout form."""
    print("  -> [Nav] Proceeding to checkout")
    try:
        human_scroll_down(page, total_distance=200, steps=2)

        page.wait_for_selector(selectors.BUY_NOW_TEXT, state="visible", timeout=15000)
        buy_btn = page.locator(selectors.BUY_NOW_TEXT).first
        human_click_element(buy_btn)
        wait_for_page(page)
        
    except Exception as e:
        print("  -> [Nav] Warning: Timeout waiting for 'Buy Now' button.")
        raise e  # Fails the bot

def fill_checkout_form(page):
    """Generates fake data and waits for the checkout form using precise selectors."""
    print("  -> [Nav] Waiting for checkout form to become visible and interactive...")
    try:
        page.wait_for_selector('input[name="name-input"]', state="visible", timeout=45000)
        print("  -> [Nav] React checkout form rendered! Processing fields...")
        human_delay(1.0, 2.0)
    except PlaywrightTimeoutError as e:
        print("  -> [Nav] ERROR: Checkout form elements did not become visible within the timeout limit.")
        raise e  # Fails the bot
        
    user = generate_user()
    try:
        if page.locator('input[name="phone-input"]').count() > 0:
            page.fill('input[name="phone-input"]', "9400000000")

        if page.locator('input[name="name-input"]').count() > 0 and page.locator('input[name="name-input"]').input_value() == "":
            page.fill('input[name="name-input"]', user["firstname"])
            time.sleep(0.2)
            
        if page.locator('input[name="lastname-input"]').count() > 0 and page.locator('input[name="lastname-input"]').input_value() == "":
            page.fill('input[name="lastname-input"]', user["lastname"])
            time.sleep(0.2)
            
        human_scroll_down(page, total_distance=400, steps=4)

        if page.locator('input[name="email-address"]').count() > 0 and page.locator('input[name="email-address"]').input_value() == "":
            page.fill('input[name="email-address"]', user["email"])
            time.sleep(0.2)
            
        if page.locator('input[name="company"]').count() > 0 and page.locator('input[name="company"]').input_value() == "":
            page.fill('input[name="company"]', user["company"])
            time.sleep(0.2)
            
        if page.locator('input[name="address"]').count() > 0 and page.locator('input[name="address"]').input_value() == "":
            page.fill('input[name="address"]', user["addressline"])
            time.sleep(0.2)
            
        if page.locator('input[name="apartment"]').count() > 0 and page.locator('input[name="apartment"]').input_value() == "":
            page.fill('input[name="apartment"]', user["apartment"])
            time.sleep(0.2)
            
        human_scroll_down(page, total_distance=350, steps=3)

        if page.locator('input[name="city"]').count() > 0 and page.locator('input[name="city"]').input_value() == "":
            page.fill('input[name="city"]', user["city"])
            time.sleep(0.2)
            
        if page.locator('input[name="region"]').count() > 0 and page.locator('input[name="region"]').input_value() == "":
            page.fill('input[name="region"]', "United States")
            time.sleep(0.2)
            
        if page.locator('input[name="postal-code"]').count() > 0 and page.locator('input[name="postal-code"]').input_value() == "":
            page.fill('input[name="postal-code"]', user["postalcode"])
            
        print("  -> [Nav] Checkout form validation complete.")
        human_delay(2.0, 4.0)
        
    except Exception as e:
        print(f"  -> [Nav] Checkout form fill error: {e}")
        raise e  # Fails the bot

def place_order(page):
    """Clicks Place Order to complete a purchase, safely waiting for API resolution."""
    print("  -> [Nav] Placing order")
    
    try:
        page.wait_for_selector(selectors.PLACE_ORDER_TEXT, state="visible", timeout=15000)
        place_btn = page.locator(selectors.PLACE_ORDER_TEXT).first
        
        print("  -> [Nav] Clicking Place Order button and waiting for API response...")
        
        with page.expect_response("**/api/orders", timeout=30000) as response_info:
            human_click_element(place_btn)
            
        response = response_info.value
        if response.ok:
            print("  -> [Nav] API confirmed order! Waiting for React to redirect...")
            page.wait_for_url("**/thank-you*", timeout=15000)
            human_delay(2.0, 3.0)
        else:
            print(f"  -> [Nav] Server rejected the order with status: {response.status}")
            human_delay(3.0, 4.0)
            raise Exception(f"Order rejected by server (HTTP {response.status})") # Fails the bot!
            
    except Exception as e:
        print(f"  -> [Nav] ERROR: An unexpected issue occurred during checkout: {e}")
        raise e  # Fails the bot