from core.navigation import goto_homepage, execute_search, view_random_product
 
def run_journey(page):

    print("  -> [Journey] Executing: Search Discovery (Abandon)")

    goto_homepage(page)

    execute_search(page)

    view_random_product(page)

    print("  -> [Journey] User finished exploring and left.")
 