import pytest
import json
import os
import shutil
import base64
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Browser, Page
from pytest_html import extras
from utils.config import Config
from pages.login.login_page import LoginPage

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    load_dotenv(Path(__file__).resolve().parent.parent / ".env.example")
except Exception:
    pass

HEADLESS = os.getenv("PW_HEADLESS", "true").strip().lower() in {"1", "true", "yes", "on"}
CLEAN_DEBUG_ARTIFACTS = os.getenv("CLEAN_DEBUG_ARTIFACTS", "false").strip().lower() in {"1", "true", "yes", "on"}

# Create .auth directory if it doesn't exist
AUTH_DIR = Path(".auth")
AUTH_DIR.mkdir(exist_ok=True)
STATE_FILE = AUTH_DIR / "user_state.json"

def pytest_configure(config):
    """
    Cleans up old lock and user state files on the master process
    before worker processes are spawned, ensuring fresh logins.
    """
    if not hasattr(config, "workerinput"):
        lock_file = Path(".pytest_cache/session.lock")
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass
        
        state_file = Path(".auth/user_state.json")
        if state_file.exists():
            try:
                state_file.unlink()
            except Exception:
                pass

        # Clean old allure-results so only current test run results appear in Allure report
        allure_results_dir = Path("reports/allure-results")
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
    is_cli_headed = False
    try:
        is_cli_headed = pytestconfig.getoption("headed", False)
    except Exception:
        pass
    is_headless = not is_cli_headed and (os.getenv("PW_HEADLESS", "true").strip().lower() in {"1", "true", "yes", "on"})
    return {"headless": is_headless}

