import logging
from datetime import datetime
from typing import Optional, Union, List
from playwright.sync_api import Page, Locator, expect

logger = logging.getLogger(__name__)


class KendoDropdown:
    """
    Dedicated Page Component representing Kendo UI DropDownList widgets.
    Encapsulates JS API and UI interactions for robust, cross-portal dropdown control.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def select_by_id(self, field_id: str, option_text: Optional[str] = None, index: int = 1) -> bool:
        """
        Selects an option from a Kendo DropDownList by element ID.
        If option_text is provided, selects matching item (case-insensitive);
        otherwise falls back to selecting by index. Dispatches change event.
        """
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{clean_id}').data('kendoDropDownList');
                    if (!ddl) return false;
                    const target = '{option_text or ""}'.toLowerCase();
                    if (target) {{
                        const data = ddl.dataSource.data();
                        for (let i = 0; i < data.length; i++) {{
                            const text = (ddl.text(data[i]) || '').toLowerCase();
                            if (text.includes(target)) {{
                                ddl.select(i + (ddl.options.optionLabel ? 1 : 0));
                                ddl.trigger('change');
                                return true;
                            }}
                        }}
                    }}
                    if (ddl.dataSource.data().length > 0) {{
                        ddl.select({index});
                        ddl.trigger('change');
                        return true;
                    }}
                    return false;
                }})();
                """
            )
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_by_id failed for #{clean_id}: {e}")
            return False

    def select_by_locator(self, dropdown_locator: Union[Locator, str], option_text: str, timeout_ms: int = 5000) -> bool:
        """
        Opens a Kendo UI DropDownList wrapper via UI click and selects option by visible text.
        """
        try:
            loc = dropdown_locator if isinstance(dropdown_locator, Locator) else self.page.locator(dropdown_locator)
            if loc.is_visible(timeout=timeout_ms):
                loc.click(force=True)
                self.page.wait_for_timeout(300)
                option = self.page.locator(".k-animation-container:visible li, .k-list-container:visible li").filter(
                    has_text=option_text
                ).first
                if option.is_visible(timeout=timeout_ms):
                    option.click(force=True)
                    return True
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_by_locator failed for '{option_text}': {e}")
        return False

    def select(self, target: Union[Locator, str], option_text: Optional[str] = None, index: int = 1, timeout_ms: int = 5000) -> bool:
        """
        Polymorphic select:
        - If target is a string ID/selector, attempts select_by_id first using Kendo JS API.
        - Falls back to select_by_locator (UI-based selection).
        """
        if isinstance(target, str):
            clean_id = target.lstrip("#")
            if " " not in clean_id and (clean_id.isalnum() or "_" in clean_id or "-" in clean_id):
                if self.select_by_id(clean_id, option_text=option_text, index=index):
                    return True
        return self.select_by_locator(target, option_text=option_text or "", timeout_ms=timeout_ms)

    def get_options(self, field_id: str) -> List[str]:
        """Returns all text options available in the Kendo DropDownList dataSource."""
        clean_id = field_id.lstrip("#")
        try:
            return self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{clean_id}').data('kendoDropDownList');
                    if (!ddl) return [];
                    return ddl.dataSource.data().map(x => ddl.text(x) || '');
                }})();
                """
            )
        except Exception:
            return []

    def get_selected_text(self, field_id: str) -> str:
        """Returns currently selected text in the Kendo DropDownList."""
        clean_id = field_id.lstrip("#")
        try:
            return self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{clean_id}').data('kendoDropDownList');
                    return ddl ? ddl.text() : '';
                }})();
                """
            ) or ""
        except Exception:
            return ""

    def select_first_valid_by_id(self, field_id: str) -> str:
        """
        Uses Kendo DropDownList JS API to select the 1st valid non-placeholder option.
        Triggers 'change' event and returns the selected text immediately.
        """
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{clean_id}').data('kendoDropDownList');
                    if (!ddl) return null;
                    const data = ddl.dataSource.data();
                    if (!data || data.length === 0) return null;
                    const targetIndex = ddl.options.optionLabel ? 1 : 0;
                    ddl.select(targetIndex);
                    ddl.trigger('change');
                    return ddl.text();
                }})();
                """
            )
            if res:
                self.logger.info(f"Selected 1st valid option for #{clean_id} via API: '{res}'")
                return str(res)
        except Exception as e:
            self.logger.warning(f"select_first_valid_by_id failed for #{clean_id}: {e}")
        return ""

    def select_first_valid_option(self, dropdown_locator: Union[Locator, str], timeout_ms: int = 5000) -> str:
        """
        Dynamically selects the 1st valid (non-placeholder) option in the list.
        Prefers direct Kendo JS API selection for speed and zero lingering popups;
        falls back to clean UI interaction.
        """
        self.logger.info("Selecting 1st valid dropdown option")

        # 1. Fast path: If string ID or locator has an identifiable Kendo input, select via API
        if isinstance(dropdown_locator, str) and ("#" in dropdown_locator or dropdown_locator.isidentifier()):
            clean_id = dropdown_locator.lstrip("#")
            selected = self.select_first_valid_by_id(clean_id)
            if selected:
                return selected

        loc = dropdown_locator if isinstance(dropdown_locator, Locator) else self.page.locator(dropdown_locator)
        expect(loc).to_be_visible(timeout=timeout_ms)

        try:
            widget_id = loc.evaluate(
                """
                el => {
                    const input = (el.tagName === 'INPUT' || el.tagName === 'SELECT')
                        ? el
                        : (el.querySelector('input, select') || el.previousElementSibling);
                    return (input && input.id) ? input.id : '';
                }
                """
            )
            if widget_id:
                selected = self.select_first_valid_by_id(widget_id)
                if selected:
                    return selected
        except Exception:
            pass

        # 2. UI interaction fallback
        loc.click()
        self.page.wait_for_timeout(200)

        items = self.page.locator(".k-animation-container:visible .k-list-container li.k-item")
        expect(items.first).to_be_visible(timeout=timeout_ms)
        count = items.count()

        selected_text = ""
        for i in range(count):
            item = items.nth(i)
            text = item.inner_text().strip()
            # Skip placeholder options (e.g. '--Select--', '-- Select Option--')
            if text and not text.startswith("--") and not text.lower().startswith("select"):
                self.logger.info(f"Selected 1st valid option: '{text}'")
                item.click()
                selected_text = text
                break

        # Clean fallback if no item matched the exclusion filter
        if not selected_text and count > 0:
            fallback_item = items.nth(1 if count > 1 else 0)
            selected_text = fallback_item.inner_text().strip()
            fallback_item.click()

        # Wait for popup to dismiss naturally; if still open, send Escape
        try:
            self.page.locator(".k-animation-container:visible").wait_for(state="hidden", timeout=1200)
        except Exception:
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass

        return selected_text



class KendoDatePicker:
    """
    Dedicated Page Component representing Kendo UI DatePicker widgets.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def set_date_by_id(self, field_id: str, date_str: str) -> bool:
        """Sets date string in a Kendo DatePicker via JS API and triggers all validation events."""
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const inp = $('#{clean_id}');
                    if (!inp.length) return false;
                    const dp = inp.data('kendoDatePicker');
                    if (dp && typeof dp.value === 'function') {{
                        dp.value('{date_str}');
                        if (typeof dp.trigger === 'function') dp.trigger('change');
                    }}
                    inp.val('{date_str}').attr('value', '{date_str}').trigger('input').trigger('change').trigger('blur');
                    return true;
                }})();
                """
            )
            # Also fill via Playwright if visible to ensure browser-level event dispatch
            try:
                inp_loc = self.page.locator(f"#{clean_id}")
                if inp_loc.is_visible():
                    inp_loc.fill(date_str)
                    inp_loc.press("Tab")
            except Exception:
                pass
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoDatePicker set_date_by_id failed for #{clean_id}: {e}")
            return False

    def select_present_day_date(
        self,
        container: Optional[Union[Locator, str]] = None,
        field_id: Optional[str] = None,
        timeout_ms: int = 3000,
    ) -> str:
        """
        Selects the present day (today's) date in the Kendo DatePicker widget.
        Directly populates and verifies the date value, avoiding redundant calendar waits.
        """
        today_str = datetime.now().strftime("%m/%d/%Y")
        today_day = str(datetime.now().day)
        self.logger.info(f"Setting present day date: {today_str}")

        # 1. If field_id is provided, set via JS API and direct fill immediately
        if field_id:
            clean_id = field_id.lstrip("#")
            self.set_date_by_id(clean_id, today_str)
            # Verify input value is populated
            try:
                inp = self.page.locator(f"#{clean_id}")
                if inp.count() > 0 and inp.first.input_value() == today_str:
                    return today_str
            except Exception:
                pass

        scope = (
            (container if isinstance(container, Locator) else self.page.locator(container))
            if container is not None
            else self.page
        )

        # 2. Check if an input exists inside scope and fill it directly
        try:
            date_input = scope.locator("input[data-role='datepicker'], .k-datepicker input").first
            if date_input.count() > 0 and date_input.is_visible():
                date_input.click(force=True)
                date_input.fill(today_str)
                date_input.press("Tab")
                return today_str
        except Exception:
            pass

        # 3. Calendar popup selection fallback
        date_btn = scope.locator(".k-datepicker .k-select, button:has-text('select'), span.k-select").first
        if date_btn.is_visible(timeout=1000):
            try:
                date_btn.click(force=True)
                cal = self.page.locator(".k-calendar:visible").first
                if cal.is_visible(timeout=1000):
                    today_cell = cal.locator("td.k-today a, td.k-state-focused a").first
                    if today_cell.is_visible(timeout=500):
                        today_cell.click(force=True)
                    else:
                        day_link = cal.locator("td:not(.k-other-month) a").filter(has_text=today_day).first
                        if day_link.is_visible(timeout=500):
                            day_link.click(force=True)
            except Exception as e:
                self.logger.warning(f"Calendar popup selection note: {e}")

        return today_str



class KendoNumericTextBox:
    """
    Dedicated Page Component representing Kendo UI NumericTextBox widgets.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def set_value_by_id(self, field_id: str, value: float) -> bool:
        """Sets numeric value in a Kendo NumericTextBox and triggers change event."""
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const num = $('#{clean_id}').data('kendoNumericTextBox');
                    if (num) {{
                        num.value({value});
                        num.trigger('change');
                        return true;
                    }}
                    $('#{clean_id}').val({value}).trigger('change');
                    return true;
                }})();
                """
            )
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoNumericTextBox set_value_by_id failed for #{clean_id}: {e}")
            return False
