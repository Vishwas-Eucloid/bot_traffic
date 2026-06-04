from core.navigation import goto_homepage, click_random_category, view_random_product
 
def run_journey(page):

    print("  -> [Journey] Executing: Product Deep Explore")

    goto_homepage(page)

    click_random_category(page)

    view_random_product(page)

    # They go back and look at another product

    click_random_category(page) 

    view_random_product(page)

    print("  -> [Journey] User compared products and left.")
 