import pytest
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Browser, Page
from utils.config import Config
from pages.login.login_page import LoginPage

# Create .auth directory if it doesn't exist
AUTH_DIR = Path(".auth")
AUTH_DIR.mkdir(exist_ok=True)
STATE_FILE = AUTH_DIR / "user_state.json"

def pytest_configure(config):
    """
    Cleans up old lock file on the master process before worker processes are spawned.
    """
    if not hasattr(config, "workerinput"):
        lock_file = Path(".pytest_cache/session.lock")
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass

@pytest.fixture(scope="session")
def auth_storage(browser, browser_context_args, tmp_path_factory):
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
        with open(Config.PROJECT_ROOT / "testdata" / "login_data.json") as f:
            valid_user = json.load(f)["valid_users"][0]
        login_page.load(Config.LOGIN_URL)
        login_page.login(email=valid_user["email"], password=valid_user["password"], pin="11")
        
        # Use 'domcontentloaded' to avoid server load hang
        page.wait_for_url("**/Home/Dashboard**", timeout=60000, wait_until="domcontentloaded")
        
        context.storage_state(path=str(STATE_FILE))
        page.close()
        context.close()
        return STATE_FILE

    # --- CROSS-WORKER SYNCHRONIZATION (Native Python) ---
    if os.getenv("PYTEST_XDIST_WORKER"):
        # We use a native 'Exclusive Creation' lock (works on Windows/Linux)
        # This ensures only ONE worker can create the lock file.
        lock_acquired = False
        try:
            # O_CREAT | O_EXCL will fail if the file already exists
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            lock_acquired = True
            print(f"\n[LOCK] Worker {os.getenv('PYTEST_XDIST_WORKER')} acquired the master lock.")
        except FileExistsError:
            # Another worker already has the lock
            pass

        if lock_acquired:
            try:
                # We are the master! Perform login and save state.
                return perform_fresh_login()
            finally:
                # Optional: keep the lock for the whole session or delete it
                pass
        else:
            # We are a secondary worker - wait for the state file to appear
            print(f"\n[LOCK] Worker {os.getenv('PYTEST_XDIST_WORKER')} waiting for session state...")
            import time
            timeout = 120 # 2 minute wait for slow staging login
            start_time = time.time()
            while not STATE_FILE.exists() or STATE_FILE.stat().st_size == 0:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Timed out waiting for master worker to create session state.")
                time.sleep(2)
            
            # Use small buffer to ensure file writing is finished
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
    
    # Check if this is the HTML report generation phase
    pytest_html = item.config.pluginmanager.getplugin("html")
    if rep.when == "call" and pytest_html:
        extra = getattr(rep, "extra", [])
        
        # We define the link logic here. 
        # Even if the file is saved 1 second later in teardown, the link will point to the correct path.
        test_name = item.name
        worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
        trace_rel_path = f"debug_artifacts/{test_name}_{worker_id}.zip"

        if rep.failed:
            # We add the link if the test failed. 
            # In the final HTML, this link will be clickable.
            extra.append(pytest_html.extras.url(trace_rel_path, name="🔍 View Full Trace (ZIP)"))
            
        rep.extra = extra

def pytest_html_report_title(report):
    report.title = f"Staff Portal Automation Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"


@pytest.fixture
def authenticated_page(browser, browser_context_args, auth_storage, request):
    """
    PROFESSIONAL FIXTURE:
    1. Reuses validated session state for speed.
    2. SELF-HEALING: If session is expired (redirected to Logout/Login), it performs a fresh login.
    3. Records a full TRACE only if the test fails.
    """
    # 1. Setup Unique Trace Path
    test_name = request.node.name
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    trace_dir = Path("reports/debug_artifacts")
    trace_dir.mkdir(parents=True, exist_ok=True)
    
    # ✅ FIXED FILE NAME (professional)
    trace_path = trace_dir / f"{test_name}_{worker_id}.zip"

    # ✅ DELETE ONLY SAME TEST FILE
    if trace_path.exists():
        trace_path.unlink()

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
    # If the app redirected us to the Logout page, we are NOT logged in.
    if "LogOutUser" in page.url or "Account/Login" in page.url:
        print(f"\n[SELF-HEALING] Session expired or invalid for Worker {worker_id}. Performing fresh login...")
        login_page = LoginPage(page)
        with open(Config.PROJECT_ROOT / "testdata" / "login_data.json") as f:
            valid_user = json.load(f)["valid_users"][0]
        
        login_page.login(email=valid_user["email"], password=valid_user["password"], pin="11")
        
        # Ensure we reach the dashboard
        page.wait_for_url("**/Home/Dashboard**", timeout=60000, wait_until="domcontentloaded")
        
        # Update the storage state for other tests to reuse
        context.storage_state(path=str(auth_storage))
    
    yield page
    
    # 4. Teardown & Conditional Trace Saving
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    try:
        if failed:
            context.tracing.stop(path=str(trace_path))
            print(f"\n[TRACE SAVED] Failure recorded: {trace_path}")
        else:
            context.tracing.stop()
    except Exception:
        context.tracing.stop()

    page.close()
    context.close()



