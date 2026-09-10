import logging
import re
from pathlib import Path
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)

class KendoUtils:
    """
    Centralized handler for all advanced Kendo UI components.
    Prevents duplication of dropdown interactions, fast-pagination, and file uploads.
    """
    
    @staticmethod
    def select_dropdown_option(page: Page, dropdown_locator: Locator, option_text: str) -> None:
        """
        Dynamically interacts with a Kendo DropDownList and selects the specified text.
        """
        try:
            dropdown_locator.click(timeout=5000)
        except Exception:
            dropdown_locator.click(force=True)
            
        # Wait for the popup list to render
        option = page.locator("li[role='option']").filter(has_text=option_text).first
        option.wait_for(state="visible", timeout=10000)
        option.click()

    @staticmethod
    def upload_file(page: Page, dropzone_locator: Locator, file_path: str) -> None:
        """
        Robustly handles Kendo UI asynchronous file uploads.
        """
        # Ensure file exists
        path = Path(file_path)
        if not path.is_file():
            # If the user passed a relative path, resolve it relative to testdata
            path = Path.cwd() / "testdata" / file_path
            
        logger.info(f"Uploading file: {path.name}")
        
        # Intercept the native file chooser and route the local file into it
        with page.expect_file_chooser() as fc_info:
            dropzone_locator.click(force=True)
        file_chooser = fc_info.value
        file_chooser.set_files(str(path.absolute()))
        
        # Wait for the Kendo UI green checkmark icon to confirm the file chunk uploaded securely
        page.locator(".k-file-success, .k-i-check").first.wait_for(state="visible", timeout=30000)

    @staticmethod
    def fast_paginate_to_last_page(page: Page, next_btn: Locator, last_btn: Locator, page_input: Locator, wait_callback) -> None:
        """
        Extremely fast pagination algorithm. Avoids clicking 'Next' 200 times.
        Requires a 'wait_callback' (like BasePage._wait_for_loader) to pause between clicks.
        """
        logger.info("Attempting fast navigation to the last page of the grid...")
        try:
            last_btn.wait_for(state="visible", timeout=5000)
            last_btn.click()
            wait_callback()
        except Exception:
            # Fallback: use page input
            KendoUtils._go_to_last_page_using_input(page, next_btn, page_input, wait_callback)

    @staticmethod
    def _go_to_last_page_using_input(page: Page, next_btn: Locator, page_input: Locator, wait_callback) -> None:
        """Fallback pagination using the Kendo UI page number input."""
        logger.info("Fallback: attempting to use Kendo page input for fast navigation...")
        try:
            page_text = page.locator("text=of").inner_text(timeout=5000)
            total_pages = int(page_text.split("of")[1].strip())

            page_input.fill(str(total_pages))
            page_input.press("Enter")
            wait_callback()
        except Exception:
            # Final fallback (rare) - iterate manually
            logger.info("Final fallback: iterating through pages manually...")
            while True:
                class_attr = next_btn.get_attribute("class") or ""
                if "k-state-disabled" in class_attr:
                    break

                next_btn.click(force=True)
                wait_callback()

    @staticmethod
    def verify_grid_records(grid_container: Locator, no_records_msg: Locator) -> bool:
        """
        Dynamically waits for actual grid rows to render OR the empty-state message.
        Returns True if records exist, False if empty.
        """
        logger.info("Verifying grid records...")
        grid_rows = grid_container.locator("tbody tr")
        try:
            grid_rows.first.or_(no_records_msg).wait_for(state="visible", timeout=15000)
        except Exception as e:
            raise AssertionError(f"❌ Grid failed to load entirely. Neither records nor empty-state appeared. {e}")

        if no_records_msg.is_visible():
            logger.info("Grid is empty (No records available).")
            return False

        count = grid_rows.count()
        logger.info(f"Found {count} records on current page.")
        if count == 0:
            return False
            
        return True

    @staticmethod
    def select_dropdown_by_id(page: Page, element_id: str, value_text: str = None) -> None:
        """
        Selects a Kendo DropDownList option by element ID using Kendo API.
        If value_text is provided, matches and selects that option.
        Otherwise, selects the first valid (non-placeholder) option.
        """
        logger.info(f"Selecting '{value_text or 'first valid'}' for Kendo widget: {element_id}")
        try:
            page.wait_for_function(
                f"""() => {{
                    var jq = window.jQuery || window.$;
                    if (!jq) return false;
                    var el = jq("{element_id}");
                    if (el.length === 0) return false;
                    var dropdown = el.data("kendoDropDownList");
                    return dropdown && dropdown.dataSource && dropdown.dataSource.data().length > 0;
                }}""",
                timeout=15000
            )
        except Exception as e:
            logger.warning(f"Wait for Kendo dropdown {element_id} note: {e}")

        result = page.evaluate(
            """([sel, valText]) => {
                var jq = window.jQuery || window.$;
                if (!jq) return null;
                var el = jq(sel);
                var dropdown = el.data("kendoDropDownList");
                if (!dropdown) return null;
                
                var index = -1;
                if (valText) {
                    var data = dropdown.dataSource.data();
                    var textProp = dropdown.options.dataTextField;
                    for (var i = 0; i < data.length; i++) {
                        var itemText = data[i][textProp];
                        if (itemText && itemText.toString().trim() === valText) {
                            index = i;
                            break;
                        }
                    }
                }
                
                var selectIndex = -1;
                if (index !== -1) {
                    selectIndex = dropdown.options.optionLabel ? index + 1 : index;
                } else {
                    selectIndex = dropdown.options.optionLabel ? 1 : 0;
                }
                
                dropdown.select(selectIndex);
                dropdown.trigger("change");
                if (dropdown.element && dropdown.element.length) {
                    dropdown.element.trigger("change").trigger("input");
                    try { if (jq.validator) dropdown.element.valid(); } catch(e) {}
                }
                return dropdown.text();
            }""",
            [element_id, value_text]
        )
        if result:
            logger.info(f"Successfully selected '{result}' in {element_id}")
        else:
            logger.warning(f"Failed to select option in {element_id}")
