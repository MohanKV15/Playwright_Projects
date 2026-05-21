import sys
import os
import json
import logging
import base64
# from datetime import datetime
from pathlib import Path
from playwright.sync_api import Browser


import pytest

try:
    from pytest_html import extras as html_extras
except ImportError:
    html_extras = None


ZOOM_PERCENT = 75
HEADLESS = os.getenv("PW_HEADLESS", "false").strip().lower() in {"1", "true", "yes", "on"}
CLEAN_DEBUG_ARTIFACTS = os.getenv("CLEAN_DEBUG_ARTIFACTS", "false").strip().lower() in {"1", "true", "yes", "on"}

PROJECT_ROOT = Path(__file__).resolve().parent
PARENT_DIR = PROJECT_ROOT.parent
DEBUG_ARTIFACTS_DIR = PROJECT_ROOT / "reports" / "debug_artifacts"
AUTH_DIR = PROJECT_ROOT / ".auth"
AUTH_STATE_PATH = AUTH_DIR / "auth_state.json"
TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"

if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from NJDOT_EPermitting_System.pages.login import LoginPage
from NJDOT_EPermitting_System.pages.submit_application.permit_major_page import PermitMajorPage
from uuid import uuid4


def _cleanup_debug_artifacts() -> None:
    if not DEBUG_ARTIFACTS_DIR.exists():
        return

    removed_count = 0
    for path in DEBUG_ARTIFACTS_DIR.iterdir():
        if path.is_file():
            path.unlink(missing_ok=True)
            removed_count += 1

    if removed_count:
        logging.info("Removed %s debug artifact file(s) after successful test run.", removed_count)


def _ensure_debug_artifacts_dir() -> None:
    DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def _build_context(browser, storage_state: str | None = None):
    context_kwargs = {
        "viewport": {"width": 1366, "height": 768},
        "ignore_https_errors": True,
    }
    if storage_state:
        context_kwargs["storage_state"] = storage_state
    return browser.new_context(**context_kwargs)


