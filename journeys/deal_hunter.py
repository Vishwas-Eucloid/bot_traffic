from core.navigation import view_random_product, add_to_cart, wait_for_page, human_delay

from config import BASE_URL
 
def run_journey(page):

    print("  -> [Journey] Executing: Deal Hunter (Browse Only)")

    print("  -> [Nav] Navigating directly to Offers page")

    page.goto(f"{BASE_URL}/offers", wait_until="load")

    human_delay(2, 4)

    view_random_product(page)

    add_to_cart(page)

    print("  -> [Journey] Deal hunter added discounted item to cart and left.")
 