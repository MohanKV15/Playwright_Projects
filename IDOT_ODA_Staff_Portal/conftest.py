import base64
import json
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
import pytest
from playwright.sync_api import Browser, BrowserContext, Page

PROJECT_ROOT = Path(__file__).resolve().parent
PARENT_DIR = PROJECT_ROOT.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

# Load Environment Variables from subproject and root
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(PARENT_DIR / ".env")
except Exception:
    pass

from IDOT_ODA_Staff_Portal.utils.config import Config
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Staff_Portal.pages.dashboard.dashboard_page import DashboardPage
from IDOT_ODA_Staff_Portal.pages.add_paper_application import PrimaryHighwayPage, InterstateHighwayPage

logger = logging.getLogger(__name__)


def _get_valid_env(key: str) -> str | None:
    """Returns the environment variable value if defined and not a dummy placeholder."""
    val = os.getenv(key)
    if val and not ("example.com" in val.lower() or val.lower().startswith("your_")):
        return val
    return None


# Execution Flags & Directories
HEADLESS = os.getenv("PW_HEADLESS", "true").strip().lower() in {"1", "true", "yes", "on"}
CLEAN_DEBUG_ARTIFACTS = os.getenv("CLEAN_DEBUG_ARTIFACTS", "false").strip().lower() in {"1", "true", "yes", "on"}

AUTH_DIR = Config.PROJECT_ROOT / ".auth"
REPORTS_DIR = Config.PROJECT_ROOT / "reports"
DEBUG_ARTIFACTS_DIR = REPORTS_DIR / "debug_artifacts"
TESTDATA_DIR = Config.PROJECT_ROOT / "testdata"

# Ensure output and auth directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
AUTH_DIR.mkdir(parents=True, exist_ok=True)


