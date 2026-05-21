from playwright.sync_api import Page

class ApiCaptureHelper:
    """A highly reusable wrapper to intercept and validate background network traffic."""
    
    def __init__(self, page: Page):
        self.page = page
        self.responses = []
        self._listener_bound = False

    def start(self):
        """Activates network listening on the current page."""
        self.responses.clear()
        if not self._listener_bound:
            self.page.on("response", self._capture_response)
            self._listener_bound = True

    def _capture_response(self, response):
        """Internal callback hooked into Playwright network events."""
        self.responses.append(response)

    def wait_for_api_idle(self):
        """Allows trailing background APIs to fetch before calculating pass/fail."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass # Failsafe if networkidle doesn't achieve absolute 0 requests

    def stop(self):
        """Detaches network listening."""
        if self._listener_bound:
            self.page.remove_listener("response", self._capture_response)
            self._listener_bound = False

    def assert_all_responses_successful(self, ignored_domains=None):
        """Scans the captured traffic array and violently fails if any 4xx or 5xx errors occurred on internal APIS."""
        if ignored_domains is None:
            # We inherently ignore 3rd party analytic and helpdesk widgets that commonly block automation browsers
            ignored_domains = ["atlassian.com", "google-analytics.com", "googletagmanager.com"]
            
        failed_apis = []
        for r in self.responses:
            # Skip non-HTTP requests
            if not r.url.startswith("http"):
                continue
                
            # Skip manually ignored 3rd party domains
            if any(domain in r.url for domain in ignored_domains):
                continue
                
            # Trap any failed statuses
            # We ignore the known staging routing bug hitting /Account?Length=7
            if r.status >= 400 and not ("?Length=7" in r.url and r.status == 404):
                failed_apis.append(f"{r.request.method} | {r.url} | STATUS: {r.status}")
                
        if failed_apis:
            error_message = "CRITICAL: The following API requests failed during the flow:\n" + "\n".join(failed_apis)
            raise AssertionError(error_message)