class _LocatorWrapper:
    """Wrap a Playwright Locator to add safe waits before common actions.

    This reduces flakiness by waiting for visibility before click/fill/press.
    """
    def __init__(self, locator, visible_timeout: int = 20000):
        self._locator = locator
        self._visible_timeout = visible_timeout

    def _ensure_visible(self):
        try:
            self._locator.wait_for(state="visible", timeout=self._visible_timeout)
        except Exception:
            pass

    def click(self, *args, **kwargs):
        self._ensure_visible()
        return self._locator.click(*args, **kwargs)

    def fill(self, *args, **kwargs):
        self._ensure_visible()
        return self._locator.fill(*args, **kwargs)

    def press(self, *args, **kwargs):
        self._ensure_visible()
        return self._locator.press(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(self._locator, item)



def _add_zoom_script(page) -> None:
    page.add_init_script(
        f"""
        (() => {{
            const applyZoom = () => {{
                if (document.body) {{
                    document.body.style.zoom = '{ZOOM_PERCENT}%';
                    document.body.style.transformOrigin = 'top left';
                }}
            }};

            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', applyZoom, {{ once: true }});
            }} else {{
                applyZoom();
            }}

            window.addEventListener('load', applyZoom);
        }})();
        """
    )


@pytest.fixture(scope="session")
def shared_browser(playwright):
    """Launch a single browser instance for the test session to avoid repeated
    browser startup costs. Tests still create fresh contexts for isolation.
    """
    browser = playwright.chromium.launch(headless=HEADLESS)
    yield browser
    try:
        browser.close()
    except Exception:
        pass

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    _ = call  # ✅ Fix Pylance warning (professional way)

    outcome = yield
    rep = outcome.get_result()

    extras = list(getattr(rep, "extras", []))

    if rep.when == "call" and rep.failed:
        _ensure_debug_artifacts_dir()

        page = item.funcargs.get("page") or item.funcargs.get("authenticated_page")

        test_name = item.name
        worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")

        # ---------- SCREENSHOT (REPLACE SAME FILE) ----------
        screenshot_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.png"

        # Remove only this test's old screenshot
        if screenshot_path.exists():
            screenshot_path.unlink()

        try:
            if page:
                screenshot_bytes = page.screenshot(timeout=10000)
                screenshot_path.write_bytes(screenshot_bytes)

                logging.error("Test failed. Screenshot saved to %s", screenshot_path)

                if html_extras is not None:
                    extras.append(html_extras.text(item.nodeid, name="Failed Test"))
                    extras.append(html_extras.text(page.url, name="Failed Page URL"))

                    screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                    extras.append(html_extras.png(screenshot_base64, name="Failure Screenshot"))
                    extras.append(html_extras.text(str(screenshot_path), name="Failure Screenshot Path"))

        except Exception as ex:
            logging.error("Screenshot capture failed: %s", ex)

    rep.extras = extras


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 0 and CLEAN_DEBUG_ARTIFACTS:
        _cleanup_debug_artifacts()


@pytest.fixture(scope="session")
def auth_storage_state_path(playwright, shared_browser):
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    credentials = json.loads(TEST_DATA_PATH.read_text(encoding="utf-8"))["professional"]
    email = os.getenv("NJHT_EMAIL") or credentials.get("email")
    password = os.getenv("NJHT_PASSWORD") or credentials.get("password")
    # Use a worker-specific storage_state file when running under xdist so
    # parallel workers do not trample a single shared file.
    worker = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    auth_state_path = AUTH_DIR / f"auth_state_{worker}.json"

    context = _build_context(shared_browser)
    page = context.new_page()
    _add_zoom_script(page)

    login_page = LoginPage(page)
    login_page.goto(credentials["url"])
    login_page.login(email, password)
    login_page.wait_for_dashboard(timeout=30000)

    context.storage_state(path=str(auth_state_path))
    context.close()
    # keep browser lifecycle to other fixtures; do not close here to allow reuse

    return str(auth_state_path)

@pytest.fixture(scope="function")
def page(shared_browser):
    # Create a fresh context from a shared browser for unauthenticated tests
    context = _build_context(shared_browser)

    page = context.new_page()
    _add_zoom_script(page)



    yield page
    context.close()


@pytest.fixture(scope="function")
def authenticated_page(shared_browser: Browser, request, auth_storage_state_path):
    context = _build_context(shared_browser, storage_state=auth_storage_state_path)

    # ---------- TRACE SETUP ----------
    test_name = request.node.name
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")

    trace_dir = Path("reports/debug_artifacts")
    trace_dir.mkdir(parents=True, exist_ok=True)

    # ✅ FIXED FILE NAME (professional)
    trace_path = trace_dir / f"{test_name}_{worker_id}.zip"

    # ✅ DELETE ONLY SAME TEST FILE
    if trace_path.exists():
        trace_path.unlink()

    # ---------- START TRACE ----------
    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )

    page = context.new_page()
    _add_zoom_script(page)

    # LOGIN is now handled by storage_state in the context.
    # The `ensure_clean_dashboard` fixture will handle navigation to the dashboard.

    yield page

    # ---------- TRACE SAVE ----------
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            print(f"[TRACE SAVED] {trace_path}")
        else:
            context.tracing.stop()
    except Exception:
        context.tracing.stop()

    context.close()
# @pytest.fixture(scope="function")
# def authenticated_page(shared_browser, request):
#     context = _build_context(shared_browser)

#     from pathlib import Path
#     import time
#     import os

#     # ---------- TRACE SETUP ----------
#     test_name = request.node.name
#     worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")

#     trace_dir = Path("reports/debug_artifacts")
#     trace_dir.mkdir(parents=True, exist_ok=True)

#     # Remove old trace for same test
#     for old_file in trace_dir.glob(f"{test_name}_*.zip"):
#         try:
#             old_file.unlink()
#         except Exception:
#             pass

