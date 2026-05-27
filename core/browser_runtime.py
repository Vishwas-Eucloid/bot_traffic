import os


def build_context_options():
    options = {
        "viewport": {
            "width": int(os.environ.get("BOT_VIEWPORT_WIDTH", "1365")),
            "height": int(os.environ.get("BOT_VIEWPORT_HEIGHT", "900")),
        },
        "locale": os.environ.get("BOT_LOCALE", "en-US"),
        "timezone_id": os.environ.get("BOT_TIMEZONE", "America/New_York"),
    }

    user_agent = os.environ.get("BOT_USER_AGENT")
    if user_agent:
        options["user_agent"] = user_agent

    if os.environ.get("BOT_IGNORE_HTTPS_ERRORS", "0") == "1":
        options["ignore_https_errors"] = True

    return options
