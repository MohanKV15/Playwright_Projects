import logging
import datetime
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage
from faker import Faker

logger = logging.getLogger(__name__)

class LotDevelopmentPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Tabs
        self.lot_development_tab = page.get_by_role("link", name="Lot Development/Frontages")
        
        # Heading & Section Container Selectors
        self.heading_lot_development = page.get_by_role("heading", name="Lot/Development/Frontage")
        self.spacing_heading = page.get_by_role("heading", name="Spacing")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        
        # Add New Land Use Selectors
        self.add_land_use_button = page.locator("#btnlandusenewentry")
        self.land_use_modal_title = page.locator("div").filter(has_text="Add/Edit New Land Use")
        self.land_use_type_dropdown = page.locator("#landusediv").get_by_text("--Select Land Use Type--")
        self.land_use_size_input = page.get_by_role("dialog", name="Add/Edit New Land Use").get_by_role("spinbutton")
        self.save_land_use_button = page.locator("#btnsavelanduse")
        
        # Add/Edit Spacing Selectors
        self.add_spacing_button = page.locator("#btnspacingentry")
        self.spacing_modal_title = page.locator("#DivForNewEntryWindow_wnd_title")
        self.lot_size_input = page.locator("#lot_size")
        self.lot_frontage_input = page.locator("#lot_frontage")
        self.save_spacing_button = page.locator("#btnspacingsave")
        
        # Documents and Log Selectors
        self.attach_document_button = page.get_by_role("button", name="Attach Document")
        self.document_modal_save = page.get_by_text("Save Cancel Preparation Date")
        self.date_picker_button = page.get_by_role("button", name="select", exact=True)
        self.file_input = page.get_by_role("button", name="File Name * Select files...")
        self.subject_input = page.get_by_role("textbox", name="Subject *")
        self.description_input = page.get_by_role("textbox", name="Description")
        self.save_document_button = page.get_by_role("button", name=" Save")
        
        # Communications Selectors
        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.communication_modal_container = page.locator("#divfrmLog > .form-wrapper > .row > .col-md-12")
        self.communication_date_picker = page.get_by_role("button", name="select")
        
        # Package & Email Selectors
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_title = page.locator(".k-window-title:visible").get_by_text("Select Attachments for Permit")
        self.first_attachment_checkbox = page.locator(".k-window:visible input[type='checkbox'], [role='dialog']:visible input[type='checkbox']").first
        self.select_attachments_confirm_button = page.get_by_role("button", name="Select Attachments")
        self.package_created_message = page.locator(".k-window:visible, [role='dialog']:visible").get_by_text("Your document package is")
        self.ok_button = page.get_by_role("button", name="OK")
        
        self.send_email_button = page.get_by_role("button", name="Send Email")
        self.email_form_container = page.get_by_text("Send Cancel To: * CC: BCC:")
        self.cancel_email_button = page.get_by_role("button", name=" Cancel")

    def _wait_for_loader(self, timeout=60000):
        """Waits for the global loading spinner and blocking elements to disappear."""
        try:
            self.page.locator("#loader").wait_for(state="hidden", timeout=timeout)
            self.page.locator(".k-overlay").wait_for(state="hidden", timeout=15000)
            self.page.wait_for_timeout(500)
        except Exception:
            pass

    def _select_first_dropdown_option(self) -> None:
        """Clicks the first valid option in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible, .k-list-container:visible", timeout=5000)
        options = self.page.locator("[role='listbox']:visible [role='option'], .k-list-container:visible [role='option']")
        self.page.wait_for_timeout(500)
        if options.count() > 1:
            logger.info("Selecting first valid option (index 1) in Kendo dropdown")
            self.js_click(options.nth(1))
        else:
            logger.info("Selecting option (index 0) in Kendo dropdown")
            self.js_click(options.first)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

    def set_all_datefields_to_current(self) -> None:
        """Sets all active Kendo DatePickers to today's date via direct JS injection."""
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        logger.info(f"JS Injecting current date: '{current_date_str}' to all active datepicker inputs.")
        self.page.evaluate(f"""
            () => {{
                $('input[data-role="datepicker"]').each(function() {{
                    var dp = $(this).data("kendoDatePicker");
                    if (dp) {{
                        dp.value("{current_date_str}");
                        dp.trigger("change");
                    }} else {{
                        $(this).val("{current_date_str}");
                    }}
                }});
            }}
        """)
        self.page.wait_for_timeout(500)

    def select_today_in_calendar(self, trigger_button: Locator) -> None:
        """Opens calendar datepicker and clicks the today/present link dynamically."""
        logger.info("Clicking date picker calendar button.")
        self.js_click(trigger_button)
        self.page.wait_for_timeout(500)
        today_day = str(datetime.datetime.now().day)
        try:
            # Try to click Kendo today's focused link
            today_link = self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a, .k-calendar .k-state-selected a").first
            self.js_click(today_link)
            logger.info("Clicked today's date using Kendo today classes.")
        except Exception:
            # Fallback to day number link in visible calendar
            day_link = self.page.locator(".k-calendar:visible, .k-calendar-container:visible").get_by_role("link", name=today_day, exact=True).first
            self.js_click(day_link)
            logger.info(f"Clicked day number link '{today_day}'.")
        self.page.wait_for_timeout(500)

    def navigate_to_lot_development(self) -> None:
        """Transitions to the Lot Development / Frontages tab."""
        logger.info("Navigating to Lot Development/Frontages tab.")
        self._wait_for_loader()
        self.js_click(self.lot_development_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates all headers and layout grids exist on the page."""
        logger.info("Verifying initial layout of Lot Development/Frontages page.")
        expect(self.heading_lot_development).to_be_visible(timeout=15000)
        expect(self.page.locator(".col-md-8")).to_be_visible(timeout=10000)
        expect(self.page.locator("#partial-form > .form-wrapper > .row > .col-md-12").first).to_be_visible(timeout=10000)

    def add_land_use(self, units: str = "4") -> None:
        """Creates a new Land Use entry with the specified units/size."""
        logger.info("Adding a new Land Use entry.")
        self.js_click(self.add_land_use_button)
        expect(self.land_use_modal_title.first).to_be_visible(timeout=10000)
        
        # Click dropdown and select first valid option
        self.js_click(self.land_use_type_dropdown)
        self._select_first_dropdown_option()
        
        # Fill Units/Size
        self.js_click(self.land_use_size_input)
        self.land_use_size_input.fill(units)
        
        # Save
        self.js_click(self.save_land_use_button)
        self._wait_for_loader()
        expect(self.page.locator("#partial-form > .form-wrapper > .row > .col-md-12").first).to_be_visible(timeout=10000)
        logger.info("Land Use entry added successfully.")

    def add_spacing(self, size: str = "4", frontage: str = "5") -> None:
        """Creates a new Spacing entry by filling form inputs and choosing dropdown options."""
        logger.info("Adding a new Spacing entry.")
        expect(self.spacing_heading).to_be_visible(timeout=10000)
        self.js_click(self.add_spacing_button)
        expect(self.spacing_modal_title).to_be_visible(timeout=10000)
        
        # Fill Lot Size & Lot Frontage using Kendo NumericTextBox API
        self._set_kendo_numeric_value("lot_size", float(size))
        self._set_kendo_numeric_value("lot_frontage", float(frontage))
        
        # Loop through all dropdown widgets inside spacing form and choose the 1st valid option
        dropdowns = self.page.locator("#spacingformdiv span.k-dropdown, #spacingformdiv span[role='listbox']")
        count = dropdowns.count()
        logger.info(f"Found {count} dropdowns inside spacing form container. Cycling selections.")
        for i in range(count):
            self.js_click(dropdowns.nth(i))
            self._select_first_dropdown_option()
            
        # Save spacing
        self.js_click(self.save_spacing_button)
        self._wait_for_loader()
        logger.info("Spacing entry added successfully.")

    def attach_document(self, file_path: str, subject: str = "test", description: str = "test") -> None:
        """Attaches a document to the Documents and Log section."""
        logger.info(f"Attaching document: {file_path}")
        expect(self.documents_log_heading).to_be_visible(timeout=10000)
        self.js_click(self.attach_document_button)
        expect(self.document_modal_save).to_be_visible(timeout=10000)
        
        # Set file input
        self.file_input.set_input_files(file_path)
        self.page.wait_for_timeout(1000)
        
        # Fill text inputs
        self.js_click(self.subject_input)
        self.subject_input.fill(subject)
        
        self.js_click(self.description_input)
        self.description_input.fill(description)
        
        # Select today's date
        self.select_today_in_calendar(self.date_picker_button)
        
        # Direct JS safety injection just to ensure dates are correct
        self.set_all_datefields_to_current()
        
        # Click Save
        self.js_click(self.save_document_button)
        self._wait_for_loader()
        logger.info("Document attached successfully.")

    def add_communication(self, subject: str = "testingd", description: str = "one") -> None:
        """Adds a communication log entry."""
        logger.info("Adding a new communication entry.")
        self.js_click(self.add_communication_button)
        expect(self.communication_modal_container).to_be_visible(timeout=10000)
        
        # Select date
        self.select_today_in_calendar(self.communication_date_picker)
        
        # Fill text inputs
        self.js_click(self.subject_input)
        self.subject_input.fill(subject)
        
        self.js_click(self.description_input)
        self.description_input.fill(description)
        
        # Direct JS safety injection just to ensure dates are correct
        self.set_all_datefields_to_current()
        
        # Click Save
        self.js_click(self.save_document_button)
        self._wait_for_loader()
        logger.info("Communication entry added successfully.")

    def create_package_and_verify(self) -> None:
        """Clicks Create Package, checks the first attachment, and verifies document package creation."""
        logger.info("Creating package from attachments.")
        self.js_click(self.create_package_button)
        expect(self.select_attachments_title).to_be_visible(timeout=10000)
        
        # Select first checkbox
        expect(self.first_attachment_checkbox).to_be_visible(timeout=10000)
        self.js_click(self.first_attachment_checkbox)
        
        # Select attachments button
        self.js_click(self.select_attachments_confirm_button)
        
        # Verify success message and click OK
        expect(self.package_created_message).to_be_visible(timeout=15000)
        self.js_click(self.ok_button)
        self._wait_for_loader()
        logger.info("Document package created and verified successfully.")

    def send_email_and_verify(self) -> None:
        """Clicks Send Email, validates email window layout, cancels, and accepts final prompt."""
        logger.info("Testing Send Email action.")
        self.js_click(self.send_email_button)
        expect(self.email_form_container).to_be_visible(timeout=10000)
        
        # Cancel Email
        self.js_click(self.cancel_email_button)
        
        # Accept final alert dialog (if any Kendo confirmation overlay appears)
        try:
            self.ok_button.wait_for(state="visible", timeout=5000)
            self.js_click(self.ok_button)
            logger.info("Clicked OK on confirmation prompt.")
        except Exception:
            logger.info("OK button confirmation prompt did not appear.")
            
        self._wait_for_loader()
        expect(self.heading_lot_development).to_be_visible(timeout=15000)
        logger.info("Email cancelled and verified successfully.")
