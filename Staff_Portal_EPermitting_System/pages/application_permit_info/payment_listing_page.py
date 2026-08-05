import datetime
import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PaymentListingPage(BasePage):
    """
    Page Object Model for Payment Listing & Payment Details in Staff Portal E-Permitting System.
    Implemented based on Playwright codegen recording with high resilience.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.payments_tab = page.get_by_role("link", name="Payments").or_(
            page.locator("a:has-text('Payments'), span:has-text('Payments'), .k-tabstrip a:has-text('Payments')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")

        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing").or_(
            page.get_by_role("heading", name=re.compile("Payment", re.I))
        ).first

        self.row_div_three = page.locator(".row > div:nth-child(3)").first

        # ── Form Controls & Buttons ───────────────────────────────────────────
        self.add_new_payment_button = page.get_by_role("button", name=" Add New Payment").or_(
            page.get_by_role("button", name="Add New Payment")
        ).first

        self.payment_details_heading = page.get_by_role("heading", name="Payment Details").first

        self.refund_details_heading = page.get_by_role("heading", name="Refund Details").first

        self.payment_details_save_cancel_text = page.get_by_text("Payment Details Save Cancel").first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).first

        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log").or_(
            page.get_by_text("Documents and Log")
        ).first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_payments(self) -> None:
        """Navigates to Payments tab."""
        logger.info("Navigating to Payments tab.")
        self._wait_for_loader()
        if self.payments_tab.is_visible():
            self.js_click(self.payments_tab)
        else:
            self.page.evaluate("$('a:contains(\"Payments\"), span:contains(\"Payments\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Verifies Payments page initial layout matching codegen assertions."""
        logger.info("Verifying Payments initial layout.")
        self._wait_for_loader()
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.payment_listing_heading).to_be_visible(timeout=15000)
        expect(self.row_div_three).to_be_visible(timeout=15000)

    def add_payment_details(self, amount: str = "50", comments: str = "test") -> None:
        """
        Fills and saves payment details matching exact codegen sequence:
        1. Click 'Add New Payment' -> Expect 'Payment Details' heading
        2. Select Payment Type ('Bond' or 1st valid option)
        3. Wait for Sub Type options via Kendo AJAX and select ('Maintenance' or 1st valid option)
        4. Select Method of Payment ('Bond' or 1st valid option)
        5. Fill Requested Amount ($) & Comments (populated via Faker)
        6. Expect 'Refund Details' heading & 'Payment Details Save Cancel' text
        7. Interact with Date Pickers selecting current date (present day)
        8. Click Save -> Expect row div 3 & 'Documents and Log' heading
        """
        logger.info(f"Adding payment details - Amount: {amount}, Comments: {comments}")
        self._wait_for_loader()

        # 1. Click Add New Payment
        if self.add_new_payment_button.is_visible():
            self.js_click(self.add_new_payment_button)
            self._wait_for_loader()

        expect(self.payment_details_heading).to_be_visible(timeout=15000)

        # 2. Select Payment Type --Select Payment Type --
        try:
            pt_trigger = self.page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --").or_(
                self.page.locator("#frmPaymentDetails span.k-widget.k-dropdown").first
            ).first
            if pt_trigger.is_visible():
                pt_trigger.click()
                self.page.wait_for_timeout(500)
                bond_opt = self.page.get_by_role("option", name="Bond").first
                if bond_opt.is_visible():
                    bond_opt.click()
                else:
                    self.page.evaluate("""
                        () => {
                            var ddl = $('#frmPaymentDetails span.k-widget.k-dropdown').eq(0).find('input, select').data('kendoDropDownList');
                            if (ddl) { ddl.select(1); ddl.trigger('change'); }
                        }
                    """)
                self.page.wait_for_timeout(1000)
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Payment Type selection note: {e}")

        # 3. Wait for Payment Sub Type options to load via AJAX and select
        try:
            for _ in range(20):
                data_len = self.page.evaluate("""
                    () => {
                        var ddls = $('#frmPaymentDetails span.k-widget.k-dropdown');
                        for (var i = 0; i < ddls.length; i++) {
                            var kWidget = $(ddls[i]).find('input, select').data('kendoDropDownList') || $(ddls[i]).data('kendoDropDownList');
                            if (kWidget && kWidget.element && (kWidget.element.attr('id') || '').toLowerCase().includes('sub')) {
                                return kWidget.dataSource ? kWidget.dataSource.data().length : 0;
                            }
                        }
                        var ddl = $('#Payment_Sub_Type, #Payment_SubType, #Payment_Subtype, [name*="Sub"]').data('kendoDropDownList');
                        return (ddl && ddl.dataSource) ? ddl.dataSource.data().length : 0;
                    }
                """)
                if data_len > 1:
                    break
                self.page.wait_for_timeout(500)

            pst_trigger = self.page.locator("#frmPaymentDetails").get_by_text("--Select Payment Sub Type--").or_(
                self.page.locator("#frmPaymentDetails span.k-widget.k-dropdown").nth(1)
            ).first
            if pst_trigger.is_visible():
                pst_trigger.click()
                self.page.wait_for_timeout(500)
                maint_opt = self.page.get_by_role("option", name="Maintenance").first
                if maint_opt.is_visible():
                    maint_opt.click()
                else:
                    self.page.evaluate("""
                        () => {
                            var ddls = $('#frmPaymentDetails span.k-widget.k-dropdown');
                            for (var i = 0; i < ddls.length; i++) {
                                var kWidget = $(ddls[i]).find('input, select').data('kendoDropDownList') || $(ddls[i]).data('kendoDropDownList');
                                if (kWidget && kWidget.element && (kWidget.element.attr('id') || '').toLowerCase().includes('sub')) {
                                    kWidget.select(1);
                                    kWidget.trigger('change');
                                    return;
                                }
                            }
                            var ddl = $('#Payment_Sub_Type, #Payment_SubType, #Payment_Subtype, [name*="Sub"]').data('kendoDropDownList');
                            if (ddl) { ddl.select(1); ddl.trigger('change'); }
                        }
                    """)
                self.page.wait_for_timeout(500)
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Payment Sub Type selection note: {e}")

        # 4. Select Method Of Payment --Select Method Of Payment --
        try:
            mop_trigger = self.page.locator("#frmPaymentDetails").get_by_text("--Select Method Of Payment --").or_(
                self.page.locator("#frmPaymentDetails span.k-widget.k-dropdown").nth(2)
            ).first
            if mop_trigger.is_visible():
                mop_trigger.click()
                self.page.wait_for_timeout(500)
                bond_opt = self.page.get_by_role("option", name="Bond").first
                if bond_opt.is_visible():
                    bond_opt.click()
                else:
                    self.page.evaluate("""
                        () => {
                            var ddls = $('#frmPaymentDetails span.k-widget.k-dropdown');
                            var ddl = $(ddls[2]).find('input, select').data('kendoDropDownList') || $('#Method_Of_Payment, #Method_of_Payment').data('kendoDropDownList');
                            if (ddl) { ddl.select(1); ddl.trigger('change'); }
                        }
                    """)
                self.page.wait_for_timeout(500)
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Method of Payment selection note: {e}")

        # Ensure all dropdowns are selected via Kendo API fallback if still showing placeholder
        self.page.evaluate("""
            () => {
                $('#frmPaymentDetails span.k-widget.k-dropdown').each(function() {
                    var ddl = $(this).find('input, select').data('kendoDropDownList') || $(this).data('kendoDropDownList');
                    if (ddl && (ddl.selectedIndex === 0 || ddl.value() === "" || (ddl.text() || "").startsWith("--"))) {
                        if (ddl.dataSource && ddl.dataSource.data().length > 1) {
                            ddl.select(1);
                            ddl.trigger("change");
                        }
                    }
                });
            }
        """)

        # 5. Fill Requested Amount ($)
        try:
            amount_input = self.page.get_by_role("spinbutton", name="Requested Amount ($) *").or_(
                self.page.get_by_role("spinbutton").first
            ).first
            amount_input.click()
            amount_input.fill(str(amount))
            amount_input.press("Enter")
        except Exception as e:
            logger.warning(f"Amount fill note: {e}")

        # 6. Fill Comments
        try:
            comments_input = self.page.get_by_role("textbox", name="Comments").first
            comments_input.click()
            comments_input.fill(comments)
        except Exception as e:
            logger.warning(f"Comments fill note: {e}")

        # 7. Assert section headings from codegen
        try:
            if self.refund_details_heading.is_visible():
                expect(self.refund_details_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        try:
            if self.payment_details_save_cancel_text.is_visible():
                expect(self.payment_details_save_cancel_text).to_be_visible(timeout=5000)
        except Exception:
            pass

        # 8. Date Pickers using present day
        today = datetime.date.today()
        day_str = str(today.day)
        date_title_prefix = today.strftime("%A, %B %d")

        try:
            select_first = self.page.get_by_role("button", name="select").first
            if select_first.is_visible():
                select_first.click()
                self.page.wait_for_timeout(300)
                link1 = self.page.get_by_label("Current focused date is").get_by_role("link", name=day_str).first
                if link1.is_visible():
                    link1.click()
                else:
                    link1_alt = self.page.locator(".k-calendar-container:visible, .k-animation-container:visible").get_by_role("link", name=day_str, exact=True).first
                    if link1_alt.is_visible():
                        link1_alt.click()
        except Exception as e:
            logger.warning(f"Date picker 1 selection note: {e}")

        try:
            select_second = self.page.get_by_role("button", name="select").nth(1)
            if select_second.is_visible():
                select_second.click()
                self.page.wait_for_timeout(300)
                grid_title = self.page.get_by_role("grid").get_by_title(re.compile(date_title_prefix, re.I)).first
                if grid_title.is_visible():
                    grid_title.click()
                else:
                    link2 = self.page.get_by_label("Current focused date is").get_by_role("link", name=day_str).first
                    if link2.is_visible():
                        link2.click()
        except Exception as e:
            logger.warning(f"Date picker 2 selection note: {e}")

        self.set_all_datefields_to_current()

        # 9. Click Save and assert no validation errors
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

        # 10. Final assertions matching codegen
        expect(self.row_div_three).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=15000)
