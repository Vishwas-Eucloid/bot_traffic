from core.navigation import goto_homepage, click_random_category, view_random_product, add_to_cart
 
def run_journey(page):

    print("  -> [Journey] Executing: Cart Abandonment")

    goto_homepage(page)

    click_random_category(page)

    view_random_product(page)

    add_to_cart(page)

    print("  -> [Journey] User added item to cart but abandoned.")
 