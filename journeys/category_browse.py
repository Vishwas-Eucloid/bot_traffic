from core.navigation import goto_homepage, click_random_category, view_random_product
 
def run_journey(page):

    print("  -> [Journey] Executing: Category Browse")

    goto_homepage(page)

    click_random_category(page)

    view_random_product(page)
 