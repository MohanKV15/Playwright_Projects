import logging
import os
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage
from utils.config import Config

logger = logging.getLogger(__name__)
fake = Faker()


class OfferNegotiationsPage(ProjectBasePage):
    """
    Page Object Model representing NCDOT Parcel Central - Offer/Negotiations workflow:
      - Inherits Project search, login, Tabstrip navigation, and Parcel Central entry from ProjectBasePage.
      - Navigates to 'Offer/Negotiations' sub-menu via #navigationMenu2 sidebar menu.
      - Adds a new Negotiation record (Owner, Acquisition Agent, Status dropdowns via KendoDropdown) and saves.
      - Edits Offer Details (Recommendation dropdowns via KendoDropdown) and saves.
      - Offers Subtab: Adds new offer (Offer Type dropdown, date picker) and saves.
      - Admin Adjustment Subtab: Edits admin adjustment details (date picker) and saves.
      - Encumbrances Subtab: Adds new encumbrance (Type, Grantor, Grantee, Easement Type) and saves.
      - Recording Subtab: Adds new recording instrument (Instrument Type dropdown) and saves.
      - Documents Subtab: Navigates and verifies document container visibility.
      - Log Subtab: Performs Call Data, Notes, and Attachment operations using separated Kendo components.
      - Verifies clean state without errors across all subtabs.
    """

    # Subtab Constants
    TAB_OFFERS: str = "Offers"
    TAB_ADMIN_ADJUSTMENT: str = "Admin Adjustment"
    TAB_ENCUMBRANCES: str = "Encumbrances"
    TAB_RECORDING: str = "Recording"
    TAB_DOCUMENTS: str = "Documents"
    TAB_LOG: str = "Log"
    DEFAULT_SAMPLE_FILENAME: str = "dummy_sample.txt"

    def __init__(self, page: Page):
        super().__init__(page)

        # ---------------------------------------------------------------------
        # 1. Navigation & Content Containers
        # ---------------------------------------------------------------------
        self.offer_negotiations_nav_link = (
            page.locator("#navigationMenu2, #navigationMenu")
            .get_by_text("Offer/Negotiations", exact=True)
            .or_(page.locator("nav, ul, .k-panelbar").get_by_text("Offer/Negotiations", exact=True))
            .or_(page.get_by_text("Offer/Negotiations", exact=True))
        )
        self.landing_content_container = page.locator("#partialForm #partial-form, #partial-form")

        # ---------------------------------------------------------------------
        # 2. Add New Negotiation Modal Elements (#negotiationaddnew)
        # ---------------------------------------------------------------------
        self.add_new_negotiation_button = (
            page.locator("#btnNegotiationAddNew:visible, a#btnNegotiationAddNew:visible")
            .or_(page.get_by_role("button", name=re.compile(r"Add New", re.I)))
            .or_(page.locator("button:visible, a:visible").filter(has_text=re.compile(r"Add New", re.I)))
        )
        self.negotiation_modal = page.locator("#negotiationaddnew")
        self.owner_dropdown = page.locator(
            "#negotiationaddnew span.k-widget.k-dropdown:has(#owner_tenant), #negotiationaddnew span[aria-owns='owner_tenant_listbox'], #negotiationaddnew .k-dropdown"
        )
        self.agent_dropdown = page.locator(
            "#negotiationaddnew span.k-widget.k-dropdown:has(#negotiator), #negotiationaddnew span[aria-owns='negotiator_listbox']"
        )
        self.status_dropdown = page.locator(
            "#negotiationaddnew span.k-widget.k-dropdown:has(#status), #negotiationaddnew span[aria-owns='status_listbox']"
        )
        self.save_negotiation_button = page.locator(
            "#saveneg:visible, #negotiationaddnew button:has-text('Save'), button#saveneg"
        )
        self.cancel_negotiation_button = page.locator(
            "#cancelneg:visible, #negotiationaddnew button:has-text('Cancel')"
        )

        # ---------------------------------------------------------------------
        # 3. Offer Details Section (#RecommendationRB)
        # ---------------------------------------------------------------------
        self.edit_offer_details_button = page.locator(
            "#btnOfferDetailsEdit:visible, button#btnOfferDetailsEdit"
        )
        self.recommendation_container = page.locator("#RecommendationRB")
        self.recommendation_dropdown = page.locator(
            "#RecommendationRB span.k-widget.k-dropdown, #RecommendationRB .k-dropdown, span.k-widget.k-dropdown:has(#Recommendation)"
        )
        self.secondary_recommendation_dropdown = page.locator(
            "#RecommendationRB span.k-widget.k-dropdown"
        ).nth(1)
        self.save_offer_details_button = page.locator(
            "#savedetailsneg:visible, #RecommendationRB button:has-text('Save'), button#savedetailsneg"
        )

        # ---------------------------------------------------------------------
        # 4. TabStrip Component (#OfferNegotiationTab)
        # ---------------------------------------------------------------------
        self.offer_negotiation_tabs = page.locator("#OfferNegotiationTab")

        # ---------------------------------------------------------------------
        # 5. Offers Subtab Elements
        # ---------------------------------------------------------------------
        self.add_new_offer_button = page.locator(
            "#btnAddNewOffer:visible, button#btnAddNewOffer, button:visible:has-text('Add New')"
        )
        self.offer_type_dropdown = page.locator(
            "#divDisplayonAddnew span.k-widget.k-dropdown, #divDisplayonAddnew .k-dropdown"
        )
        self.offer_date_picker_button = page.locator(
            "#divDisplayonAddnew .k-datepicker button, #divDisplayonAddnew button:has(.k-i-calendar)"
        )
        self.save_offer_button = page.locator(
            "#ngnSave:visible, #divDisplayonAddnew button:has-text('Save'), button#ngnSave"
        )
        self.back_offer_button = page.locator(
            "#negOfferback:visible, button#negOfferback:visible, a#negOfferback:visible"
        )

        # ---------------------------------------------------------------------
        # 6. Admin Adjustment Subtab Elements
        # ---------------------------------------------------------------------
        self.edit_admin_form_button = page.locator(
            "#btnEditNegotiationAdminForm:visible, button#btnEditNegotiationAdminForm"
        )
        self.admin_date_picker_button = (
            page.locator("#partial-form .k-datepicker button, #partial-form button:has(.k-i-calendar)")
            .or_(page.locator("#partial-form").get_by_role("button", name="select"))
            .or_(page.get_by_role("button", name="select"))
        )
        self.save_admin_form_button = (
            page.locator("#btnSaveNegotiationAdmindetForm:visible, button#btnSaveNegotiationAdmindetForm")
            .or_(page.locator("#partial-form").get_by_role("button", name=re.compile(r"Save", re.I)))
            .or_(page.get_by_role("button", name=re.compile(r"Save", re.I)))
        )

        # ---------------------------------------------------------------------
        # 7. Encumbrances Subtab Elements
        # ---------------------------------------------------------------------
        self.add_new_encumbrance_button = page.locator(
            "#AddNewEncumbBtn:visible, button#AddNewEncumbBtn, button:visible:has-text('Add New')"
        )
        self.encumbrance_type_dropdown = page.locator(
            "#encumbDiv span.k-widget.k-dropdown:has(#encumb_type), #encumbDiv span[aria-owns='encumb_type_listbox'], #encumbDiv .k-dropdown"
        )
        self.grantor_input = (
            page.locator("#encumbDiv textarea#grantor, textarea#grantor:visible")
            .or_(page.locator("#encumbDiv input#Grantor, #encumbDiv input[name*='Grantor']"))
            .or_(page.get_by_role("textbox", name=re.compile(r"Grantor", re.I)))
        )
        self.grantee_input = (
            page.locator("#encumbDiv textarea#grantee, textarea#grantee:visible")
            .or_(page.locator("#encumbDiv input#Grantee, #encumbDiv input[name*='Grantee']"))
            .or_(page.get_by_role("textbox", name=re.compile(r"Grantee", re.I)))
        )
        self.save_encumbrance_button = page.locator(
            "#EncumbSaveBtn:visible, #encumbDiv button:has-text('Save'), button#EncumbSaveBtn"
        )
        self.easement_form = page.locator("#easementfrm")
        self.easement_type_dropdown = page.locator(
            "#easementfrm span.k-widget.k-dropdown:has(#type), #easementfrm span[aria-owns='type_listbox'], #easementfrm .k-dropdown"
        )
        self.back_encumbrance_button = page.locator(
            "#btnBackEncum:visible, button#btnBackEncum:visible"
        )

        # ---------------------------------------------------------------------
        # 8. Recording Subtab Elements
        # ---------------------------------------------------------------------
        self.add_new_recording_button = page.locator(
            "#AddNewRecordingBtn:visible, button#AddNewRecordingBtn, button:visible:has-text('Add New')"
        )
        self.instrument_type_dropdown = page.locator(
            "#RecordingDiv span.k-widget.k-dropdown, #RecordingDiv .k-dropdown"
        )
        self.save_recording_button = (
            page.locator("#RecordingDiv button:has-text('Save'), #RecordingDiv button:visible:has-text('Save')")
            .or_(page.locator("#RecordingDiv").get_by_role("button", name=re.compile(r"Save", re.I)))
            .or_(page.get_by_role("button", name=re.compile(r"Save", re.I)))
        )
        self.back_recording_button = page.locator(
            "#btnRecordingBack:visible, button#btnRecordingBack:visible"
        )

        # ---------------------------------------------------------------------
        # 9. Documents Subtab Elements
        # ---------------------------------------------------------------------
        self.documents_container = page.locator(
            "#partial-form > section > div > div, #partial-form:visible"
        )

        # ---------------------------------------------------------------------
        # 10. Log Tab Elements & Triggers
        # ---------------------------------------------------------------------
        self.log_container = page.locator(
            "#divLogTable:visible, #divLgTable:visible, button#btnAddCallData:visible"
        )
        self.log_table_header = page.get_by_text(
            "Type --Select Type-- Date - From To Subject Create Package Refresh Add Call"
        )
        self.add_call_data_button = page.locator(
            "button#btnAddCallData:visible, button:visible:has-text('Add Call Data')"
        )
        self.add_notes_button = page.locator(
            "button#btnAddNotes:visible, button:visible:has-text('Add Notes')"
        )
        self.add_attachment_button = page.locator(
            "button#btnAddAttachment:visible, button:visible:has-text('Add Attachment')"
        )

        # Log Form Locators (Call Data / Notes)
        self.log_subject_input = (
            page.locator("input#log_subject:visible, input[name='log_subject']:visible")
            .or_(page.get_by_role("textbox", name=re.compile(r"Subject", re.I)))
        )
        self.log_save_button = page.locator(
            "#btnSubmit:visible, button#btnSubmit:visible, button:visible:has-text('Save')"
        )
        self.log_back_button = page.locator(
            "#btnBacknotes:visible, button#btnBacknotes:visible"
        )

        # Add Attachment Form Locators
        self.attachment_container = page.locator("#CommLogDiv:visible, #divCommLog:visible")
        self.doc_type_dropdown = page.locator(
            "#CommLogDiv span.k-widget.k-dropdown, #CommLogDiv span.k-dropdown-wrap, #CommLogDiv .k-dropdown, span.k-widget.k-dropdown:has(#doctype_id)"
        )
        self.file_input = page.locator(
            "#CommLogDiv input#files[type='file'], input#files[type='file'], input[type='file']"
        )
        self.attachment_subject_input = (
            page.locator("#CommLogDiv input#doctitle:visible, input#doctitle:visible")
            .or_(page.locator("#CommLogDiv").get_by_role("textbox", name=re.compile(r"Subject", re.I)))
            .or_(page.get_by_role("textbox", name=re.compile(r"Subject", re.I)))
        )
        self.attachment_save_button = page.locator(
            "#SaveDocumentBtn:visible, button#SaveDocumentBtn, #CommLogDiv button:has-text('Save'), button:visible:has-text('Save')"
        )

        # ---------------------------------------------------------------------
        # 11. Error / Validation Alerts
        # ---------------------------------------------------------------------
        self.error_alerts = page.locator(
            ".alert-danger:visible, .field-validation-error:visible, .k-alert-error:visible"
        )

    # =========================================================================
    # Section 1: Navigation & Subtab Switching
    # =========================================================================

    def navigate_to_offer_negotiations(self) -> "OfferNegotiationsPage":
        """
        Navigates to Offer/Negotiations sub-menu in the left navigation sidebar
        and verifies the landing container visibility.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Navigating to Offer/Negotiations sub-menu via sidebar")
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        # Ensure Parcel Central sidebar group is expanded if needed
        pc_header = self.page.locator("#navigationMenu2, #navigationMenu").get_by_text("Parcel Central", exact=True).first
        nav_link = self.offer_negotiations_nav_link.first

        if not nav_link.is_visible() and pc_header.is_visible():
            pc_header.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        nav_link.scroll_into_view_if_needed()
        nav_link.click(force=True)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.landing_content_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        return self

    def switch_negotiation_tab(self, tab_name: str) -> "OfferNegotiationsPage":
        """
        Switches between tabs on the #OfferNegotiationTab widget using KendoTabStrip.

        Args:
            tab_name (str): Name of the subtab (e.g. 'Offers', 'Admin Adjustment', 'Log').

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info(f"Switching to negotiation tab '{tab_name}' via KendoTabStrip component")
        self._wait_for_loader()
        self.kendo_tabstrip.select_tab(self.offer_negotiation_tabs, tab_name)
        self.page.wait_for_timeout(300)
        self._wait_for_loader()
        return self

    # =========================================================================
    # Section 2: Negotiation Record Management & Offer Details
    # =========================================================================

    def open_add_new_negotiation_modal(self) -> "OfferNegotiationsPage":
        """Clicks 'Add New' button to open the negotiation modal."""
        self.logger.info("Opening Add New Negotiation modal")
        self.add_new_negotiation_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_negotiation_button.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        expect(self.negotiation_modal.first).to_be_visible(timeout=15000)
        return self

    def fill_and_save_negotiation(
        self,
        owner_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        status_name: Optional[str] = None,
    ) -> "OfferNegotiationsPage":
        """
        Fills the Add New Negotiation modal using KendoDropdown components (defaults to 1st option)
        and clicks Save.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Filling Add New Negotiation modal fields")
        # 1. Owner dropdown
        if owner_name:
            self.kendo_dropdown.select_option(self.owner_dropdown.first, owner_name)
        else:
            self.kendo_dropdown.select_first_option(self.owner_dropdown.first)
        self.page.wait_for_timeout(300)

        # 2. Acquisition Agent dropdown
        if agent_name:
            self.kendo_dropdown.select_option(self.agent_dropdown.first, agent_name)
        else:
            self.kendo_dropdown.select_first_option(self.agent_dropdown.first)
        self.page.wait_for_timeout(300)

        # 3. Status dropdown
        if status_name:
            self.kendo_dropdown.select_option(self.status_dropdown.first, status_name)
        else:
            self.kendo_dropdown.select_first_option(self.status_dropdown.first)
        self.page.wait_for_timeout(300)

        # 4. Save
        self.logger.info("Saving Negotiation record (#saveneg)")
        self.save_negotiation_button.first.click()
        self.page.wait_for_timeout(1500)
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()
        self.verify_no_errors()
        return self

    def ensure_negotiation_details_open(self) -> "OfferNegotiationsPage":
        """
        Ensures the Negotiation Details view is open. If #btnOfferDetailsEdit is not visible,
        opens the Add New modal, fills defaults, and saves.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        if self.edit_offer_details_button.count() == 0 or not self.edit_offer_details_button.first.is_visible():
            self.open_add_new_negotiation_modal()
            self.fill_and_save_negotiation()
        expect(self.edit_offer_details_button.first).to_be_visible(timeout=15000)
        return self

    def edit_offer_details(self, recommendation: Optional[str] = None) -> "OfferNegotiationsPage":
        """
        Clicks #btnOfferDetailsEdit, selects Recommendation dropdowns via KendoDropdown,
        and saves.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Editing Offer Details (#btnOfferDetailsEdit)")
        self.edit_offer_details_button.first.wait_for(state="visible", timeout=15000)
        self.edit_offer_details_button.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        # Select primary Recommendation dropdown
        rec_drop = self.recommendation_dropdown.first
        if rec_drop.is_visible():
            if recommendation:
                self.kendo_dropdown.select_option(rec_drop, recommendation)
            else:
                self.kendo_dropdown.select_first_option(rec_drop)
            self.page.wait_for_timeout(300)

        # Select secondary Recommendation dropdown if present
        if self.secondary_recommendation_dropdown.count() > 0 and self.secondary_recommendation_dropdown.is_visible():
            self.kendo_dropdown.select_first_option(self.secondary_recommendation_dropdown)
            self.page.wait_for_timeout(300)

        # Save Offer Details
        self.save_offer_details_button.first.wait_for(state="visible", timeout=15000)
        self.save_offer_details_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()
        self.verify_no_errors()
        self.logger.info("Offer Details saved successfully.")
        return self

    # =========================================================================
    # Section 3: Offers Subtab Operations
    # =========================================================================

    def navigate_to_offers_tab(self) -> "OfferNegotiationsPage":
        """Switches to the 'Offers' subtab."""
        return self.switch_negotiation_tab(self.TAB_OFFERS)

    def add_new_offer(self, offer_type: Optional[str] = None) -> "OfferNegotiationsPage":
        """
        Clicks 'Add New' in Offers subtab, selects Offer Type, picks date, saves,
        and returns to grid view.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Offers Subtab: Adding new offer record")
        self.add_new_offer_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_offer_button.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        # Select Offer Type dropdown
        drop = self.page.locator(
            "#divDisplayonAddnew span.k-widget.k-dropdown:has(#offer_type), #divDisplayonAddnew span[aria-owns='offer_type_listbox'], #divDisplayonAddnew span.k-widget.k-dropdown"
        ).first
        if drop.is_visible():
            if offer_type:
                self.kendo_dropdown.select_option(drop, offer_type)
            else:
                self.kendo_dropdown.select_first_option(drop)
            self.page.wait_for_timeout(300)

        # Set Offer Date
        date_inp = self.page.locator("#divDisplayonAddnew input#offer_dt, input#offer_dt").first
        if date_inp.is_visible() and date_inp.is_editable():
            date_inp.fill("11/24/2026")
            date_inp.press("Tab")
            self.page.wait_for_timeout(300)
        else:
            date_btn = self.offer_date_picker_button.first
            if date_btn.is_visible():
                date_btn.click()
                self.page.wait_for_timeout(300)
                day_link = self.page.locator(".k-calendar:visible td:not(.k-other-month) a").first
                if day_link.is_visible():
                    day_link.click()
                self.page.wait_for_timeout(300)

        # Save Offer
        self.save_offer_button.first.wait_for(state="visible", timeout=15000)
        self.save_offer_button.first.click()
        self.page.wait_for_timeout(1500)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()

        # Click Back if still visible
        if self.back_offer_button.count() > 0 and self.back_offer_button.first.is_visible():
            self.back_offer_button.first.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        self.verify_no_errors()
        self.logger.info("Offers Subtab: Offer added successfully.")
        return self

    # =========================================================================
    # Section 4: Admin Adjustment Subtab Operations
    # =========================================================================

    def navigate_to_admin_adjustment_tab(self) -> "OfferNegotiationsPage":
        """Switches to the 'Admin Adjustment' subtab."""
        return self.switch_negotiation_tab(self.TAB_ADMIN_ADJUSTMENT)

    def edit_and_save_admin_adjustment(self) -> "OfferNegotiationsPage":
        """
        Clicks Edit in Admin Adjustment subtab, picks date via calendar button, and saves.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Admin Adjustment Subtab: Editing admin adjustment")
        if self.edit_admin_form_button.count() > 0 and self.edit_admin_form_button.first.is_visible():
            self.edit_admin_form_button.first.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

            # Date picker: Click calendar button (select) and pick first valid active day
            date_picker_btn = self.admin_date_picker_button.first
            if date_picker_btn.is_visible():
                self.logger.info("Opening Kendo calendar picker via 'select' button")
                date_picker_btn.click()
                self.page.wait_for_timeout(400)
                cal_day = self.page.locator(".k-calendar:visible td:not(.k-other-month) a").first
                if cal_day.is_visible():
                    cal_day.click()
                self.page.wait_for_timeout(300)
            else:
                # Fallback to editable date input if present
                editable_date = self.page.locator(
                    "#partial-form input[name*='Date']:not([readonly]):not([disabled]), #partial-form input[id*='Date']:not([readonly]):not([disabled])"
                ).first
                if editable_date.is_visible() and editable_date.is_editable():
                    editable_date.fill("11/24/2026")
                    editable_date.press("Tab")
                    self.page.wait_for_timeout(300)

            # Save
            self.save_admin_form_button.first.wait_for(state="visible", timeout=15000)
            self.save_admin_form_button.first.click()
            self.page.wait_for_timeout(1500)
            self._wait_for_loader()
            self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
            self._wait_for_loader()

        self.verify_no_errors()
        self.logger.info("Admin Adjustment Subtab: Saved successfully.")
        return self

    # =========================================================================
    # Section 5: Encumbrances Subtab Operations
    # =========================================================================

    def navigate_to_encumbrances_tab(self) -> "OfferNegotiationsPage":
        """Switches to the 'Encumbrances' subtab."""
        return self.switch_negotiation_tab(self.TAB_ENCUMBRANCES)

    def add_new_encumbrance(
        self,
        encumbrance_type: Optional[str] = None,
        grantor_text: Optional[str] = None,
        grantee_text: Optional[str] = None,
        easement_type: Optional[str] = None,
    ) -> "OfferNegotiationsPage":
        """
        Clicks 'Add New' in Encumbrances subtab, selects Encumbrance Type,
        fills mandatory Grantor, Grantee, and Easement Type (if applicable),
        saves the encumbrance, and returns to the grid view.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Encumbrances Subtab: Adding new encumbrance")
        self.add_new_encumbrance_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_encumbrance_button.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        # 1. Select Encumbrance Type from dropdown
        enc_drop = (
            self.page.locator("#encumbDiv").get_by_text(re.compile(r"--Select Type--", re.I))
            .or_(self.page.locator("#encumbDiv .k-dropdown-wrap:visible, #encumbDiv span.k-widget.k-dropdown:visible"))
            .first
        )
        if enc_drop.is_visible():
            enc_drop.click()
            self.page.wait_for_timeout(400)
            if encumbrance_type:
                enc_opt = self.page.get_by_role("option", name=re.compile(encumbrance_type, re.I)).first
            else:
                enc_opt = (
                    self.page.get_by_role("option", name=re.compile(r"Easement", re.I))
                    .or_(self.page.get_by_role("option").filter(has_not_text=re.compile(r"--Select", re.I)))
                    .first
                )
            if enc_opt.is_visible():
                enc_opt.click()
            else:
                self.kendo_dropdown.select_first_option(enc_drop)
            self.page.wait_for_timeout(500)

        # 2. Fill Mandatory Grantor & Grantee textboxes
        g_text = grantor_text or f"Grantor {fake.last_name()}"
        ge_text = grantee_text or f"Grantee {fake.random_int(100, 999)}"

        grantor = (
            self.page.locator("#encumbDiv textarea#grantor, textarea#grantor:visible")
            .or_(self.page.locator("#encumbDiv input#Grantor, #encumbDiv input[name*='Grantor']"))
            .or_(self.page.get_by_role("textbox", name=re.compile(r"Grantor", re.I)))
            .first
        )
        grantor.wait_for(state="visible", timeout=10000)
        grantor.click()
        grantor.fill(g_text)
        self.page.wait_for_timeout(200)

        grantee = (
            self.page.locator("#encumbDiv textarea#grantee, textarea#grantee:visible")
            .or_(self.page.locator("#encumbDiv input#Grantee, #encumbDiv input[name*='Grantee']"))
            .or_(self.page.get_by_role("textbox", name=re.compile(r"Grantee", re.I)))
            .first
        )
        grantee.wait_for(state="visible", timeout=10000)
        grantee.click()
        grantee.fill(ge_text)
        self.page.wait_for_timeout(200)

        # 3. Fill Mandatory Easement Type if visible (BEFORE saving!)
        ease_ddl_trigger = (
            self.page.locator("#easementfrm").get_by_text(re.compile(r"--Select Easement Type--", re.I))
            .or_(self.page.locator("#easementfrm span.k-widget.k-dropdown:has(#type), #easementfrm .k-dropdown-wrap:visible"))
            .first
        )
        if ease_ddl_trigger.is_visible() or (self.easement_form.count() > 0 and self.easement_form.first.is_visible()):
            self.logger.info("Encumbrances: Selecting mandatory Easement Type")
            if ease_ddl_trigger.is_visible():
                ease_ddl_trigger.click()
                self.page.wait_for_timeout(400)
                if easement_type:
                    opt = self.page.get_by_role("option", name=re.compile(easement_type, re.I)).first
                else:
                    opt = (
                        self.page.get_by_role("option", name=re.compile(r"Permanent Drainage|Drainage", re.I))
                        .or_(self.page.get_by_role("option").filter(has_not_text=re.compile(r"--Select", re.I)))
                        .first
                    )
                if opt.is_visible():
                    opt.click()
                else:
                    self.kendo_dropdown.select_by_id("type", index=1)
                self.page.wait_for_timeout(400)

        # 4. Save Encumbrance (all mandatory fields filled!)
        save_btn = (
            self.page.locator("#EncumbSaveBtn:visible, #encumbDiv button:has-text('Save'), button#EncumbSaveBtn")
            .or_(self.page.locator("#encumbDiv").get_by_role("button", name=re.compile(r"Save", re.I)))
            .first
        )
        save_btn.wait_for(state="visible", timeout=15000)
        save_btn.click()
        self.page.wait_for_timeout(1500)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()

        # 5. Return via Back button
        back_enc = self.page.locator("#btnBackEncum:visible, button#btnBackEncum:visible, #btnBackEncum").first
        if back_enc.count() > 0 and back_enc.is_visible():
            back_enc.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        self.verify_no_errors()
        self.logger.info("Encumbrances Subtab: Encumbrance added successfully.")
        return self

    # =========================================================================
    # Section 6: Recording Subtab Operations
    # =========================================================================

    def navigate_to_recording_tab(self) -> "OfferNegotiationsPage":
        """Switches to the 'Recording' subtab."""
        return self.switch_negotiation_tab(self.TAB_RECORDING)

    def add_new_recording(self, instrument_type: Optional[str] = None) -> "OfferNegotiationsPage":
        """
        Clicks 'Add New' in Recording subtab, selects Instrument Type, saves,
        and returns to grid.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Recording Subtab: Adding new recording entry")
        self.add_new_recording_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_recording_button.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        # Select Instrument Type
        rec_drop = (
            self.page.locator("#RecordingDiv").get_by_text(re.compile(r"--Select Instrument Type--", re.I))
            .or_(self.page.locator("#RecordingDiv .k-dropdown-wrap:visible, #RecordingDiv span.k-widget.k-dropdown:visible"))
            .first
        )
        rec_drop.wait_for(state="visible", timeout=10000)
        rec_drop.click()
        self.page.wait_for_timeout(400)
        if instrument_type:
            rec_opt = self.page.get_by_role("option", name=re.compile(instrument_type, re.I)).first
        else:
            rec_opt = (
                self.page.get_by_role("option", name=re.compile(r"Affidavit", re.I))
                .or_(self.page.get_by_role("option").filter(has_not_text=re.compile(r"--Select", re.I)))
                .first
            )
        if rec_opt.is_visible():
            rec_opt.click()
        else:
            self.kendo_dropdown.select_first_option(rec_drop)
        self.page.wait_for_timeout(400)

        # Save Recording
        save_rec = (
            self.page.locator("#RecordingDiv button:visible")
            .filter(has_text=re.compile(r"Save", re.I))
            .or_(self.page.locator("#RecordingDiv [role='button']:visible").filter(has_text=re.compile(r"Save", re.I)))
            .or_(self.save_recording_button)
            .first
        )
        save_rec.wait_for(state="visible", timeout=15000)
        save_rec.click()
        self.page.wait_for_timeout(1500)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()

        # Return via Back button
        back_rec = self.page.locator("#btnRecordingBack:visible, button#btnRecordingBack:visible, #btnRecordingBack").first
        if back_rec.count() > 0 and back_rec.is_visible():
            back_rec.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        self.verify_no_errors()
        self.logger.info("Recording Subtab: Recording entry added successfully.")
        return self

    # =========================================================================
    # Section 7: Documents Subtab Operations
    # =========================================================================

    def navigate_to_documents_tab(self) -> "OfferNegotiationsPage":
        """
        Clicks 'Documents' tab and verifies view container visibility.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Documents Tab: Navigating and verifying container")
        self.switch_negotiation_tab(self.TAB_DOCUMENTS)
        expect(self.documents_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Documents Tab: Verified successfully.")
        return self

    # =========================================================================
    # Section 8: Log Tab Operations
    # =========================================================================

    def navigate_to_log_tab(self) -> "OfferNegotiationsPage":
        """
        Navigates to Log tab on #OfferNegotiationTab, verifies table visibility,
        and checks for zero error alerts.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        self.logger.info("Log Tab: Navigating to Log tab and verifying table display")
        self.switch_negotiation_tab(self.TAB_LOG)
        expect(self.log_container.first.or_(self.log_table_header).first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Log Tab: Verified table displayed cleanly without errors.")
        return self

    def _create_log_entry(self, trigger_button: Locator, subject: str, entry_type: str = "Entry") -> None:
        """Helper to create a log entry (Call Data or Notes), save, and return via #btnBacknotes."""
        self.logger.info(f"Log Tab: Creating {entry_type} with subject '{subject}'")
        btn = trigger_button.first
        btn.wait_for(state="visible", timeout=15000)
        btn.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        subj = self.log_subject_input.first
        subj.wait_for(state="visible", timeout=15000)
        subj.click()
        subj.fill(subject)
        self.page.wait_for_timeout(300)

        save_btn = (
            self.page.locator("button#btnSubmit:visible, #btnSubmit:visible")
            .or_(self.page.get_by_role("button", name=re.compile(r"Save", re.I)))
            .first
        )
        save_btn.wait_for(state="visible", timeout=15000)
        save_btn.click()
        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()

        back_btn = self.log_back_button.first
        back_btn.wait_for(state="visible", timeout=15000)
        back_btn.click()
        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        self.log_container.first.wait_for(state="visible", timeout=15000)

    def add_call_data(self, subject: Optional[str] = None) -> "OfferNegotiationsPage":
        """Adds a Call Data entry using dummy Faker data, saves, and returns."""
        c_subj = subject or f"Call {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self._create_log_entry(self.add_call_data_button, c_subj, entry_type="Call Data")
        self.verify_no_errors()
        return self

    def add_notes(self, subject: Optional[str] = None) -> "OfferNegotiationsPage":
        """Adds a Notes entry using dummy Faker data, saves, and returns."""
        n_subj = subject or f"Note {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self._create_log_entry(self.add_notes_button, n_subj, entry_type="Notes")
        self.verify_no_errors()
        return self

    def _get_or_create_dummy_file(self) -> str:
        """Ensures a valid sample file exists for attachment upload using Config.TESTDATA_DIR."""
        testdata_dir = str(Config.TESTDATA_DIR)
        os.makedirs(testdata_dir, exist_ok=True)
        sample_path = os.path.join(testdata_dir, self.DEFAULT_SAMPLE_FILENAME)
        if not os.path.exists(sample_path):
            with open(sample_path, "w") as f:
                f.write("This is a dummy test attachment for NCDOT offer negotiations automation.")
        return sample_path

    def add_attachment(
        self,
        file_path: Optional[str] = None,
        subject: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> "OfferNegotiationsPage":
        """
        Adds an attachment:
          1. Clicks 'Add Attachment' and waits for #CommLogDiv container.
          2. Selects the 1st available Document Type option via KendoDropdown component.
          3. Uploads the dummy file.
          4. Enters Subject.
          5. Clicks Save (#SaveDocumentBtn) and handles alert dialog via KendoDialog.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        upload_path = file_path or self._get_or_create_dummy_file()
        att_subj = subject or f"Att {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self.logger.info(f"Log Tab: Adding Attachment (file='{os.path.basename(upload_path)}', subject='{att_subj}')")

        attach_btn = self.add_attachment_button.first
        attach_btn.wait_for(state="visible", timeout=15000)
        attach_btn.click()

        # Wait for #CommLogDiv container to open
        self.attachment_container.first.wait_for(state="visible", timeout=15000)
        self._wait_for_loader()

        # Select Document Type
        doc_drop = (
            self.page.locator("#CommLogDiv").get_by_text(re.compile(r"--Select Document Type--", re.I))
            .or_(self.page.locator("#CommLogDiv .k-dropdown-wrap:visible, #CommLogDiv span.k-widget.k-dropdown:visible"))
            .first
        )
        if doc_drop.is_visible():
            doc_drop.click()
            self.page.wait_for_timeout(400)
            if doc_type:
                doc_opt = self.page.get_by_role("option", name=re.compile(doc_type, re.I)).first
            else:
                doc_opt = (
                    self.page.get_by_role("option").filter(has_not_text=re.compile(r"--Select", re.I))
                    .first
                )
            if doc_opt.is_visible():
                doc_opt.click()
            else:
                self.kendo_dropdown.select_first_option(self.doc_type_dropdown)
            self.page.wait_for_timeout(300)

        # Upload file via file input
        file_inp = self.file_input.first
        file_inp.set_input_files(upload_path)
        self.page.wait_for_timeout(500)

        # Fill Subject
        subj_inp = self.attachment_subject_input.first
        subj_inp.wait_for(state="visible", timeout=10000)
        subj_inp.click()
        subj_inp.fill(att_subj)
        self.page.wait_for_timeout(300)

        # Click Save (#SaveDocumentBtn)
        save_btn = (
            self.page.locator("#CommLogDiv button:visible")
            .filter(has_text=re.compile(r"Save", re.I))
            .or_(self.attachment_save_button)
            .first
        )
        save_btn.wait_for(state="visible", timeout=15000)
        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()

        # Verify returned to log table
        expect(self.log_container.first.or_(self.log_table_header).first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Attachment uploaded and saved successfully.")
        return self

    # =========================================================================
    # Section 9: Error Verification
    # =========================================================================

    def verify_no_errors(self) -> "OfferNegotiationsPage":
        """
        Verifies that no error alerts or validation errors are displayed.

        Returns:
            OfferNegotiationsPage: Current page instance for fluent chaining.
        """
        if self.error_alerts.count() > 0:
            err_texts = self.error_alerts.all_text_contents()
            self.logger.error(f"Validation/Error alerts found: {err_texts}")
        expect(self.error_alerts).to_have_count(0, timeout=5000)
        return self
