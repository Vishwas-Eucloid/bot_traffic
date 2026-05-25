from core.navigation import goto_homepage, click_random_category, view_random_product, add_to_cart, proceed_to_checkout, place_order, fill_checkout_form
 
def run_journey(page):

    print("  -> [Journey] Executing: Successful Purchase")

    goto_homepage(page)

    click_random_category(page)

    view_random_product(page)

    add_to_cart(page)

    proceed_to_checkout(page)

    fill_checkout_form(page)

    place_order(page)
 