@pytest.fixture(scope="session")
def auth_storage(browser, browser_context_args):
    """
    PROFESSIONAL PARALLEL AUTH: 
    Uses a file-lock to ensure only ONE worker performs the login.
    All other workers wait and reuse the generated state.
    """
    # Create a project-level lock file
    root_tmp_dir = Path(os.path.abspath(".")).joinpath(".pytest_cache")
    root_tmp_dir.mkdir(exist_ok=True)
    lock_file = root_tmp_dir.joinpath("session.lock")

    def perform_fresh_login():
        print(f"\n[AUTH] Worker {os.getenv('PYTEST_XDIST_WORKER', 'gw0')} performing fresh physical login...")
        context = browser.new_context(**browser_context_args)
        page = context.new_page()
        login_page = LoginPage(page)
        
        login_data_path = Config.PROJECT_ROOT / "testdata" / "login_data.json"
        with open(login_data_path) as f:
            valid_user = json.load(f)["valid_users"][0]
            
        email = os.getenv("NJHT_EMAIL") or valid_user["email"]
        password = os.getenv("NJHT_PASSWORD") or valid_user["password"]
        login_page.load(Config.LOGIN_URL)
        login_page.login(email=email, password=password)
        
        # Wait for the main accounts portal link to become visible
        login_page.outdoor_advertising_link.wait_for(state="visible", timeout=Config.TIMEOUT)
        
        # Give the session cookies a moment to settle in the browser storage jar
        page.wait_for_timeout(2000)
        
        context.storage_state(path=str(STATE_FILE))
        page.close()
        context.close()
        return STATE_FILE

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
                return perform_fresh_login()
            finally:
                pass
        else:
            print(f"\n[LOCK] Worker {os.getenv('PYTEST_XDIST_WORKER')} waiting for session state...")
            import time
            timeout = 120
            start_time = time.time()
            while not STATE_FILE.exists() or STATE_FILE.stat().st_size == 0:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Timed out waiting for master worker to create session state.")
                time.sleep(2)
            time.sleep(1)
            return STATE_FILE
    else:
        # Standard serial execution
        if STATE_FILE.exists():
            return STATE_FILE
        return perform_fresh_login()

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": ["--start-maximized", "--window-size=1920,1080"]
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Forces the browser to use the full available screen width.
    """
    return {
        **browser_context_args,
        "viewport": None,      # Match the maximized window size
        "ignore_https_errors": True
    }

@pytest.fixture(autouse=True)
def configure_zoom(context):
    """
    Applies a professional 75% zoom - the 'Sweet Spot' for this application.
    """
    context.add_init_script("""
        const applyZoom = () => {
             if (document.body) { document.body.style.zoom = "75%"; }
             else { setTimeout(applyZoom, 10); }
        };
        applyZoom();
    """)
    yield

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    
    if rep.when == "call":
        report_extras = getattr(rep, "extras", [])
        
        test_name = item.name
        worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
        trace_path, screenshot_path, trace_rel_path, screenshot_rel_path = _get_artifact_paths(test_name, worker_id)

        if rep.failed:
            page = item.funcargs.get("authenticated_page") or item.funcargs.get("page")
            if page:
                try:
                    if screenshot_path.exists():
                        try:
                            screenshot_path.unlink()
                        except Exception:
                            pass
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    if screenshot_path.exists():
                        with open(screenshot_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                        # Embed base64 image in HTML using extras.png
                        report_extras.append(extras.png(encoded_string, name="Failure Screenshot"))
                        print(f"\n[REPORTING] Failure screenshot captured and embedded for {item.name}")
                except Exception as e:
                    print(f"\n[REPORTING] [ERROR] Failed to capture failure screenshot: {e}")

            # Add trace link on test failure
            report_extras.append(extras.url(trace_rel_path, name="🔍 View Full Trace (ZIP)"))
            
        rep.extras = report_extras

def pytest_html_report_title(report):
    report.title = f"Outdoor Advertising Automation Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

def _get_artifact_paths(test_name, worker_id):
    """
    Sanitizes test names to be safe Windows filenames and constructs consistent paths
    for failure screenshots and Playwright trace logs.
    """
    safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', test_name)
    trace_dir = Path("reports/debug_artifacts")
    trace_dir.mkdir(parents=True, exist_ok=True)
    trace_path = trace_dir / f"{safe_name}_{worker_id}.zip"
    screenshot_path = trace_dir / f"{safe_name}_{worker_id}.png"
    trace_rel_path = f"debug_artifacts/{safe_name}_{worker_id}.zip"
    screenshot_rel_path = f"debug_artifacts/{safe_name}_{worker_id}.png"
    return trace_path, screenshot_path, trace_rel_path, screenshot_rel_path

@pytest.fixture(autouse=True)
def setup_default_tracing(context, request):
    """
    For tests using the default 'page' fixture, this automatically manages
    trace cleanup and conditional trace saving on failure.
    """
    if "authenticated_page" in request.fixturenames or "page" not in request.fixturenames:
        yield
        return

    test_name = request.node.name
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_path, screenshot_path, trace_rel_path, screenshot_rel_path = _get_artifact_paths(test_name, worker_id)

    # Delete existing trace and screenshot files for this test at start of run
    if trace_path.exists():
        try:
            trace_path.unlink()
        except Exception:
            pass
    if screenshot_path.exists():
        try:
            screenshot_path.unlink()
        except Exception:
            pass

    # Start Tracing
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
    yield
    
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            print(f"\n[TRACE SAVED] Failure recorded: {trace_path}")
        else:
            context.tracing.stop()
    except Exception:
        try:
            context.tracing.stop()
        except Exception:
            pass

@pytest.fixture
def authenticated_page(browser, browser_context_args, auth_storage, request):
    """
    PROFESSIONAL FIXTURE:
    1. Reuses validated session state for speed.
    2. SELF-HEALING: If session is expired, it performs a fresh login.
    3. Records a full TRACE only if the test fails.
    """
    # 1. Setup Unique Trace Path & Clean Old Artifacts
    test_name = request.node.name
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_path, screenshot_path, trace_rel_path, screenshot_rel_path = _get_artifact_paths(test_name, worker_id)

    # Delete existing trace and screenshot files for this test at start of run
    if trace_path.exists():
        try:
            trace_path.unlink()
        except Exception:
            pass
    if screenshot_path.exists():
        try:
            screenshot_path.unlink()
        except Exception:
            pass

    # 2. Initialize Context with reuse
    context = browser.new_context(
        **browser_context_args,
        storage_state=str(auth_storage) if auth_storage.exists() else None
    )
    
    # 3. Start Tracing
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
    # Apply professional zoom
    context.add_init_script("""
        const applyZoom = () => {
             if (document.body) { document.body.style.zoom = "75%"; }
             else { setTimeout(applyZoom, 10); }
        };
        applyZoom();
    """)
    
    page = context.new_page()
    page.goto(Config.DASHBOARD_URL, timeout=Config.TIMEOUT, wait_until="domcontentloaded")
    
    # --- SELF-HEALING LOGIN LOGIC ---
    login_page = LoginPage(page)
    
    # Wait for either the dashboard link (indicating logged in) or the email field (indicating logged out)
    try:
        page.locator("a:has-text('Outdoor Advertising'), input[name='Email'], input[type='email']").first.wait_for(state="visible", timeout=15000)
    except Exception:
        pass

    # If the email input is visible, the session is invalid or expired, requiring a fresh login
    if login_page.email_input.is_visible():
        print(f"\n[SELF-HEALING] Session expired or invalid for Worker {worker_id}. Performing fresh login...")
        
        login_data_path = Config.PROJECT_ROOT / "testdata" / "login_data.json"
        with open(login_data_path) as f:
            valid_user = json.load(f)["valid_users"][0]
        
        email = os.getenv("NJHT_EMAIL") or valid_user["email"]
        password = os.getenv("NJHT_PASSWORD") or valid_user["password"]
        login_page.login(email=email, password=password)
        
        # Ensure we reach the accounts portal dashboard
        login_page.outdoor_advertising_link.wait_for(state="visible", timeout=Config.TIMEOUT)
        
        # Update storage state
        context.storage_state(path=str(auth_storage))
    
    # Automatically select and enter the Outdoor Advertising application module
    login_page.select_outdoor_advertising()
    
    yield page
    
    # 4. Teardown & Conditional Trace Saving
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            print(f"\n[TRACE SAVED] Failure recorded: {trace_path}")
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
        try:
            context.tracing.stop()
        except Exception:
            pass

    page.close()
    context.close()


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
                auto_open = os.getenv("AUTO_OPEN_ALLURE", "true").strip().lower() in {"1", "true", "yes"}
                if not is_ci and auto_open:
                    subprocess.Popen('allure open reports/allure-report', shell=True, env=env)
                    print("[ALLURE AUTO-OPEN] Opened interactive Allure report in browser.")
        except Exception as e:
            print(f"\n[ALLURE AUTO-GENERATE NOTE] {e}")
