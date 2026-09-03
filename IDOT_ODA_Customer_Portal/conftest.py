import base64
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

from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Customer_Portal.pages.login.create_an_account_page import CreateAnAccountPage
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage

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
    """
    Cleans up stale lock files and old Allure results on the master process
    before worker processes are spawned.
    """
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

        # Clean old allure-results so only current test run results appear
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
    PARALLEL AUTH WITH SEQUENTIAL LOCKING:
    Each worker has its own unique user state file. A cross-process file lock
    ensures physical logins are performed sequentially to prevent database locks
    and server-side timeouts on the staging environment.
    """
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    state_file = AUTH_DIR / f"user_state_{worker_id}.json"

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

        logger.info(f"Worker {worker_id} performing fresh physical login to {state_file.name}...")
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

        email = _get_valid_env("IDOT_EMAIL") or valid_user.get("email", "sprabhu@bemsys.com")
        password = _get_valid_env("IDOT_PASSWORD") or valid_user.get("password", "Security@#")
        pin = _get_valid_env("IDOT_PIN") or valid_user.get("pin", "11")

        login_page.navigate_to_login()
        login_page.login(email=email, password=password)
        login_page.fill_pin_if_prompted(pin=pin)

        try:
            page.wait_for_url("**/Portal/Page/Index/**", timeout=30000, wait_until="domcontentloaded")
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
    Standard Playwright page fixture.
    Starts Playwright tracing and saves trace ZIP file ONLY if the test fails.
    """
    test_name = request.node.name.replace("[", "_").replace("]", "_")
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.zip"

    # Remove old trace for this test
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
def authenticated_page(browser: Browser, browser_context_args, auth_storage, request) -> Page:
    """
    Pre-authenticated Playwright page fixture.
    Reuses storage state and performs self-healing login if session expired.
    Conditionally saves trace and screenshots only upon failure.
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
    if "Account" in page.url and ("Login" in page.url or page.locator("button:has-text('Login')").count() > 0):
        logger.info(f"Session expired for worker {worker_id}. Performing self-healing re-login...")
        login_page = LoginPage(page)
        login_data_file = TESTDATA_DIR / "login_data.json"
        valid_user = {}
        if login_data_file.exists():
            try:
                data = json.loads(login_data_file.read_text(encoding="utf-8"))
                valid_user = data.get("valid_credentials", {})
            except Exception:
                pass

        email = _get_valid_env("IDOT_EMAIL") or valid_user.get("email", "sprabhu@bemsys.com")
        password = _get_valid_env("IDOT_PASSWORD") or valid_user.get("password", "Security@#")
        pin = _get_valid_env("IDOT_PIN") or valid_user.get("pin", "11")

        login_page.login(email=email, password=password)
        login_page.fill_pin_if_prompted(pin=pin)
        try:
            page.wait_for_url("**/Portal/Page/Index/**", timeout=30000, wait_until="domcontentloaded")
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
    context.close()


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Fixture providing an initialized LoginPage object instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def create_account_page(page: Page) -> CreateAnAccountPage:
    """Fixture providing an initialized CreateAnAccountPage object instance."""
    return CreateAnAccountPage(page)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to capture failure screenshots and attach them
    along with trace links to pytest-html and Allure reports.
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)

    pytest_html = item.config.pluginmanager.getplugin("html")
    if report.when == "call" and report.failed:
        test_name = item.name.replace("[", "_").replace("]", "_")
        worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
        screenshot_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.png"
        trace_rel_path = f"debug_artifacts/{test_name}_{worker_id}.zip"

        page: Page = item.funcargs.get("page") or item.funcargs.get("authenticated_page")
        extra = getattr(report, "extra", [])

        if page:
            try:
                screenshot_bytes = page.screenshot(full_page=True)
                screenshot_path.write_bytes(screenshot_bytes)
                logger.error(f"Captured failure screenshot: {screenshot_path}")

                if pytest_html:
                    screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                    extra.append(pytest_html.extras.png(screenshot_base64, name="Failure Screenshot"))
                    extra.append(pytest_html.extras.url(trace_rel_path, name="🔍 View Full Trace (ZIP)"))
            except Exception as e:
                logger.error(f"Failed to capture failure screenshot: {e}")

        # Optional RAG AI Failure Diagnostics Hook
        if os.getenv("ENABLE_RAG_DIAGNOSTICS", "false").strip().lower() in {"1", "true", "yes"}:
            try:
                from utils.rag_engine import QARagEngine
                rag = QARagEngine(PARENT_DIR)
                if rag.is_available():
                    page_url = page.url if page else "Unknown"
                    failure_trace = str(report.longrepr)
                    analysis = rag.analyze_failure(item.name, failure_trace, page_url=page_url)
                    logger.info(f"[RAG DIAGNOSTIC] {analysis}")
                    if pytest_html:
                        extra.append(pytest_html.extras.text(analysis, name="AI RAG Failure Diagnosis"))
            except Exception as rag_err:
                logger.debug(f"RAG Diagnostic Note: {rag_err}")

        report.extra = extra


def pytest_html_report_title(report):
    """Customizes the title of the generated HTML report."""
    report.title = f"IDOT ODA Customer Portal Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"


def pytest_sessionfinish(session, exitstatus):
    """
    Cleans debug artifacts if passed, and auto-generates static Allure HTML report.
    """
    if not hasattr(session.config, "workerinput") and not getattr(session.config.option, "collectonly", False):
        # Clean debug artifacts on success if requested
        if exitstatus == 0 and CLEAN_DEBUG_ARTIFACTS:
            if DEBUG_ARTIFACTS_DIR.exists():
                for item in DEBUG_ARTIFACTS_DIR.iterdir():
                    if item.is_file():
                        try:
                            item.unlink()
                        except Exception:
                            pass

        # Generate Allure Report
        try:
            env = os.environ.copy()
            local_jdk = r"C:\Users\Mohan(QAQC)\jdk-21"
            local_allure = r"C:\Users\Mohan(QAQC)\allure-2.45.0\bin"
            if os.path.exists(local_jdk):
                env["JAVA_HOME"] = local_jdk
            if os.path.exists(local_allure):
                env["PATH"] = f"{local_jdk}\\bin;{local_allure};" + env.get("PATH", "")

            res = subprocess.run(
                "allure generate reports/allure-results -o reports/allure-report --clean",
                shell=True,
                env=env,
                capture_output=True,
            )
            if res.returncode == 0:
                print("\n[ALLURE AUTO-GENERATE] Generated HTML report at: reports/allure-report/index.html")
                is_ci = os.getenv("CI") or os.getenv("TF_BUILD") or os.getenv("AZURE_HTTP_USER_AGENT")
                auto_open = os.getenv("AUTO_OPEN_ALLURE", "true").strip().lower() in {"1", "true", "yes"}
                if not is_ci and auto_open:
                    subprocess.Popen("allure open reports/allure-report", shell=True, env=env)
                    print("[ALLURE AUTO-OPEN] Opened interactive Allure report in browser.")
        except Exception as e:
            print(f"\n[ALLURE AUTO-GENERATE NOTE] {e}")