def _add_zoom_script(page: Page) -> None:
    """Applies zoom script cleanly to body without layout distortion."""
    page.add_init_script(
        f"""
        (() => {{
            const applyZoom = () => {{
                if (document.body) {{
                    document.body.style.zoom = '{Config.ZOOM_PERCENT}%';
                }} else {{
                    setTimeout(applyZoom, 10);
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


def pytest_configure(config):
    """Cleans up stale lock files and old Allure results on the master process."""
    if not hasattr(config, "workerinput"):
        # Clean stale lock file in .auth
        if AUTH_DIR.exists():
            lock_file = AUTH_DIR / "login.lock"
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except Exception:
                    pass

        # Clean session lock
        cache_lock = PROJECT_ROOT / ".pytest_cache" / "session.lock"
        if cache_lock.exists():
            try:
                cache_lock.unlink()
            except Exception:
                pass

        # Clean old allure-results
        allure_results_dir = REPORTS_DIR / "allure-results"
        if allure_results_dir.exists():
            for item in allure_results_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception:
                    pass


@pytest.fixture(scope="session")
def browser_type_launch_options(pytestconfig):
    """Determines headless mode considering CLI --headed and PW_HEADLESS flag."""
    is_cli_headed = False
    try:
        is_cli_headed = pytestconfig.getoption("headed", False)
    except Exception:
        pass
    is_headless = not is_cli_headed and (os.getenv("PW_HEADLESS", "true").strip().lower() in {"1", "true", "yes", "on"})
    return {"headless": is_headless}


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Launches browser with maximized window args."""
    return {
        **browser_type_launch_args,
        "args": ["--start-maximized", "--window-size=1920,1080"],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Forces browser to use full available screen width without viewport clipping."""
    return {
        **browser_context_args,
        "viewport": None,
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def auth_storage(browser, browser_context_args):
    """
    Parallel Auth with Sequential Locking:
    Generates worker storage state and performs physical login.
    """
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    state_file = AUTH_DIR / f"staff_state_{worker_id}.json"

    if state_file.exists():
        return state_file

    match = re.search(r"\d+", worker_id)
    worker_idx = int(match.group()) if match else 0

    # Acquire cross-process lock to serialize physical logins
    lock_file = AUTH_DIR / "login.lock"
    while True:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            time.sleep(1.5)

    try:
        if state_file.exists():
            return state_file

        stagger_delay = worker_idx * 4
        if stagger_delay > 0:
            logger.info(f"Worker {worker_id} waiting {stagger_delay}s to stagger login load...")
            time.sleep(stagger_delay)

        logger.info(f"Worker {worker_id} performing physical Staff login to {state_file.name}...")
        context = browser.new_context(**browser_context_args)
        page = context.new_page()
        page.set_default_timeout(Config.TIMEOUT)
        _add_zoom_script(page)

        login_page = LoginPage(page)
        login_data_file = TESTDATA_DIR / "login_data.json"
        valid_user = {}
        if login_data_file.exists():
            try:
                data = json.loads(login_data_file.read_text(encoding="utf-8"))
                valid_user = data.get("valid_credentials", {})
            except Exception:
                pass

        email = _get_valid_env("STAFF_EMAIL") or _get_valid_env("IDOT_STAFF_EMAIL") or valid_user.get("email", "sprabhu@bemsys.com")
        password = _get_valid_env("STAFF_PASSWORD") or _get_valid_env("IDOT_STAFF_PASSWORD") or valid_user.get("password", "Security@#")
        pin = _get_valid_env("STAFF_PIN") or _get_valid_env("IDOT_STAFF_PIN") or valid_user.get("pin", "11")

        login_page.navigate_to_login()
        login_page.login(email=email, password=password, pin=pin)

        try:
            page.wait_for_selector("text=ADTrak", timeout=30000)
        except Exception:
            page.wait_for_timeout(3000)

        context.storage_state(path=str(state_file))
        page.close()
        context.close()
    finally:
        try:
            lock_file.unlink()
        except Exception:
            pass

    return state_file


@pytest.fixture(scope="function")
def page(context: BrowserContext, request) -> Page:
    """
    Standard Playwright page fixture with trace recording on failure only.
    """
    test_name = request.node.name.replace("[", "_").replace("]", "_")
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.zip"

    if trace_path.exists():
        try:
            trace_path.unlink()
        except Exception:
            pass

    # Start Playwright Tracing
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()
    page.set_default_timeout(Config.TIMEOUT)
    page.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    _add_zoom_script(page)

    yield page

    # Conditional Trace Saving (Only on Failure)
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            logger.info(f"Playwright trace saved on failure: {trace_path}")
            try:
                import allure
                allure.attach(
                    page.screenshot(full_page=True),
                    name=f"Failure_Screenshot_{test_name}",
                    attachment_type=allure.attachment_type.PNG,
                )
                if trace_path.exists():
                    allure.attach.file(
                        source=str(trace_path),
                        name=f"Playwright_Trace_{test_name}",
                        attachment_type="application/zip",
                    )
            except Exception as e:
                logger.debug(f"Allure attachment note: {e}")
        else:
            context.tracing.stop()
    except Exception:
        context.tracing.stop()

    page.close()


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Returns an initialized LoginPage instance for unauthenticated tests."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def staff_dashboard_page(page: Page) -> DashboardPage:
    """Returns an initialized DashboardPage instance (alias for backward compatibility)."""
    return DashboardPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page: Page) -> DashboardPage:
    """Returns an initialized DashboardPage instance."""
    return DashboardPage(page)


@pytest.fixture(scope="function")
def primary_highway_page(page: Page) -> PrimaryHighwayPage:
    """Returns an initialized PrimaryHighwayPage instance."""
    return PrimaryHighwayPage(page)


@pytest.fixture(scope="function")
def authenticated_staff_page(page: Page, login_page: LoginPage) -> Page:
    """Authenticates into the Staff Portal and returns the ready page."""
    login_data_file = TESTDATA_DIR / "login_data.json"
    valid_user = {}
    if login_data_file.exists():
        try:
            data = json.loads(login_data_file.read_text(encoding="utf-8"))
            valid_user = data.get("valid_credentials", {})
        except Exception:
            pass

    email = _get_valid_env("STAFF_EMAIL") or _get_valid_env("IDOT_STAFF_EMAIL") or valid_user.get("email", "sprabhu@bemsys.com")
    password = _get_valid_env("STAFF_PASSWORD") or _get_valid_env("IDOT_STAFF_PASSWORD") or valid_user.get("password", "Security@#")
    pin = _get_valid_env("STAFF_PIN") or _get_valid_env("IDOT_STAFF_PIN") or valid_user.get("pin", "11")

    login_page.navigate_to_login()
    login_page.login(email=email, password=password, pin=pin)
    return page


@pytest.fixture(scope="function")
def authenticated_dashboard(authenticated_staff_page: Page) -> DashboardPage:
    """Provides an authenticated DashboardPage on the Application/Permit Search view."""
    dash = DashboardPage(authenticated_staff_page)
    dash.navigate_to_search()
    return dash


@pytest.fixture(scope="function")
def authenticated_primary_highway(authenticated_staff_page: Page) -> PrimaryHighwayPage:
    """Provides an authenticated PrimaryHighwayPage."""
    return PrimaryHighwayPage(authenticated_staff_page)


@pytest.fixture(scope="function")
def interstate_highway_page(page: Page) -> InterstateHighwayPage:
    """Returns an initialized InterstateHighwayPage instance."""
    return InterstateHighwayPage(page)


@pytest.fixture(scope="function")
def authenticated_interstate_highway(authenticated_staff_page: Page) -> InterstateHighwayPage:
    """Provides an authenticated InterstateHighwayPage."""
    return InterstateHighwayPage(authenticated_staff_page)


@pytest.fixture(scope="function")
def authenticated_page(browser: Browser, browser_context_args, auth_storage, request) -> Page:
    """
    Pre-authenticated Playwright page fixture.
    Reuses staff storage state and performs self-healing login if needed.
    """
    test_name = request.node.name.replace("[", "_").replace("]", "_")
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.zip"

    if trace_path.exists():
        try:
            trace_path.unlink()
        except Exception:
            pass

    context = browser.new_context(
        **browser_context_args,
        storage_state=str(auth_storage) if auth_storage.exists() else None,
    )

    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()
    page.set_default_timeout(Config.TIMEOUT)
    page.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    _add_zoom_script(page)

    # Navigate to dashboard
    try:
        page.goto(Config.DASHBOARD_URL, timeout=Config.TIMEOUT, wait_until="domcontentloaded")
    except Exception:
        page.goto(Config.LOGIN_URL, timeout=Config.TIMEOUT, wait_until="domcontentloaded")

    # Self-healing login if redirected back to Login
    if "Accounts/Account" in page.url or page.locator("button:has-text('Login')").count() > 0:
        logger.info(f"Staff session expired for worker {worker_id}. Performing self-healing re-login...")
        login_page = LoginPage(page)
        login_data_file = TESTDATA_DIR / "login_data.json"
        valid_user = {}
        if login_data_file.exists():
            try:
                data = json.loads(login_data_file.read_text(encoding="utf-8"))
                valid_user = data.get("valid_credentials", {})
            except Exception:
                pass

        email = _get_valid_env("STAFF_EMAIL") or _get_valid_env("IDOT_STAFF_EMAIL") or valid_user.get("email", "sprabhu@bemsys.com")
        password = _get_valid_env("STAFF_PASSWORD") or _get_valid_env("IDOT_STAFF_PASSWORD") or valid_user.get("password", "Security@#")
        pin = _get_valid_env("STAFF_PIN") or _get_valid_env("IDOT_STAFF_PIN") or valid_user.get("pin", "11")

        login_page.login(email=email, password=password, pin=pin)
        try:
            page.wait_for_selector("text=ADTrak", timeout=30000)
        except Exception:
            page.wait_for_timeout(2000)
        context.storage_state(path=str(auth_storage))

    yield page

    # Conditional Trace Saving on Failure
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            logger.info(f"Playwright trace saved on failure: {trace_path}")
            try:
                import allure
                allure.attach(
                    page.screenshot(full_page=True),
                    name=f"Failure_Screenshot_{test_name}",
                    attachment_type=allure.attachment_type.PNG,
                )
                if trace_path.exists():
                    allure.attach.file(
                        source=str(trace_path),
                        name=f"Playwright_Trace_{test_name}",
                        attachment_type="application/zip",
                    )
            except Exception as e:
                logger.debug(f"Allure attachment note: {e}")
        else:
            context.tracing.stop()
    except Exception:
        context.tracing.stop()

    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attaches test outcome report to item for failure detection."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
