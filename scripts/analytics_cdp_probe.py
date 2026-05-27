import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import BASE_URL, NAVIGATION_TIMEOUT
from core.analytics import AnalyticsMonitor, read_analytics_state, wait_for_analytics_flush
from core.browser_runtime import build_context_options


def run_probe(output_path, screenshot_path, strict):
    report = {
        "base_url": BASE_URL,
        "analytics": {},
        "browser_state": {},
        "console_errors": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.new_context(**build_context_options())
        page = context.new_page()

        monitor = AnalyticsMonitor("Probe")
        monitor.attach(page)

        page.on(
            "console",
            lambda message: report["console_errors"].append(
                {
                    "type": message.type,
                    "text": message.text,
                }
            )
            if message.type in ("error", "warning")
            else None,
        )

        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT)

            try:
                page.wait_for_load_state("load", timeout=NAVIGATION_TIMEOUT)
            except PlaywrightTimeoutError:
                print("[Analytics Probe] Page load timed out; continuing with diagnostics.")

            wait_for_analytics_flush(page, "Probe")
            report["browser_state"] = read_analytics_state(page)
            page.screenshot(path=str(screenshot_path), full_page=True)

        finally:
            report["analytics"] = {
                "request_count": len(monitor.requests),
                "response_count": len(monitor.responses),
                "failure_count": len(monitor.failures),
                "requests": monitor.requests,
                "responses": monitor.responses,
                "failures": monitor.failures,
            }

            output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            monitor.print_summary()
            context.close()
            browser.close()

    if strict and report["analytics"]["request_count"] == 0:
        print("[Analytics Probe] No GA/PostHog browser requests were observed.")
        return 1

    if strict and report["analytics"]["response_count"] == 0:
        print("[Analytics Probe] GA/PostHog requests were seen, but none completed.")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="analytics-probe.json",
        help="Path to write JSON diagnostics.",
    )
    parser.add_argument(
        "--screenshot",
        default="analytics-probe.png",
        help="Path to write the loaded homepage screenshot.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if no analytics browser requests complete.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    screenshot_path = Path(args.screenshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    raise SystemExit(run_probe(output_path, screenshot_path, args.strict))


if __name__ == "__main__":
    main()
