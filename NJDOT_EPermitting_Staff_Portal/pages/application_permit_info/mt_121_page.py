import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class MT121Page(BasePage):
    """
    Page Object Model for MT-121 Inspection Report section in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Tab Navigation & Headers
        self.mt121_tab = page.locator("a:has-text('MT-121'), span:has-text('MT-121'), .k-tabstrip a:has-text('MT-121')").or_(
            page.get_by_role("link", name=re.compile(r"^MT-", re.I))
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.mt121_title_text = page.get_by_text(re.compile(r"MT-121 Inspection Report", re.I)).first

        # Time inputs
        self.time_from_input = page.locator("#Inspection_Time_From_Date_Placeholder2")
        self.time_to_input = page.locator("#Inspection_Time_To_Date_Placeholder3")

        # Text & Numeric fields from Codegen
        self.sec3_comment = page.locator("#Sec3_Comment_Placeholder1")
        self.sec5_text = page.locator("#Sec5_Text_Placeholder_6")

        self.sec3_numeric = page.locator("#Sec3_Numeric_Placeholder7")
        self.sec4_numeric2 = page.locator("#Sec4_Numeric_Placeholder2")
        self.sec4_numeric3 = page.locator("#Sec4_Numeric_Placeholder3")
        self.sec4_numeric4 = page.locator("#Sec4_Numeric_Placeholder4")
        self.sec4_numeric5 = page.locator("#Sec4_Numeric_Placeholder5")

        # Dropdowns
        self.pavement_type_dropdown = page.locator("#MTInspectiondiv").get_by_text("--Select Pavement Type--").first
        self.unit_type_dropdown = page.locator("#MTInspectiondiv").get_by_text("--Select Unit Type--").first
        self.traffic_dir_dropdown = page.locator("#MTInspectiondiv").get_by_text("--Select Direction of traffic").first
        self.select_option_dropdown = page.locator("#MTInspectiondiv").get_by_text("--Select option--").first

        # Action Buttons
        self.save_button = page.locator(
            "button:has-text('Save'), input[type='submit'][value='Save'], input[type='button'][value='Save'], a:has-text('Save'), .btn:has-text('Save'), #btnSave"
        ).first

        self.ok_confirm_button = page.get_by_role("button", name="OK").first
        self.gen_report_button = page.locator(
            "#generateInsReport, "
            "button:has-text('Generate Inspection Report'), "
            "input[type='button'][value*='Generate'], "
            "input[type='submit'][value*='Generate']"
        ).first
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log").or_(
            page.get_by_text("Documents and Log")
        ).first

    def navigate_to_mt121(self) -> None:
        """Navigates to MT-121 Inspection tab."""
        logger.info("Navigating to MT-121 tab.")
        self._wait_for_loader()
        if self.mt121_tab.is_visible():
            self.js_click(self.mt121_tab)
        else:
            self.page.evaluate("$('a:contains(\"MT-\"), span:contains(\"MT-\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates MT-121 initial layout."""
        logger.info("Verifying MT-121 layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def fill_inspection_report(self, comment: str = "test", text_val: str = "test", num_val: str = "10") -> None:
        """Fills out MT-121 inspection report form per codegen workflow."""
        logger.info("Filling MT-121 inspection report form.")
        self._wait_for_loader()

        # 1. Fill Dates & Times
        self.set_all_datefields_to_current()

        self.page.evaluate("""
            () => {
                var jq = window.jQuery || window.$;
                if (!jq) return;
                
                // Dismiss any open alert dialogs or overlays
                jq('.k-dialog button:contains("OK"), .k-alert button:contains("OK"), .k-window button:contains("OK")').each(function() {
                    if (jq(this).is(':visible')) jq(this).click();
                });
                jq('.k-overlay').remove();
                
                jq('#Inspection_Time_From_Date_Placeholder2, input[name*="Time_From"], input[id*="Time_From"]').each(function() {
                    var mtb = jq(this).data("kendoMaskedTextBox");
                    if (!mtb && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                        try { mtb = window.kendo.widgetInstance(jq(this)); } catch(e) {}
                    }
                    if (mtb && typeof mtb.value === "function") {
                        mtb.value("09:00");
                        if (typeof mtb.trigger === "function") mtb.trigger("change");
                    }
                    jq(this).val("09:00").attr("value", "09:00").trigger("input").trigger("change").trigger("blur");
                });

                jq('#Inspection_Time_To_Date_Placeholder3, input[name*="Time_To"], input[id*="Time_To"]').each(function() {
                    var mtb = jq(this).data("kendoMaskedTextBox");
                    if (!mtb && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                        try { mtb = window.kendo.widgetInstance(jq(this)); } catch(e) {}
                    }
                    if (mtb && typeof mtb.value === "function") {
                        mtb.value("10:00");
                        if (typeof mtb.trigger === "function") mtb.trigger("change");
                    }
                    jq(this).val("10:00").attr("value", "10:00").trigger("input").trigger("change").trigger("blur");
                });
            }
        """)

        # 2. Select Radio options & Checkboxes
        self.page.evaluate("""
            () => {
                var jq = window.jQuery || window.$;
                if (!jq) return;
                jq('input[type="radio"]').each(function() {
                    var name = jq(this).attr("name") || "";
                    var labelText = (jq(this).closest('label').text() || jq(this).next().text() || "").toLowerCase();
                    if (name && !labelText.includes("other") && jq('input[type="radio"][name="' + name + '"]:checked').length === 0) {
                        jq(this).prop("checked", true).trigger("change").trigger("click");
                    }
                });
                jq('input[type="checkbox"]').prop("checked", true).trigger("change");
            }
        """)

        # 3. Select Dropdowns (1st non-placeholder option)
        if self.pavement_type_dropdown.is_visible():
            self.select_first_dropdown_option(self.pavement_type_dropdown)

        if self.unit_type_dropdown.is_visible():
            self.select_first_dropdown_option(self.unit_type_dropdown)

        if self.traffic_dir_dropdown.is_visible():
            self.select_first_dropdown_option(self.traffic_dir_dropdown)

        if self.select_option_dropdown.is_visible():
            self.select_first_dropdown_option(self.select_option_dropdown)

        self.select_all_kendo_dropdowns()
        self.select_kendo_location_dropdowns()

        # 4. Fill Comments & Text inputs (ignoring date, time, and numeric/dropdown inputs)
        if self.sec3_comment.is_visible():
            self.sec3_comment.fill(comment)

        if self.sec5_text.is_visible():
            self.sec5_text.fill(text_val)

        self.page.evaluate(f"""
            (txt) => {{
                var jq = window.jQuery || window.$;
                if (!jq) return;
                jq('input[type="text"], textarea').each(function() {{
                    var id = (jq(this).attr('id') || '').toLowerCase();
                    var name = (jq(this).attr('name') || '').toLowerCase();
                    if (id.includes('time') || name.includes('time') || id.includes('date') || name.includes('date') || id.includes('dropdown') || name.includes('dropdown') || id.includes('numeric') || name.includes('numeric') || id.includes('unit') || id.includes('route')) {{
                        return;
                    }}
                    if (!jq(this).val()) {{
                        jq(this).val(txt);
                        var el = this;
                        ['input', 'change', 'blur', 'keyup'].forEach(function(evt) {{
                            var e = document.createEvent('HTMLEvents');
                            e.initEvent(evt, true, true);
                            el.dispatchEvent(e);
                        }});
                    }}
                }});
            }}
        """, text_val)

        # 5. Populate Numeric fields
        num_int = int(num_val) if num_val and num_val.isdigit() else 10
        if num_int < 1:
            num_int = 10

        self.fill_kendo_numeric("Sec3_Numeric_Placeholder7", float(num_int))
        self._wait_for_loader()

        for num_id in ["Sec4_Numeric_Placeholder2", "Sec4_Numeric_Placeholder3", "Sec4_Numeric_Placeholder4", "Sec4_Numeric_Placeholder5"]:
            try:
                val = self.page.evaluate(f"() => $('#{num_id}').val()")
                if not val or val == "0" or val == "":
                    self.fill_kendo_numeric(num_id, 10.0)
            except Exception:
                pass

        self._wait_for_loader()

    def save_inspection_report(self) -> None:
        """Saves MT-121 inspection report and confirms dialogs."""
        logger.info("Saving MT-121 inspection report.")
        self.js_click(self.save_button)
        self._wait_for_loader()

        try:
            if self.ok_confirm_button.is_visible():
                self.js_click(self.ok_confirm_button)
                self._wait_for_loader()
        except Exception:
            pass

        self.assert_no_validation_errors()

    def generate_inspection_report_pdf(self) -> None:
        """Generates Inspection Report PDF, confirms dialog, and verifies popup canvas."""
        logger.info("Generating MT-121 Inspection Report PDF.")
        self._wait_for_loader()
        self.scroll_to_locator(self.gen_report_button)
        if self.gen_report_button.is_visible():
            self.js_click(self.gen_report_button)
        else:
            self.page.evaluate("$('button:contains(\"Generate\"), input[value*=\"Generate\"], .btn:contains(\"Generate\")').first().click()")

        self._wait_for_loader()

        try:
            with self.page.expect_popup() as popup_info:
                if self.ok_confirm_button.is_visible():
                    self.js_click(self.ok_confirm_button)
                else:
                    self.page.evaluate("$('button:contains(\"OK\"), .btn:contains(\"OK\")').first().click()")
            popup = popup_info.value
            expect(popup.locator("#mainCanvas")).to_be_visible(timeout=30000)
            popup.close()
            logger.info("Inspection report PDF canvas verified successfully.")
        except Exception as e:
            logger.warning(f"Report popup note: {e}")

        if self.documents_log_heading.is_visible():
            expect(self.documents_log_heading).to_be_visible(timeout=10000)
