import pytest
import logging
import json
import os
import shutil
import time
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Browser, Page
from utils.config import Config
from pages.login.login_page import LoginPage

def _get_valid_env(key: str) -> str | None:
    val = os.getenv(key)
    if val and not ("example.com" in val.lower() or val.lower().startswith("your_")):
        return val
    return None


try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

HEADLESS = os.getenv("PW_HEADLESS", "true").strip().lower() in {"1", "true", "yes", "on"}
CLEAN_DEBUG_ARTIFACTS = os.getenv("CLEAN_DEBUG_ARTIFACTS", "false").strip().lower() in {"1", "true", "yes", "on"}

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
        
        email = _get_valid_env("STAFF_EMAIL") or valid_user["email"]
        password = _get_valid_env("STAFF_PASSWORD") or valid_user["password"]
        pin = _get_valid_env("STAFF_PIN") or valid_user.get("pin", "11")
        login_page.load(Config.LOGIN_URL)
        login_page.login(email=email, password=password, pin=pin)
        
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
            extra.append(pytest_html.extras.url(trace_rel_path, name="🔍 View Full Trace (ZIP)"))

            # ---------- RAG AI FAILURE DIAGNOSTICS (SAFE OPTIONAL HOOK) ----------
            if os.getenv("ENABLE_RAG_DIAGNOSTICS", "false").strip().lower() in {"1", "true", "yes"}:
                try:
                    from utils.rag_engine import QARagEngine
                    rag = QARagEngine(PROJECT_ROOT.parent)
                    if rag.is_available():
                        page = item.funcargs.get("page") or item.funcargs.get("authenticated_page")
                        page_url = page.url if page else "Unknown"
                        failure_trace = str(rep.longrepr)
                        analysis = rag.analyze_failure(item.name, failure_trace, page_url=page_url)
                        logging.info("[RAG DIAGNOSTIC] %s", analysis)
                        if pytest_html is not None:
                            extra.append(pytest_html.extras.text(analysis, name="AI RAG Failure Diagnosis"))
                except Exception as rag_err:
                    logging.debug("RAG Diagnostic Note: %s", rag_err)
            
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
        downloads_dir = Config.PROJECT_ROOT / "downloads"
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
                        downloads_dir = Config.PROJECT_ROOT / "downloads"
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
        
        email = _get_valid_env("STAFF_EMAIL") or valid_user["email"]
        password = _get_valid_env("STAFF_PASSWORD") or valid_user["password"]
        pin = _get_valid_env("STAFF_PIN") or valid_user.get("pin", "11")
        login_page.login(email=email, password=password, pin=pin)
        
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






