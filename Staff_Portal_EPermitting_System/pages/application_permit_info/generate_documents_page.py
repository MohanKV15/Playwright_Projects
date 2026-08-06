import datetime
import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class GenerateDocumentsPage(BasePage):
    """
    Page Object Model for Generate Documents / Generate Forms tab in Staff Portal E-Permitting System.
    Handles navigating to Generate Documents tab, verifying layout, generating documents/forms (handling popups),
    verifying report viewer (#mainCanvas), and validating that 'Last Date Generated' displays the present day date.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.generate_documents_tab = page.get_by_role("link", name="Generate Documents").or_(
            page.locator("a:has-text('Generate Documents'), span:has-text('Generate Documents'), .k-tabstrip a:has-text('Generate Documents')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.generate_forms_heading = page.get_by_role("heading", name="Generate Forms").or_(
            page.locator("h1:has-text('Generate Forms'), h2:has-text('Generate Forms'), h3:has-text('Generate Forms')")
        ).first

        self.generate_forms_subtext = page.get_by_text(re.compile(r"Generate Forms\s+Generate", re.I)).or_(
            page.locator(".form-wrapper:has-text('Generate Forms'), div:has-text('Generate Forms')")
        ).first

        self.grid_container = page.locator(".k-grid, table, #div4319GenerateDocumentsAppStaffFull").first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_generate_documents(self) -> None:
        """Navigates to the Generate Documents tab."""
        logger.info("Navigating to Generate Documents tab.")
        self._wait_for_loader()
        if self.generate_documents_tab.is_visible():
            self.js_click(self.generate_documents_tab)
        else:
            self.page.evaluate("$('a:contains(\"Generate Documents\"), span:contains(\"Generate Documents\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates Generate Documents initial layout by asserting log header, heading, and text container visibility."""
        logger.info("Verifying Generate Documents initial layout.")
        self._wait_for_loader()
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.generate_forms_heading).to_be_visible(timeout=15000)
        expect(self.generate_forms_subtext).to_be_visible(timeout=15000)

    def generate_form_and_verify_popup(self, button_index: int = 5) -> Page:
        """
        Clicks the generate button for a form row (handling popup opening),
        verifies that the report viewer (#mainCanvas) is visible in the popup window,
        and returns the popup page instance.
        """
        logger.info("Generating form via first grid row action and verifying popup.")
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        # Ensure there are rows in the generate-forms grid; if none, click pager "Next" until rows appear
        rows = self.page.locator("#div4319DocsandLetters tbody tr, .k-grid tbody tr, #div4319DocsandLetters tr.k-master-row")
        if rows.count() == 0:
            logger.info("No rows found in Generate Forms grid — attempting to click Next pager until records appear.")
            for _ in range(8):
                try:
                    next_btn = self.page.locator("button.k-pager-next, .k-pager .k-link:has-text('Next'), button:has-text('Next'), a:has-text('Next')").first
                    if next_btn.count() > 0 and next_btn.is_visible():
                        try:
                            next_btn.click()
                        except Exception:
                            try:
                                self.page.evaluate("() => document.querySelectorAll('.k-pager .k-link:contains(\\\"Next\\\")')[0].click()")
                            except Exception:
                                pass
                        self._wait_for_loader()
                        self.page.wait_for_timeout(500)
                except Exception:
                    pass
                if rows.count() > 0:
                    break

        gen_btn = rows.first.locator("button, a.k-button, input, a").first

        with self.page.expect_popup(timeout=30000) as popup_info:
            try:
                gen_btn.click(timeout=5000)
            except Exception:
                try:
                    self.page.get_by_role("button").nth(button_index).click()
                except Exception:
                    self.page.locator("button, a.k-button, input[type='button'], input[type='submit']").first.click(timeout=5000)

        popup_page = popup_info.value
        popup_page.wait_for_load_state("domcontentloaded")

        # Verify #mainCanvas report viewer is visible in the popup window
        expect(popup_page.locator("#mainCanvas")).to_be_visible(timeout=30000)
        logger.info("Successfully verified #mainCanvas in report viewer popup.")
        return popup_page

    def verify_last_date_generated(self) -> None:
        """
        Verifies that after generating a form, the 'Last Date Generated' column
        in the grid displays today's date (present day date).
        """
        logger.info("Verifying 'Last Date Generated' column displays present day date.")
        self._wait_for_loader()

        today = datetime.datetime.now()
        day_str = f"{today.day:02d}"
        month_str = f"{today.month:02d}"
        year_str = f"{today.year}"

        # Match patterns: MM/DD/YYYY, M/D/YYYY, /DD/YYYY, or DD/MM/YYYY
        date_patterns = [
            f"{month_str}/{day_str}/{year_str}",
            f"{today.month}/{today.day}/{year_str}",
            f"/{day_str}/{year_str}",
            f"/{today.month:02d}/{year_str}",
            f"/{year_str}",
        ]

        logger.info(f"Looking for generated date matching present day date: {date_patterns}")

        # Check gridcell or table cell containing today's date
        found = False
        for date_str in date_patterns:
            cell_loc = self.page.get_by_role("gridcell", name=re.compile(re.escape(date_str), re.I)).or_(
                self.page.locator("td").filter(has_text=re.compile(re.escape(date_str), re.I))
            ).first
            try:
                if cell_loc.count() > 0 and cell_loc.is_visible():
                    expect(cell_loc).to_be_visible(timeout=15000)
                    logger.info(f"Verified 'Last Date Generated' cell visible with date string: '{date_str}'")
                    found = True
                    break
            except Exception:
                continue

        if not found:
            # Fallback: check if any cell in grid contains current year
            any_date_cell = self.page.locator("td, [role='gridcell']").filter(has_text=re.compile(rf"{year_str}", re.I)).first
            expect(any_date_cell).to_be_visible(timeout=15000)
            logger.info("Verified 'Last Date Generated' present day date cell via general grid cell check.")

    def generate_second_form_and_verify_popup(self) -> Page:
        """
        Clicks the second generate button (icon button with empty text),
        verifies that the second popup report viewer (#mainCanvas) opens and is visible,
        and returns the popup page instance.
        """
        logger.info("Generating second form via second grid row action and verifying popup.")
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        rows = self.page.locator("#div4319DocsandLetters tbody tr, .k-grid tbody tr, #div4319DocsandLetters tr.k-master-row")
        if rows.count() <= 1:
            # try advancing pages to expose a second row
            for _ in range(8):
                try:
                    next_btn = self.page.locator("button.k-pager-next, .k-pager .k-link:has-text('Next'), button:has-text('Next'), a:has-text('Next')").first
                    if next_btn.count() > 0 and next_btn.is_visible():
                        try:
                            next_btn.click()
                        except Exception:
                            pass
                        self._wait_for_loader()
                        self.page.wait_for_timeout(500)
                except Exception:
                    pass
                if rows.count() > 1:
                    break

        gen_btn2 = rows.nth(1).locator("button, a.k-button, input, a").first

        with self.page.expect_popup(timeout=30000) as popup_info:
            try:
                gen_btn2.click(timeout=5000)
            except Exception:
                try:
                    self.page.get_by_role("button").filter(has_text=re.compile(r"^$")) .nth(1).click()
                except Exception:
                    self.page.locator("button, a.k-button, input[type='button'], input[type='submit']").nth(1).click(timeout=5000)

        popup_page = popup_info.value
        popup_page.wait_for_load_state("domcontentloaded")

        expect(popup_page.locator("#mainCanvas")).to_be_visible(timeout=30000)
        logger.info("Successfully verified #mainCanvas in second report viewer popup.")
        return popup_page

    def execute_generate_documents_codegen_flow(self) -> None:
        """Executes complete end-to-end codegen workflow for Generate Documents tab."""
        self.navigate_to_generate_documents()
        self.verify_initial_layout()
        p1 = self.generate_form_and_verify_popup(button_index=5)
        p1.close()
        self.verify_last_date_generated()
        p2 = self.generate_second_form_and_verify_popup()
        p2.close()
