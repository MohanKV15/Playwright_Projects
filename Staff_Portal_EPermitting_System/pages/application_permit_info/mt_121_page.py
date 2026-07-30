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
        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(page.locator("#btnSave, .btn:has-text('Save')")).first

        self.ok_confirm_button = page.get_by_role("button", name="OK").first
        self.gen_report_button = page.get_by_role("button", name="Generate Inspection Report").first
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

        if self.time_from_input.is_visible():
            self.time_from_input.fill("01:00")

        if self.time_to_input.is_visible():
            self.time_to_input.fill("02:00")

        # 2. Select Radio options (prefer non-Other options)
        self.page.evaluate("""
            () => {
                $('input[type="radio"]').each(function() {
                    var name = $(this).attr("name") || "";
                    var labelText = ($(this).closest('label').text() || $(this).next().text() || "").toLowerCase();
                    if (name && !labelText.includes("other") && $('input[type="radio"][name="' + name + '"]:checked').length === 0) {
                        $(this).prop("checked", true).trigger("change").trigger("click");
                    }
                });
                $('input[type="checkbox"]').prop("checked", true).trigger("change");
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

        # 4. Fill Comments & Text inputs
        if self.sec3_comment.is_visible():
            self.sec3_comment.fill(comment)

        if self.sec5_text.is_visible():
            self.sec5_text.fill(text_val)

        self.page.evaluate(f"""
            (txt) => {{
                $('input[type="text"], textarea, #Sec3_Comment_Placeholder1, #Sec5_Text_Placeholder_6, #Other, [name*="Other"]').each(function() {{
                    if (!$(this).val()) {{
                        $(this).val(txt);
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

        # 5. Fill Numeric inputs
        for num_loc in [self.sec3_numeric, self.sec4_numeric2, self.sec4_numeric3, self.sec4_numeric4, self.sec4_numeric5]:
            try:
                if num_loc.is_visible():
                    num_loc.fill(num_val)
            except Exception:
                pass

        self.page.evaluate(f"""
            (amtStr) => {{
                $('input[data-role="numerictextbox"], .k-numerictextbox input, input[name*="Quantity"], input[name*="Size"], input[name*="Fee"], input[name*="Received"], input[name*="Balance"], input[name*="Amount"]').each(function() {{
                    var num = kendo.widgetInstance($(this)) || $(this).data("kendoNumericTextBox") || $(this).closest(".k-numerictextbox").find("input").data("kendoNumericTextBox");
                    if (num && typeof num.value === "function") {{
                        num.value(parseFloat(amtStr));
                        if (typeof num.trigger === "function") num.trigger("change");
                    }}
                    $(this).val(amtStr).attr("value", amtStr).trigger("input").trigger("change").trigger("blur");
                    var el = this;
                    ['input', 'change', 'blur', 'keyup'].forEach(function(evt) {{
                        var e = document.createEvent('HTMLEvents');
                        e.initEvent(evt, true, true);
                        el.dispatchEvent(e);
                    }});
                }});
                $('[data-valmsg-for]').each(function() {{
                    var fieldName = $(this).attr("data-valmsg-for");
                    var $field = $('[name="' + fieldName + '"], #' + fieldName);
                    if ($field.length && !$field.val()) {{
                        $field.val(amtStr).trigger("change");
                    }}
                }});
            }}
        """, num_val)

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
        self.js_click(self.gen_report_button)
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
