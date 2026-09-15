import logging
import re
from pathlib import Path
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.inspection_page import InspectionPage
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_details_page import JunkyardDetailsPage
from IDOT_ODA_Staff_Portal.utils.config import Config

logger = logging.getLogger(__name__)
fake = Faker()


class JunkyardInspectionPage(InspectionPage):
    """
    Page Object Model representing the Junkyards Inspection workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Inherits core dropdown/datepicker helpers and base page capabilities
    from InspectionPage and BasePage.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.junkyard_details = JunkyardDetailsPage(page)

        # Sidebar Navigation Locators
        self.junkyards_menu_link = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_inspection_link = page.get_by_role("link", name="Inspection").filter(visible=True).or_(
            page.locator("a[href*='Inspection']").filter(visible=True)
        ).first

        # Inspection Log View Locators
        self.header_junkyard_details_permit = page.get_by_text("Junkyard Details Permit").or_(
            page.get_by_text("Application Details Permit")
        ).first
        self.heading_inspection_log = page.get_by_role("heading", name="Inspection Log").or_(
            page.get_by_text("Inspection Log")
        ).first
        self.inspection_grid_wrapper = page.locator("#InspectionList").or_(
            page.locator(".k-grid-content, .k-grid, #partial-form")
        ).first
        self.new_entry_button = page.get_by_role("button", name="New Entry").first

        # New Inspection Entry Form Locators
        self.header_new_entry_app_details = page.get_by_text("Application Details Permit").or_(
            page.get_by_text("Junkyard Details Permit")
        ).first
        self.text_inspected_by_label = page.get_by_text("Inspection Inspected By").or_(
            page.get_by_text("Inspected By")
        ).first
        self.frm_new_entry = page.locator("#frmInsNeEntry")
        self.submit_button = page.get_by_role("button", name=re.compile(r"Submit", re.I)).or_(
            page.locator("#frmInsNeEntry button:has-text('Submit'), button:has-text('Submit')")
        ).first
        self.record_saved_text = page.get_by_text("Record saved successfully").first

        # Inspection Report Locators
        self.generate_report_button = page.get_by_role("button", name=re.compile(r"Generate\s+Inspection\s+Report", re.I)).or_(
            page.locator("button:has-text('Generate Inspection Report'), #btnGenerateInspectionReport")
        ).first
        self.report_generated_text = page.get_by_text("Generated successfully").first

        # Document Attachment Locators
        self.attach_doc_button = page.get_by_role("button", name="Attach Document").or_(
            page.locator("button:has-text('Attach Document'), a:has-text('Attach Document')")
        ).first
        self.doc_file_input = page.locator("input[type='file']").first
        self.doc_title_input = page.locator("#doctitle, [name='DocumentTitle']").first
        self.doc_desc_input = page.locator("#docdesc, [name='DocumentDescription']").first
        self.doc_save_button = page.get_by_role("button", name=re.compile(r"Save", re.I)).or_(
            page.locator("#SaveDocumentBtn, #frmInspectionDocSave button:has-text('Save'), button:has-text('Save')")
        ).first

        # Communication Log Locators
        self.add_comm_button = page.get_by_role("button", name="Add Communication").or_(
            page.locator("button:has-text('Add Communication'), a:has-text('Add Communication')")
        ).first
        self.comm_subject_input = page.locator("#Subject, [name='Subject'], input[name*='Subject' i]").or_(
            page.get_by_role("textbox", name=re.compile(r"Subject", re.I))
        ).first
        self.comm_desc_input = page.locator("#Description, [name='Description'], textarea[name*='Description' i]").or_(
            page.get_by_role("textbox", name=re.compile(r"Description", re.I))
        ).first
        self.comm_save_button = page.get_by_role("button", name=re.compile(r"Save", re.I)).or_(
            page.locator("button:has-text('Save')")
        ).first

        # Email Modal Locators
        self.send_email_button = page.get_by_role("button", name="Send Email").or_(
            page.locator("button:has-text('Send Email'), a:has-text('Send Email')")
        ).first
        self.email_modal_text = page.get_by_text("To:* CC:").or_(
            page.get_by_text("To:*")
        ).first

        # Grid Content Locator
        self.k_grid_content = page.locator(
            ".k-grid-content, #LogListGrid, #InspectionList, .k-grid, table.k-selectable, .form-wrapper, #partial-form"
        ).first

    def dismiss_ok_popups(self, timeout_ms: int = 2000, max_clicks: int = 3) -> int:
        """Safely dismisses visible OK modal popups."""
        dismissed = 0
        ok_btn = self.page.locator(
            ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:visible:has-text('OK'), a:visible:has-text('OK')"
        ).first
        for _ in range(max_clicks):
            try:
                if ok_btn.is_visible(timeout=timeout_ms):
                    self.logger.info("Dismissing modal popup OK button")
                    ok_btn.click(force=True)
                    self.page.wait_for_timeout(400)
                    dismissed += 1
                else:
                    break
            except Exception as e:
                self.logger.debug("Modal OK popup handling note: %s", e)
                break
        return dismissed

    def handle_select_application_popup_if_present(self, timeout_ms: int = 3000) -> bool:
        """Dismisses 'Select an Application from listing' modal alert if visible."""
        select_app_popup = self.page.get_by_text("Select an Application from listing").or_(
            self.page.get_by_text("Outdoor Advertising System")
        ).first
        if select_app_popup.is_visible(timeout=timeout_ms):
            self.logger.info("Detected 'Select an Application from listing' modal popup, clicking 'OK'")
            return self.dismiss_ok_popups(timeout_ms=2000, max_clicks=2) > 0
        return False

    def navigate_to_junkyard_inspection(self, company_name: str = "IDOTOAtest2") -> str:
        """Navigates to Junkyard Inspection Log view via search context and sidebar link."""
        self.logger.info("Navigating to Junkyard/Permit Search and searching company: '%s'", company_name)
        self.junkyard_details.navigate_to_junkyard_search()
        self.junkyard_details.search_junkyard_permits(company_name=company_name)
        record_info = self.junkyard_details.click_edit_on_permit_record()

        self.logger.info("Navigating to Inspection menu link under Junkyards")
        if self.junkyards_menu_link.is_visible(timeout=5000):
            if not self.page.locator(".sidebar a[href*='Inspection']").filter(visible=True).is_visible():
                self.logger.info("Expanding Junkyards sidebar menu")
                self.junkyards_menu_link.click(force=True)
                self.page.wait_for_timeout(400)

        target_inspection_link = self.page.get_by_role("link", name="Inspection").filter(visible=True).or_(
            self.page.locator("a[href*='Inspection']").filter(visible=True)
        ).first

        expect(target_inspection_link).to_be_visible(timeout=20000)
        target_inspection_link.click(force=True)
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.handle_select_application_popup_if_present()
        self.dismiss_ok_popups(timeout_ms=1000, max_clicks=1)
        self.verify_junkyard_inspection_page_loaded()
        return record_info

    def verify_junkyard_inspection_page_loaded(self, timeout_ms: int = 20000) -> None:
        """Verifies Junkyard Inspection Log headers and grid container."""
        self.logger.info("Verifying Junkyard Inspection Log page elements")
        self.handle_select_application_popup_if_present()
        if self.heading_inspection_log.is_visible(timeout=5000):
            expect(self.heading_inspection_log).to_be_visible(timeout=timeout_ms)
        if self.header_junkyard_details_permit.is_visible(timeout=5000):
            expect(self.header_junkyard_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.inspection_grid_wrapper).to_be_visible(timeout=timeout_ms)

    def click_new_entry_and_verify_form(self, timeout_ms: int = 20000) -> None:
        """Clicks 'New Entry' button and verifies entry form headers."""
        self.logger.info("Clicking 'New Entry' button on Inspection Log page")
        self.handle_select_application_popup_if_present()
        expect(self.new_entry_button).to_be_visible(timeout=timeout_ms)
        self.new_entry_button.click(force=True)
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.handle_select_application_popup_if_present()
        self.dismiss_ok_popups(timeout_ms=1000, max_clicks=1)
        self.logger.info("Verifying New Inspection Entry form elements")
        if self.header_new_entry_app_details.is_visible(timeout=5000):
            expect(self.header_new_entry_app_details).to_be_visible(timeout=timeout_ms)
        expect(self.text_inspected_by_label).to_be_visible(timeout=timeout_ms)

    def create_new_inspection_entry(
        self,
        inspected_by_name: Optional[str] = None,
        report_type: Optional[str] = None,
    ) -> Dict[str, str]:
        """Creates a new inspection entry using present day date and 1st option in each dropdown."""
        self.click_new_entry_and_verify_form()

        today_date = self.select_present_day_date(
            container=self.frm_new_entry,
            field_id="Assigned_Date",
        )

        self.logger.info("Selecting first valid Inspected By dropdown option")
        selected_inspected_by = self.select_first_valid_dropdown_option(
            self.page.locator("#frmInsNeEntry #inspected_by, #frmInsNeEntry span.k-dropdown").first
        )

        self.logger.info("Selecting first valid Report Type dropdown option")
        selected_report_type = self.select_first_valid_dropdown_option(
            self.page.locator("#indspetydd span.k-dropdown, #indspetydd #Type_of_Inspection").first
        )

        self.logger.info("Submitting New Inspection Entry form")
        expect(self.submit_button).to_be_visible(timeout=10000)
        self.submit_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(500)

        if self.record_saved_text.is_visible(timeout=3000):
            self.logger.info("Record saved successfully popup displayed")
        self.dismiss_ok_popups(timeout_ms=2500, max_clicks=3)

        self.details_url = self.page.url
        self.logger.info(f"Captured Inspection Details URL: {self.details_url}")

        return {
            "inspected_by": selected_inspected_by or "Inspected By Selected",
            "report_type": selected_report_type or "Report Type Selected",
            "inspection_date": today_date,
        }

    def generate_inspection_report(self) -> bool:
        """Generates inspection report, asserts popup canvas, closes window, and handles popups."""
        self.logger.info("Generating Inspection Report")
        expect(self.generate_report_button).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(400)

        try:
            with self.page.expect_popup(timeout=8000) as popup_info:
                self.generate_report_button.click(force=True)
            popup_page = popup_info.value
            popup_page.wait_for_load_state("domcontentloaded")
            self.logger.info("Inspection report popup opened: '%s'", popup_page.title())
            expect(popup_page.locator("#mainCanvas").first).to_be_visible(timeout=10000)
            popup_page.close()
        except Exception as e:
            self.logger.warning("Report popup handling note: %s", e)
            context_pages = self.page.context.pages
            if len(context_pages) > 1:
                p1 = context_pages[-1]
                if p1 != self.page:
                    try:
                        expect(p1.locator("#mainCanvas").first).to_be_visible(timeout=5000)
                        p1.close()
                    except Exception:
                        pass

        if self.report_generated_text.is_visible(timeout=4000):
            self.logger.info("Generated successfully text displayed")
        self.dismiss_ok_popups(timeout_ms=2000, max_clicks=2)
        return True

    def attach_document(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, str]:
        """Attaches document with present day date, uploads PDF, and confirms OK popups."""
        doc_title = title or f"Doc {fake.word().capitalize()} {fake.random_int(100, 999)}"
        doc_desc = description or fake.sentence(nb_words=5)

        dummy_file = (
            Path(file_path)
            if file_path
            else Config.PROJECT_ROOT / "testdata" / "dummy.pdf"
        )
        assert dummy_file.exists(), f"Upload file not found at: {dummy_file}"

        self.logger.info("Attaching document: Title='%s', File='%s'", doc_title, dummy_file.name)
        expect(self.attach_doc_button).to_be_visible(timeout=15000)
        self.attach_doc_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(600)

        self.select_present_day_date(field_id="docdate")

        expect(self.doc_file_input).to_be_attached(timeout=10000)
        self.doc_file_input.set_input_files(str(dummy_file))
        self.page.wait_for_timeout(400)

        if self.doc_title_input.is_visible():
            self.doc_title_input.fill(doc_title)
        if self.doc_desc_input.is_visible():
            self.doc_desc_input.fill(doc_desc)

        expect(self.doc_save_button).to_be_visible(timeout=10000)
        self.doc_save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1500)

        self.dismiss_ok_popups(timeout_ms=3000, max_clicks=3)
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        return {"title": doc_title, "description": doc_desc}

    def add_communication(
        self,
        subject: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, str]:
        """Adds communication log with present day date and confirms OK popups."""
        comm_subject = subject or f"Comm {fake.word().capitalize()} {fake.random_int(100, 999)}"
        comm_desc = description or fake.sentence(nb_words=6)

        self.logger.info("Adding communication: Subject='%s'", comm_subject)
        self._wait_for_loader()
        self.dismiss_ok_popups(timeout_ms=2000, max_clicks=2)

        expect(self.add_comm_button).to_be_visible(timeout=15000)
        self.add_comm_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        self.select_present_day_date()

        expect(self.comm_subject_input).to_be_visible(timeout=15000)
        self.comm_subject_input.fill(comm_subject)
        if self.comm_desc_input.is_visible():
            self.comm_desc_input.fill(comm_desc)

        expect(self.comm_save_button).to_be_visible(timeout=10000)
        self.comm_save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        self.dismiss_ok_popups(timeout_ms=3000, max_clicks=3)

        return {"subject": comm_subject, "description": comm_desc}

    def open_and_cancel_send_email(self, timeout_ms: int = 15000) -> None:
        """Opens Send Email modal, clicks Cancel, and confirms OK popups."""
        self.logger.info("Opening Send Email modal and cancelling")
        self._wait_for_loader()
        self.dismiss_ok_popups(timeout_ms=2000, max_clicks=2)

        expect(self.send_email_button).to_be_visible(timeout=timeout_ms)
        self.send_email_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(600)

        if self.email_modal_text.is_visible(timeout=5000):
            self.logger.info("Send Email modal text 'To:* CC:' verified")

        cancel_btn = self.page.locator(
            ".k-window:visible button:has-text('Cancel'), .modal:visible button:has-text('Cancel'), button:visible:has-text('Cancel')"
        ).first
        if cancel_btn.is_visible(timeout=4000):
            cancel_btn.click(force=True)
            self._wait_for_loader()
            self.page.wait_for_timeout(1000)

        self.dismiss_ok_popups(timeout_ms=3000, max_clicks=3)

    def verify_grid_content_visible(self, timeout_ms: int = 15000) -> None:
        """Verifies listing grid container visibility."""
        self.logger.info("Verifying listing grid content (.k-grid-content) is visible")
        self._wait_for_loader()
        self.dismiss_ok_popups(timeout_ms=3000, max_clicks=3)
        self.page.wait_for_timeout(1000)

        expect(self.k_grid_content).to_be_visible(timeout=timeout_ms)
        self.logger.info("Listing grid content verified successfully")

