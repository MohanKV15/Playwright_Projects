import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import pytest
from playwright.sync_api import Browser, BrowserContext, Page

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

from utils.config import Config
from pages.login.login_page import LoginPage

logger = logging.getLogger(__name__)

# Register Page Object Fixtures
pytest_plugins = ["fixtures.page_fixtures"]

# Configuration & Directories
HEADLESS = os.getenv("PW_HEADLESS", "false").strip().lower() in {"1", "true", "yes", "on"}
CLEAN_DEBUG_ARTIFACTS = os.getenv("CLEAN_DEBUG_ARTIFACTS", "false").strip().lower() in {"1", "true", "yes", "on"}

AUTH_DIR = Config.AUTH_DIR
REPORTS_DIR = Config.REPORTS_DIR
DEBUG_ARTIFACTS_DIR = REPORTS_DIR / "debug_artifacts"

AUTH_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def _add_zoom_script(page: Page) -> None:
    """Applies zoom script cleanly to body without custom margin/width distortion."""
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
    """Cleans up stale lock files and previous Allure results before execution."""
    if not hasattr(config, "workerinput"):
        # Clean stale lock files
        if AUTH_DIR.exists():
            lock_file = AUTH_DIR / "login.lock"
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except Exception:
                    pass

        cache_lock = PROJECT_ROOT / ".pytest_cache" / "session.lock"
        if cache_lock.exists():
            try:
                cache_lock.unlink()
            except Exception:
                pass

        # Clean old allure results
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
    is_headless = not is_cli_headed and (os.getenv("PW_HEADLESS", "false").strip().lower() in {"1", "true", "yes", "on"})
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
def session_auth_state(browser: Browser, tmp_path_factory, worker_id: str) -> Path:
    """
    Session-level fixture that authenticates once and saves state to storage_state.json.
    Supports parallel workers (pytest-xdist) with file-based locking.
    """
    auth_file = AUTH_DIR / f"state_{worker_id}.json" if worker_id != "master" else AUTH_DIR / "state.json"
    lock_file = AUTH_DIR / "login.lock"

    # Acquire lock for worker synchronization
    while True:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            break
        except FileExistsError:
            time.sleep(0.5)

    try:
        if not auth_file.exists():
            logger.info("Initializing session authentication state for NCDOT...")
            context = browser.new_context(viewport=None, ignore_https_errors=True)
            page = context.new_page()
            _add_zoom_script(page)

            login_page = LoginPage(page)
            login_page.navigate_to_login()
            login_page.login(
                email=Config.DEFAULT_USER,
                password=Config.DEFAULT_PASSWORD,
                pin=Config.DEFAULT_PIN,
            )
            try:
                page.wait_for_url("**/Portal/Page/Index/**", timeout=35000, wait_until="domcontentloaded")
            except Exception:
                page.wait_for_timeout(3000)

            # Save storage state
            context.storage_state(path=str(auth_file))
            context.close()
            logger.info(f"Session authentication state saved to {auth_file}")
    finally:
        try:
            if lock_file.exists():
                lock_file.unlink()
        except Exception:
            pass

    return auth_file


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """
    Standard Playwright page fixture.
    Enforces screen zoom to 67% and maximized viewport for all test pages.
    """
    page = context.new_page()
    page.set_default_timeout(Config.TIMEOUT)
    page.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    _add_zoom_script(page)
    yield page
    page.close()


@pytest.fixture(scope="function")
def authenticated_page(browser: Browser, session_auth_state: Path, request) -> Page:
    """Fixture providing an isolated Page initialized with active login session and 67% zoom."""
    test_name = request.node.name.replace("[", "_").replace("]", "_")
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.zip"

    if trace_path.exists():
        try:
            trace_path.unlink()
        except Exception:
            pass

    context = browser.new_context(
        storage_state=str(session_auth_state),
        viewport=None,
        ignore_https_errors=True,
    )
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.set_default_timeout(Config.TIMEOUT)
    page.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    _add_zoom_script(page)

    try:
        page.goto(Config.PROJECTS_URL, timeout=Config.TIMEOUT, wait_until="domcontentloaded")
    except Exception:
        page.goto(Config.LOGIN_URL, timeout=Config.TIMEOUT, wait_until="domcontentloaded")

    # Self-healing if session expired
    if "Account" in page.url and ("Login" in page.url or page.locator("button:has-text('Login')").count() > 0):
        logger.info("Session expired for worker. Performing self-healing re-login...")
        login_page = LoginPage(page)
        login_page.login(email=Config.DEFAULT_USER, password=Config.DEFAULT_PASSWORD, pin=Config.DEFAULT_PIN)
        try:
            page.wait_for_url("**/Portal/Page/Index/**", timeout=30000, wait_until="domcontentloaded")
        except Exception:
            page.wait_for_timeout(2000)
        context.storage_state(path=str(session_auth_state))

    yield page

    # Conditional Screenshot and Trace capture on Failure before closing context
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            try:
                screenshot_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                import allure
                allure.attach.file(
                    str(screenshot_path),
                    name=f"Failure Screenshot ({test_name})",
                    attachment_type=allure.attachment_type.PNG,
                )
                if trace_path.exists():
                    allure.attach.file(
                        str(trace_path),
                        name=f"Playwright Trace ({test_name})",
                        attachment_type="application/zip",
                    )
            except Exception as e:
                logger.warning(f"Failure attachment note: {e}")
        else:
            context.tracing.stop()
    except Exception:
        context.tracing.stop()

    page.close()
    context.close()





@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_sessionfinish(session, exitstatus):
    """Automatically generates Allure HTML report at the conclusion of test run."""
    allure_results = REPORTS_DIR / "allure-results"
    allure_report = REPORTS_DIR / "allure-report"

    local_allure = r"C:\Users\Mohan(QAQC)\allure-2.45.0\bin"
    env = os.environ.copy()
    if os.path.exists(local_allure):
        env["PATH"] = f"{local_allure};" + env.get("PATH", "")

    try:
        subprocess.run(
            f"allure generate {allure_results} -o {allure_report} --clean",
            shell=True,
            env=env,
            capture_output=True,
            text=True,
        )
        print(f"\n[ALLURE AUTO-GENERATE] Generated HTML report at: {allure_report}/index.html")
    except Exception as e:
        print(f"\n[ALLURE AUTO-GENERATE NOTE] Could not generate Allure report: {e}")

