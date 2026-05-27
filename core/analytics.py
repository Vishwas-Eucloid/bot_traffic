import os
from urllib.parse import urlparse


ANALYTICS_HOST_MARKERS = (
    "google-analytics.com",
    "analytics.google.com",
    "googletagmanager.com",
    "posthog.com",
    "i.posthog.com",
)


def is_analytics_url(url):
    host = urlparse(url).netloc.lower()
    return any(marker in host for marker in ANALYTICS_HOST_MARKERS)


class AnalyticsMonitor:
    def __init__(self, label):
        self.label = label
        self.requests = []
        self.responses = []
        self.failures = []

    def attach(self, page):
        page.on("request", self._on_request)
        page.on("response", self._on_response)
        page.on("requestfailed", self._on_request_failed)

    def _on_request(self, request):
        if is_analytics_url(request.url):
            self.requests.append(
                {
                    "method": request.method,
                    "url": request.url,
                    "resource_type": request.resource_type,
                }
            )

    def _on_response(self, response):
        if is_analytics_url(response.url):
            self.responses.append(
                {
                    "status": response.status,
                    "url": response.url,
                }
            )

    def _on_request_failed(self, request):
        if is_analytics_url(request.url):
            self.failures.append(
                {
                    "url": request.url,
                    "failure": request.failure,
                }
            )

    def print_summary(self):
        print(
            f"[Analytics {self.label}] "
            f"requests={len(self.requests)} "
            f"responses={len(self.responses)} "
            f"failures={len(self.failures)}"
        )

        for item in self.responses[:10]:
            print(f"[Analytics {self.label}] HTTP {item['status']} <- {item['url']}")

        for item in self.failures[:10]:
            print(
                f"[Analytics {self.label}] FAILED {item['failure']} <- {item['url']}"
            )


def wait_for_analytics_flush(page, label):
    delay_ms = int(os.environ.get("ANALYTICS_FLUSH_MS", "8000"))

    if delay_ms <= 0:
        return

    print(f"[Analytics {label}] Waiting {delay_ms}ms for GA/PostHog beacons to flush...")

    try:
        page.evaluate(
            """
            async (delayMs) => {
              const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

              try {
                if (window.posthog && typeof window.posthog.flush === "function") {
                  window.posthog.flush();
                }
              } catch (error) {
                console.warn("PostHog flush failed", error);
              }

              await wait(delayMs);
            }
            """,
            delay_ms,
        )
    except Exception as exc:
        print(f"[Analytics {label}] Flush wait skipped: {exc}")


def read_analytics_state(page):
    return page.evaluate(
        """
        () => ({
          url: window.location.href,
          title: document.title,
          userAgent: navigator.userAgent,
          webdriver: navigator.webdriver,
          hasPostHog: Boolean(window.posthog),
          posthogLoaded: Boolean(window.posthog && window.posthog.__loaded),
          hasGtag: typeof window.gtag === "function",
          dataLayerLength: Array.isArray(window.dataLayer) ? window.dataLayer.length : null
        })
        """
    )
