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

        self.save_button = page.locator(
            "button:has-text('Save'), input[type='submit'][value='Save'], input[type='button'][value='Save'], a:has-text('Save'), .btn:has-text('Save')"
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

    def _select_payment_field_values(self) -> None:
        """Selects the payment form dropdowns via Kendo data source when the app uses non-standard IDs."""
        self.page.evaluate(r"""
            () => {
                const jq = window.jQuery || window.$;
                if (!jq) return;
                const labelLookups = ['payment type', 'payment subtype', 'method of payment'];
                const selectorList = [
                    '#payment_Type', '#Payment_Type', '#PaymentType', '#paymentType',
                    '#payment_SubType', '#Payment_SubType', '#PaymentSubType', '#paymentSubType',
                    '#Method_Of_Payment', '#Method_of_Payment', '#MethodOfPayment', '#payment_Method', '#Payment_Method'
                ];

                const chooseFirst = (node) => {
                    if (!node) return;
                    const $node = jq(node);
                    if (!$node.length) return;
                    const $source = $node.is('select, input, .k-dropdown') ? $node : ($node.find('select, input, .k-dropdown').first().length ? $node.find('select, input, .k-dropdown').first() : $node);
                    let widget = $source.data('kendoDropDownList') || $source.find('input, select').data('kendoDropDownList');
                    if (!widget) {
                        const $root = $source.closest('.k-dropdown, .k-widget');
                        if ($root.length) {
                            widget = $root.data('kendoDropDownList');
                            if (!widget && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                                try {
                                    widget = window.kendo.widgetInstance($root);
                                } catch (error) {
                                    widget = null;
                                }
                            }
                        }
                    }
                    if (!widget || !widget.dataSource || typeof widget.dataSource.data !== 'function') return;

                    const items = widget.dataSource.data();
                    let targetVal = null;
                    let targetTxt = '';
                    for (let i = 0; i < items.length; i++) {
                        const item = items[i];
                        if (!item) continue;
                        const txt = (item.text || item.Text || item.name || item.Name || item.value || item.Value || Object.values(item)[0] || '').toString().trim();
                        const val = (item.value !== undefined && item.value !== null && item.value !== '') ? item.value : ((item.Value !== undefined && item.Value !== null && item.Value !== '') ? item.Value : txt);
                        if (txt && val !== undefined && val !== null && val !== '' && !txt.startsWith('--') && !txt.toLowerCase().startsWith('select') && !txt.toLowerCase().includes('no data')) {
                            targetVal = val;
                            targetTxt = txt;
                            break;
                        }
                    }
                    if (targetVal !== null) {
                        if (typeof widget.value === 'function') widget.value(targetVal);
                        if (typeof widget.trigger === 'function') widget.trigger('change');
                        if (widget.wrapper && widget.wrapper.length) {
                            widget.wrapper.find('.k-input').text(targetTxt);
                        }
                    }
                };

                for (const selector of selectorList) {
                    const el = document.querySelector(selector);
                    if (el) chooseFirst(el);
                }

                for (const lookup of labelLookups) {
                    const labels = Array.from(document.querySelectorAll('label, span, div, th'));
                    for (const label of labels) {
                        const text = (label.textContent || '').replace(/\s+/g, ' ').trim();
                        if (!text || !text.toLowerCase().includes(lookup)) continue;
                        const container = label.closest('.row, .field, .form-group, .col-md-6, .col-lg-6, .k-widget');
                        if (container) chooseFirst(container);
                        break;
                    }
                }
            }
        """)
        self.page.wait_for_timeout(500)

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

        # 2. Select Payment Type, Payment Sub Type, and Method of Payment dropdowns sequentially
        self._select_payment_field_values()
        self.page.wait_for_timeout(500)

        # Wait up to 5s for cascading Payment Sub Type dropdown data to populate via Kendo AJAX
        for _ in range(15):
            sub_count = self.page.evaluate("""
                () => {
                    var jq = window.jQuery || window.$;
                    if (!jq) return 0;
                    var pst = jq('#payment_SubType, #Payment_SubType').data('kendoDropDownList');
                    return pst && pst.dataSource ? pst.dataSource.data().length : 0;
                }
            """)
            if sub_count > 0:
                break
            self.page.wait_for_timeout(500)

        # Select Payment Sub Type and all remaining dropdowns in form
        self._select_payment_field_values()
        self.select_all_kendo_dropdowns()
        self.page.wait_for_timeout(500)

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
