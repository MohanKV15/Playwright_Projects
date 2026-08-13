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
from NJDOT_EPermitting_System.core.base_page import BasePage
from uuid import uuid4


def pytest_configure(config):
    """
    Cleans up old lock and user state files on the master process
    before worker processes are spawned, ensuring fresh logins.
    """
    if not hasattr(config, "workerinput"):
        lock_file = PROJECT_ROOT / ".pytest_cache" / "session.lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass
        
        if AUTH_STATE_PATH.exists():
            try:
                AUTH_STATE_PATH.unlink()
            except Exception:
                pass


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
    
    # We use a single shared auth state path
    auth_state_path = AUTH_STATE_PATH

    # Create a project-level lock file
    root_tmp_dir = PROJECT_ROOT / ".pytest_cache"
    root_tmp_dir.mkdir(exist_ok=True)
    lock_file = root_tmp_dir / "session.lock"

    def perform_fresh_login():
        print(f"\n[AUTH] Worker {os.getenv('PYTEST_XDIST_WORKER', 'gw0')} performing fresh physical login...")
        context = _build_context(shared_browser)
        page = context.new_page()
        _add_zoom_script(page)

        login_page = LoginPage(page)
        login_page.goto(credentials["url"])
        login_page.login(email, password)
        login_page.wait_for_dashboard(timeout=30000)

        context.storage_state(path=str(auth_state_path))
        context.close()
        return auth_state_path

    # --- CROSS-WORKER SYNCHRONIZATION (Native Python) ---
    if os.getenv("PYTEST_XDIST_WORKER"):
        lock_acquired = False
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            lock_acquired = True
            print(f"\n[LOCK] Worker {os.getenv('PYTEST_XDIST_WORKER')} acquired the master lock.")
        except FileExistsError:
            pass

        if lock_acquired:
            try:
                perform_fresh_login()
                return str(auth_state_path)
            finally:
                pass
        else:
            print(f"\n[LOCK] Worker {os.getenv('PYTEST_XDIST_WORKER')} waiting for session state...")
            import time
            timeout = 120
            start_time = time.time()
            while not auth_state_path.exists() or auth_state_path.stat().st_size == 0:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Timed out waiting for master worker to create session state.")
                time.sleep(2)
            time.sleep(1)
            return str(auth_state_path)
    else:
        # Standard serial execution
        if auth_state_path.exists() and auth_state_path.stat().st_size > 0:
            return str(auth_state_path)
        perform_fresh_login()
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

    # Try navigating to the dashboard URL first with retries to handle transient lag spikes.
    for attempt in range(2):
        try:
            page.goto(BasePage.DASHBOARD_URL, timeout=45000, wait_until="domcontentloaded")
            break
        except Exception as e:
            if attempt == 1:
                raise e
            print(f"\n[WARNING] Attempt {attempt+1} to load dashboard failed. Retrying in worker {worker_id}...")
            page.wait_for_timeout(2000)
    
    login_page = LoginPage(page)
    try:
        # Wait up to 5 seconds to see if the login email input or button becomes visible
        page.locator("#Email, #btnAccountLogin").first.wait_for(state="visible", timeout=5000)
    except Exception:
        pass

    if login_page.email_input.is_visible():
        print(f"\n[SELF-HEALING] Session expired or invalid for Worker {worker_id}. Performing fresh login...")
        credentials = json.loads(TEST_DATA_PATH.read_text(encoding="utf-8"))["professional"]
        email = os.getenv("NJHT_EMAIL") or credentials.get("email")
        password = os.getenv("NJHT_PASSWORD") or credentials.get("password")
        
        login_page.goto(credentials["url"])
        login_page.login(email, password)
        login_page.wait_for_dashboard(timeout=30000)
        
        # Update the storage state
        context.storage_state(path=auth_storage_state_path)

    yield page

    # ---------- TRACE SAVE ----------
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            print(f"[TRACE SAVED] {trace_path}")
            try:
                import allure
                allure.attach(
                    page.screenshot(full_page=True),
                    name=f"Failure_Screenshot_{test_name}",
                    attachment_type=allure.attachment_type.PNG
                )
                if trace_path.exists():
                    allure.attach.file(
                        source=str(trace_path),
                        name=f"Playwright_Trace_{test_name}",
                        attachment_type="application/zip"
                    )
            except Exception as e:
                print(f"[ALLURE ATTACH NOTE] {e}")
        else:
            context.tracing.stop()
    except Exception:
        context.tracing.stop()

    context.close()


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


def pytest_sessionfinish(session, exitstatus):
    """
    Automatically generates static Allure HTML report at the end of test session.
    Bypasses opening interactive GUI server if running in CI/CD environment.
    """
    if not hasattr(session.config, "workerinput"):
        import subprocess
        try:
            env = os.environ.copy()
            local_jdk = r"C:\Users\Mohan(QAQC)\jdk-21"
            local_allure = r"C:\Users\Mohan(QAQC)\allure-2.45.0\bin"
            if os.path.exists(local_jdk):
                env["JAVA_HOME"] = local_jdk
            if os.path.exists(local_allure):
                env["PATH"] = f"{local_jdk}\\bin;{local_allure};" + env.get("PATH", "")

            res = subprocess.run(
                'allure generate reports/allure-results -o reports/allure-report --clean',
                shell=True,
                env=env,
                capture_output=True
            )
            if res.returncode == 0:
                print("\n[ALLURE AUTO-GENERATE] Generated HTML report at: reports/allure-report/index.html")
                is_ci = os.getenv("CI") or os.getenv("TF_BUILD") or os.getenv("AZURE_HTTP_USER_AGENT")
                auto_open = os.getenv("AUTO_OPEN_ALLURE", "false").strip().lower() in {"1", "true", "yes"}
                if not is_ci and auto_open:
                    subprocess.Popen('allure open reports/allure-report', shell=True, env=env)
                    print("[ALLURE AUTO-OPEN] Opened interactive Allure report in browser.")
        except Exception as e:
            print(f"\n[ALLURE AUTO-GENERATE NOTE] {e}")