#     timestamp = int(time.time())
#     trace_path = trace_dir / f"{test_name}_{worker_id}_{timestamp}.zip"

#     # ---------- START TRACE ----------
#     context.tracing.start(
#         screenshots=True,
#         snapshots=True,
#         sources=True
#     )

#     page = context.new_page()
#     _add_zoom_script(page)

#     # ---------- LOGIN ----------
#     credentials = json.loads(TEST_DATA_PATH.read_text(encoding="utf-8"))["professional"]

#     email = os.getenv("NJHT_EMAIL") or credentials.get("email")
#     password = os.getenv("NJHT_PASSWORD") or credentials.get("password")

#     login_page = LoginPage(page)
#     login_page.goto(credentials["url"])
#     login_page.login(email, password)
#     login_page.wait_for_dashboard(timeout=30000)

#     yield page

#     # ---------- STOP TRACE ----------
#     try:
#         if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
#             context.tracing.stop(path=str(trace_path))
#         else:
#             context.tracing.stop()
#     except Exception:
#         context.tracing.stop()

#     context.close()    
# @pytest.fixture(scope="function")
# def authenticated_page(shared_browser, request):
#     context = _build_context(shared_browser)

#     from pathlib import Path

#     # ---------- TRACE SETUP ----------
#     test_name = request.node.name
#     trace_dir = Path("reports/debug_artifacts")
#     trace_dir.mkdir(parents=True, exist_ok=True)
#     trace_path = trace_dir / f"{test_name}.zip"

#     # ---------- START TRACE ----------
#     context.tracing.start(
#         screenshots=True,
#         snapshots=True,
#         sources=True
#     )

#     page = context.new_page()
#     _add_zoom_script(page)

#     # ---------- LOGIN ----------
#     credentials = json.loads(TEST_DATA_PATH.read_text(encoding="utf-8"))["professional"]

#     email = os.getenv("NJHT_EMAIL") or credentials.get("email")
#     password = os.getenv("NJHT_PASSWORD") or credentials.get("password")

#     login_page = LoginPage(page)
#     login_page.goto(credentials["url"])
#     login_page.login(email, password)
#     login_page.wait_for_dashboard(timeout=30000)

#     yield page

#     # ---------- SAFE TRACE STOP ----------
#     try:
#         failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

#         if failed:
#             context.tracing.stop(path=str(trace_path))
#             print(f"❌ Trace saved: {trace_path}")
#         else:
#             context.tracing.stop()

#     except Exception as e:
#         print(f"❌ Trace error: {e}")

#     context.close()

@pytest.fixture(scope="function")
def unique_test_id():
    """Return a short unique id for use in creating test data."""
    return uuid4().hex

# Ensure each test that requires an authenticated page starts from a known dashboard state.
@pytest.fixture(autouse=True)
def ensure_clean_dashboard(request):
    """Navigate to dashboard and ensure Submit Application entry is visible before
    tests that request the `authenticated_page` fixture. This avoids forcing
    authentication for validation tests that should run unauthenticated.
    """
    # Only run dashboard setup for tests explicitly marked as `authenticated`.
    if request.node.get_closest_marker("authenticated") is None:
        yield
        return

    authenticated_page = request.getfixturevalue("authenticated_page")
    try:
        authenticated_page.goto(PermitMajorPage.DASHBOARD_URL, wait_until="commit")
        permit = PermitMajorPage(authenticated_page, script_name="ensure_clean_dashboard")
        permit.wait_for_dashboard_to_load()
    except Exception:
        # Best-effort: reload page and try once more.
        try:
            authenticated_page.reload()
            authenticated_page.goto(PermitMajorPage.DASHBOARD_URL, wait_until="commit")
            permit = PermitMajorPage(authenticated_page, script_name="ensure_clean_dashboard")
            permit.wait_for_dashboard_to_load()
        except Exception:
            # If dashboard cannot be reached, let the test proceed to fail with its own diagnostics.
            pass
    yield
