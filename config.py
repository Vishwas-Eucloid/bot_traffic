import random

# =====================================
# WEBSITE
# =====================================
BASE_URL = "https://new-poc.duckdns.org"
CHROME_CDP_URL = "http://127.0.0.1:9222"

# =====================================
# DAILY TRAFFIC
# =====================================
# Removed TOTAL_DAILY_USERS as the script is now completely dynamic
MAX_PARALLEL_USERS = 1

# =====================================
# DEVICE SPLIT
# =====================================
MWEB_PERCENTAGE_RANGE = (70, 75)
DESKTOP_PERCENTAGE_RANGE = (25, 30)

# =====================================
# USER TYPE SPLIT
# =====================================
LOGGED_OUT_RANGE = (55, 65)
RETURNING_LOGGED_IN_RANGE = (15, 25)
NEW_SIGNUP_RANGE = (5, 10)

# =====================================
# JOURNEY RANGES
# =====================================
JOURNEY_RANGES = {
    "bounce": (100, 130),
    "category_browse": (65, 90),
    "search_discovery": (30, 50),
    "search_discovery_success": (20, 30),
    "product_explore": (55, 80),
    "cart_abandon": (60, 85),
    "checkout_abandon": (30, 50),
    "successful_purchase": (35, 55),
    "deal_hunter": (40, 60),
    "deal_hunter_success": (15, 20),
}

# =====================================
# STATIC PASSWORD
# =====================================
DEFAULT_USER_PASSWORD = "Test@123"

# =====================================
# TIMEOUTS
# =====================================
NAVIGATION_TIMEOUT = 60000  # 60 seconds

# =====================================
# SEARCH TERMS
# =====================================
SEARCH_TERMS = [
    "tablet", "phone", "laptop", "pc", "mouse",
    "headphones", "camera", "earbuds", "printer",
    "watch", "gaming"
]