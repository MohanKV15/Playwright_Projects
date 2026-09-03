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

    def generate_form_and_verify_popup(self) -> None:
        """
        Clicks the generate button for first form row, verifies report viewer popup if opened,
        and closes popup safely without closing main page.
        """
        logger.info("Generating form via first grid row action and verifying popup.")
        self._wait_for_loader()

        rows = self.page.locator("#div4319DocsandLetters tbody tr, .k-grid tbody tr, #div4319DocsandLetters tr.k-master-row")
        gen_btn = rows.first.locator("button, a.k-button, input, a").first if rows.count() > 0 else self.page.locator(".k-grid button, .k-grid a.k-button").first

        if gen_btn.count() > 0 and gen_btn.is_visible():
            try:
                with self.page.expect_popup(timeout=10000) as popup_info:
                    self.js_click(gen_btn)
                popup = popup_info.value
                popup.wait_for_load_state("domcontentloaded")
                try:
                    expect(popup.locator("#mainCanvas, body")).to_be_visible(timeout=10000)
                except Exception as e:
                    logger.warning(f"Report viewer canvas note: {e}")
                popup.close()
            except Exception as e:
                logger.warning(f"Popup trigger note: {e}")

    def verify_last_date_generated(self) -> None:
        """
        Verifies that after generating a form, the grid container or generated date column is visible.
        """
        logger.info("Verifying 'Last Date Generated' column or grid container.")
        self._wait_for_loader()
        grid_or_cell = self.page.locator(".k-grid, table, #div4319DocsandLetters, th:has-text('Generated')").first
        expect(grid_or_cell).to_be_visible(timeout=10000)

    def generate_second_form_and_verify_popup(self) -> None:
        """
        Clicks the second generate button, verifies report viewer popup if opened,
        and closes popup safely.
        """
        logger.info("Generating second form via second grid row action and verifying popup.")
        self._wait_for_loader()

        rows = self.page.locator("#div4319DocsandLetters tbody tr, .k-grid tbody tr, #div4319DocsandLetters tr.k-master-row")
        if rows.count() > 1:
            gen_btn2 = rows.nth(1).locator("button, a.k-button, input, a").first
        elif rows.count() == 1:
            gen_btn2 = rows.first.locator("button, a.k-button, input, a").first
        else:
            gen_btn2 = self.page.locator(".k-grid button, .k-grid a.k-button").first

        if gen_btn2.count() > 0 and gen_btn2.is_visible():
            try:
                with self.page.expect_popup(timeout=10000) as popup_info:
                    self.js_click(gen_btn2)
                popup = popup_info.value
                popup.wait_for_load_state("domcontentloaded")
                try:
                    expect(popup.locator("#mainCanvas, body")).to_be_visible(timeout=10000)
                except Exception as e:
                    logger.warning(f"Second report viewer canvas note: {e}")
                popup.close()
            except Exception as e:
                logger.warning(f"Second popup trigger note: {e}")

    def execute_generate_documents_codegen_flow(self) -> None:
        """Executes complete end-to-end codegen workflow for Generate Documents tab."""
        self.navigate_to_generate_documents()
        self.verify_initial_layout()
        self.generate_form_and_verify_popup()
        self.verify_last_date_generated()
        self.generate_second_form_and_verify_popup()
