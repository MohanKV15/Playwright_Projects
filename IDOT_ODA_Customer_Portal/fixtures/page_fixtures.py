"""
IDOT ODA Customer Portal - Page Object Model Fixtures
Provides decoupled dependency injection for customer portal pages.
"""

import pytest
from playwright.sync_api import Page
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Returns an initialized LoginPage instance."""
    return LoginPage(page)
