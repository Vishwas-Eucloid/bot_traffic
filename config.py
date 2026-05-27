import random

# =====================================
# WEBSITE
# =====================================

BASE_URL = "https://new-poc.duckdns.org"
CHROME_CDP_URL = "http://127.0.0.1:9222"

# =====================================
# DAILY TRAFFIC
# =====================================

TOTAL_DAILY_USERS = 50
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
    "bounce": (85, 110),
    "category_browse": (55, 75),
    "search_discovery": (25, 40),
    "search_discovery_success": (15, 25),
    "product_explore": (45, 65),
    "cart_abandon": (50, 70),
    "checkout_abandon": (25, 40),
    "successful_purchase": (30, 45),
    "returning_logged_in": (50, 70),
    "deal_hunter": (35, 50),
    "deal_hunter_success": (15, 25),
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
    "tablet",
    "phone",
    "laptop",
    "pc",
    "mouse",
    "headphones",
    "camera",
    "earbuds",
    "printer",
    "watch",
    "gaming"
]
 