from core.navigation import goto_homepage, human_delay
 
def run_journey(page):

    print("  -> [Journey] Executing: Bounce")

    goto_homepage(page)

    human_delay(2, 5) # Looks around briefly and leaves
 