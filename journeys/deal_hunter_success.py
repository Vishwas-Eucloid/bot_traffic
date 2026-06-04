from core.navigation import view_random_product, add_to_cart, proceed_to_checkout, place_order, human_delay, fill_checkout_form

from config import BASE_URL
 
def run_journey(page):

    print("  -> [Journey] Executing: Deal Hunter (Successful Purchase)")

    page.goto(f"{BASE_URL}/offers", wait_until="load")

    human_delay(2, 3)

    view_random_product(page)

    add_to_cart(page)

    proceed_to_checkout(page)

    fill_checkout_form(page)

    place_order(page)

    print("  -> [Journey] Deal hunter successfully purchased an item.")
 