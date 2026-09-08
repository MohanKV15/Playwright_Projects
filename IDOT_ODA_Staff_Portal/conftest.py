"""
IDOT Outdoor Advertising Staff Portal - Pytest Configuration and Fixtures
Provides enterprise-grade browser configuration, parallel test worker state,
resilient authentication locking, and clean Page Object Model fixture bindings.
"""

import json
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Union

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

PROJECT_ROOT = Path(__file__).resolve().parent
PARENT_DIR = PROJECT_ROOT.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

# Load Environment Variables from subproject and workspace root
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(PARENT_DIR / ".env")
except Exception:
    pass

from IDOT_ODA_Staff_Portal.utils.config import Config

logger = logging.getLogger(__name__)

# Register dedicated Page Object and Workflow Fixtures plugin
pytest_plugins = ["IDOT_ODA_Staff_Portal.fixtures.page_fixtures"]




AUTH_DIR = Config.PROJECT_ROOT / ".auth"

REPORTS_DIR = Config.PROJECT_ROOT / "reports"
DEBUG_ARTIFACTS_DIR = REPORTS_DIR / "debug_artifacts"
TESTDATA_DIR = Config.PROJECT_ROOT / "testdata"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
AUTH_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------------------------
def _get_valid_env(key: str) -> Optional[str]:
    """Returns the environment variable value if set and not a placeholder."""
    val = os.getenv(key)
    if val and not ("example.com" in val.lower() or val.lower().startswith("your_")):
        return val
    return None


def _get_staff_credentials() -> Tuple[str, str, str]:
    """
    Resolves verified Staff Portal credentials.
    Priority:
    1. Environment variables (STAFF_EMAIL, STAFF_PASSWORD, STAFF_PIN)
    2. testdata/login_data.json valid_credentials
    """

    valid_user = {}
    login_data_file = TESTDATA_DIR / "login_data.json"
    if login_data_file.exists():
        try:
            data = json.loads(login_data_file.read_text(encoding="utf-8"))
            valid_user = data.get("valid_credentials", {})
        except Exception:
            pass

    email = (
        _get_valid_env("STAFF_EMAIL")
        or _get_valid_env("IDOT_STAFF_EMAIL")
        or valid_user.get("email")
    )
    password = (
        _get_valid_env("STAFF_PASSWORD")
        or _get_valid_env("IDOT_STAFF_PASSWORD")
        or valid_user.get("password")
    )
    pin = (
        _get_valid_env("STAFF_PIN")
        or _get_valid_env("IDOT_STAFF_PIN")
        or valid_user.get("pin", "11")
    )

    if not email or not password:
        raise ValueError(
            "Staff credentials not configured. Please define STAFF_EMAIL and STAFF_PASSWORD "
            "in your .env file or under 'valid_credentials' in testdata/login_data.json."
        )

    return email, password, pin



