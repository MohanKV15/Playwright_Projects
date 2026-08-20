from NJDOT_EPermitting_System.config import PROJECT_ROOT
from pathlib import Path
import os

from playwright.sync_api import expect

from NJDOT_EPermitting_System.api_validation.api_helper import ApiCaptureHelper
from NJDOT_EPermitting_System.pages.login import LoginPage
from NJDOT_EPermitting_System.utils.json_reader import load_json


TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
data = load_json(str(TEST_DATA_PATH))


def test_login_page_api_validation(page):
    """Example UI test that enables API capture without touching the existing framework."""

    api_capture = ApiCaptureHelper(page)
    api_capture.start()

    try:
        login_page = LoginPage(page)
        login_page.goto(data["professional"]["url"])
        email = data["professional"]["email"]
        password = data["professional"]["password"]
        login_page.login(
            email,
            password,
        )

        login_page.wait_for_dashboard(timeout=20000)

        api_capture.wait_for_api_idle()
        api_capture.assert_all_responses_successful(
            expected_statuses_by_url={
                "*Account*": (200, 302),
            }
        )
    finally:
        api_capture.stop()            