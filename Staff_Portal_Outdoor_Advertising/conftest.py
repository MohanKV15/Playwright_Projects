import pytest
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Browser, Page
from utils.config import Config
from pages.login.login_page import LoginPage

# Create .auth directory if it doesn't exist
AUTH_DIR = Path(".auth")
AUTH_DIR.mkdir(exist_ok=True)

def pytest_configure(config):
    """
    Cleans up stale lock files on the master process
    before worker processes are spawned.
    """
    if not hasattr(config, "workerinput"):
        # Clean up lock file if exists
        if AUTH_DIR.exists():
            lock_file = AUTH_DIR / "login.lock"
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except Exception:
                    pass
        
        lock_file = Path(".pytest_cache/session.lock")
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass

@pytest.fixture(scope="session")
def auth_storage(browser, browser_context_args):
    """
    PROFESSIONAL PARALLEL AUTH WITH SEQUENTIAL LOCKING:
    Each worker has its own unique user state file. A cross-process file lock
    ensures physical logins are performed sequentially to prevent database locks
    and server-side timeouts on the slow staging environment.
    """
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    state_file = AUTH_DIR / f"user_state_{worker_id}.json"
    
    if state_file.exists():
        return state_file

    # Extract worker index to add staggered delay
    match = re.search(r"\d+", worker_id)
    worker_idx = int(match.group()) if match else 0
    
    # 1. Acquire cross-process lock to serialize physical logins
    lock_file = AUTH_DIR / "login.lock"
    while True:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            time.sleep(1.5)

    try:
        # Check again under lock in case another worker already created it
        if state_file.exists():
            return state_file
            
        # Add staggered delay to distribute login load on staging server
        stagger_delay = worker_idx * 6
        if stagger_delay > 0:
            print(f"\n[AUTH] Worker {worker_id} waiting {stagger_delay}s to stagger login load...")
            time.sleep(stagger_delay)
            
        print(f"\n[AUTH] Worker {worker_id} performing fresh physical login to {state_file.name}...")
        context = browser.new_context(**browser_context_args)
        page = context.new_page()
        page.set_default_timeout(Config.TIMEOUT)
        login_page = LoginPage(page)
        with open(Config.PROJECT_ROOT / "testdata" / "login_data.json") as f:
            valid_user = json.load(f)["valid_users"][0]
        
        login_page.load(Config.LOGIN_URL)
        login_page.login(email=valid_user["email"], password=valid_user["password"], pin="11")
        
        # Wait for dynamic post-login dashboard
        page.wait_for_url("**/Portal/Page/Index/**", timeout=60000, wait_until="domcontentloaded")
        
        context.storage_state(path=str(state_file))
        page.close()
        context.close()
    finally:
        # Release lock
        try:
            lock_file.unlink()
        except Exception:
            pass
            
    return state_file



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
    clean_test_name = test_name.split("[")[0]
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
    
    # Register global download handler
    def handle_download(download):
        from pathlib import Path
        downloads_dir = Path("c:/Users/Mohan(QAQC)/PlaywrightProjects/Staff_Portal_Outdoor_Advertising/downloads")
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        filename = download.suggested_filename
        filename = f"{clean_test_name}_{filename}"
        dest_path = downloads_dir / filename
        
        if dest_path.exists():
            try:
                dest_path.unlink()
            except Exception:
                pass
        
        try:
            download.save_as(str(dest_path))
            print(f"\n[DOWNLOAD SAVED] {filename} saved to downloads directory.")
        except Exception as e:
            print(f"\n[DOWNLOAD ERROR] Failed to save {filename}: {e}")

    context.on("download", handle_download)
    
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
    page.set_default_timeout(Config.TIMEOUT)
    
    # Register global popup listener to capture inline PDF preview downloads
    def handle_popup(popup_page):
        def check_url(url):
            if not url or url == "about:blank":
                return
            is_doc_or_pdf = "documentview" in url.lower() or ".pdf" in url.lower() or "report" in url.lower() or "download" in url.lower()
            if is_doc_or_pdf:
                try:
                    document_id_match = re.search(r"document_id=(\d+)", url, re.I)
                    if document_id_match:
                        filename = f"document_{document_id_match.group(1)}.pdf"
                    else:
                        filename = url.split("/")[-1].split("?")[0] or "report.pdf"
                        if not filename.lower().endswith(".pdf") and "." not in filename:
                            filename += ".pdf"
                            
                    filename = re.sub(r"[^\w\-_\.]", "_", filename)
                    filename = f"{clean_test_name}_{filename}"
                    
                    response = context.request.get(url)
                    if response.ok:
                        from pathlib import Path
                        downloads_dir = Path("c:/Users/Mohan(QAQC)/PlaywrightProjects/Staff_Portal_Outdoor_Advertising/downloads")
                        downloads_dir.mkdir(parents=True, exist_ok=True)
                        dest_path = downloads_dir / filename
                        
                        if dest_path.exists():
                            try:
                                dest_path.unlink()
                            except Exception:
                                pass
                        
                        dest_path.write_bytes(response.body())
                        print(f"\n[POPUP PDF SAVED] {filename} saved to downloads directory.")
                except Exception as e:
                    print(f"\n[POPUP PDF ERROR] Failed to save popup PDF: {e}")

        # Check immediate URL
        check_url(popup_page.url)
        
        def on_frame_navigated(frame):
            if frame == popup_page.main_frame:
                check_url(frame.url)

        popup_page.on("framenavigated", on_frame_navigated)

    page.on("popup", handle_popup)

    
    # Stagger dashboard load requests to avoid overloading the server when tests start in parallel
    match = re.search(r"\d+", worker_id)
    worker_idx = int(match.group()) if match else 0
    stagger_delay = worker_idx * 4  # e.g., gw0: 0s, gw1: 4s, gw2: 8s, gw3: 12s
    if stagger_delay > 0:
        time.sleep(stagger_delay)
        
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
        page.wait_for_url("**/Portal/Page/Index/**", timeout=60000, wait_until="domcontentloaded")
        
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