def _add_zoom_script(target: Union[Page, BrowserContext]) -> None:
    """Applies configured screen zoom cleanly without layout or viewport distortion."""
    target.add_init_script(
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


def _record_failure_diagnostics(
    context: BrowserContext,
    page: Page,
    request: pytest.FixtureRequest,
    trace_path: Path,
    test_name: str,
) -> None:
    """
    Saves Playwright zip traces, disk screenshots, and Allure evidence on test failure.
    Guarantees only the latest failure evidence is retained.
    """
    failed = (
        (hasattr(request.node, "rep_call") and request.node.rep_call.failed)
        or (hasattr(request.node, "rep_setup") and request.node.rep_setup.failed)
    )
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    screenshot_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}_failure.png"

    try:
        if failed:
            DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
            # 1. Stop and persist latest Playwright trace
            context.tracing.stop(path=str(trace_path))
            logger.info(f"Latest Playwright trace saved on failure: {trace_path}")

            # 2. Capture and persist latest failure screenshot to disk
            screenshot_bytes = None
            try:
                screenshot_bytes = page.screenshot(full_page=True, path=str(screenshot_path))
                logger.info(f"Latest failure screenshot saved: {screenshot_path}")
            except Exception as ss_err:
                logger.debug(f"Screenshot capture fallback: {ss_err}")

            # 3. Attach evidence to Allure report
            try:
                import allure
                if screenshot_bytes:
                    allure.attach(
                        screenshot_bytes,
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
                logger.debug(f"Allure attachment diagnostic note: {e}")
        else:
            # On pass: discard trace and remove any old failure artifacts for this test
            context.tracing.stop()
            if trace_path.exists():
                trace_path.unlink(missing_ok=True)
            if screenshot_path.exists():
                screenshot_path.unlink(missing_ok=True)
    except Exception:
        try:
            context.tracing.stop()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Pytest Hooks
# ---------------------------------------------------------------------------
def pytest_configure(config: pytest.Config) -> None:
    """Cleans up stale session locks, debug artifacts, and old Allure results on session start."""
    if not hasattr(config, "workerinput"):
        # Clean stale lock file in .auth
        lock_file = AUTH_DIR / "login.lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass

        # Clean pytest-cache session lock
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

        # Clean old debug_artifacts so previous session artifacts never bleed through
        if DEBUG_ARTIFACTS_DIR.exists():
            for item in DEBUG_ARTIFACTS_DIR.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                except Exception:
                    pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """
    Attaches test outcome report to item for failure detection and
    embeds trace links and failure screenshots into pytest-html report.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    pytest_html = item.config.pluginmanager.getplugin("html")
    if rep.when == "call" and pytest_html:
        extra = getattr(rep, "extra", [])
        if rep.failed:
            test_name = item.name.replace("[", "_").replace("]", "_")
            worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
            trace_rel_path = f"debug_artifacts/{test_name}_{worker_id}.zip"
            extra.append(pytest_html.extras.url(trace_rel_path, name="🔍 View Latest Trace (ZIP)"))

            screenshot_file = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}_failure.png"
            if screenshot_file.exists():
                extra.append(pytest_html.extras.image(str(screenshot_file), name="📸 Failure Screenshot"))
        rep.extra = extra


def pytest_html_report_title(report) -> None:
    """Sets a clean, professional title for the pytest-html report."""
    report.title = f"IDOT ODA Staff Portal Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """
    Automatically compiles static Allure HTML report at the conclusion of the test session.
    Matches the automated reporting hook implemented across NJDOT portals.
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
                "allure generate reports/allure-results -o reports/allure-report --clean",
                shell=True,
                env=env,
                capture_output=True,
            )
            if res.returncode == 0:
                logger.info("[ALLURE AUTO-GENERATE] Generated static HTML report at reports/allure-report/index.html")
        except Exception as e:
            logger.debug(f"Allure auto-generation note: {e}")

# Browser & Context Configuration Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def browser_type_launch_options(pytestconfig: pytest.Config) -> dict:
    """Determines headless mode considering CLI --headed and PW_HEADLESS flag."""
    is_cli_headed = False
    try:
        is_cli_headed = pytestconfig.getoption("headed", False)
    except Exception:
        pass
    is_headless = not is_cli_headed and (
        os.getenv("PW_HEADLESS", "true").strip().lower() in {"1", "true", "yes", "on"}
    )
    return {"headless": is_headless}


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    """Launches browser with maximized window args."""
    return {
        **browser_type_launch_args,
        "args": ["--start-maximized", "--window-size=1920,1080"],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Forces browser to use full available screen width without viewport clipping."""
    return {
        **browser_context_args,
        "viewport": None,
        "ignore_https_errors": True,
    }


@pytest.fixture(autouse=True)
def configure_zoom(context: BrowserContext) -> None:
    """
    Applies configured screen zoom cleanly across the entire browser context,
    ensuring all pages, popups, and frames inherit zoom automatically.
    """
    _add_zoom_script(context)



# ---------------------------------------------------------------------------
# Core Playwright Page Fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Page:
    """
    Standard Playwright page fixture with tracing, zoom initialization,
    and automatic failure diagnostics (screenshots + traces attached to Allure).
    """
    test_name = request.node.name.replace("[", "_").replace("]", "_")
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_path = DEBUG_ARTIFACTS_DIR / f"{test_name}_{worker_id}.zip"

    if DEBUG_ARTIFACTS_DIR.exists():
        for old_file in DEBUG_ARTIFACTS_DIR.glob(f"{test_name}*"):
            try:
                old_file.unlink()
            except Exception:
                pass


    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()
    page.set_default_timeout(Config.TIMEOUT)
    page.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    _add_zoom_script(page)

    yield page

    _record_failure_diagnostics(context, page, request, trace_path, test_name)
    page.close()



