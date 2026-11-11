import logging
import re
from datetime import datetime
from typing import Optional, Union, List
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)


class KendoDropdown:
    """
    Dedicated Page Component representing Kendo UI DropDownList widgets.
    Encapsulates both UI interaction and internal Kendo JS API for robust control.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def select_by_locator(self, dropdown_locator: Union[Locator, str], option_text: str, timeout_ms: int = 5000) -> bool:
        """
        Opens a Kendo UI DropDownList wrapper via UI click and selects option by visible text.
        """
        try:
            loc = dropdown_locator if isinstance(dropdown_locator, Locator) else self.page.locator(dropdown_locator)
            loc.first.wait_for(state="visible", timeout=timeout_ms)
            loc.first.click(force=True)
            self.page.wait_for_timeout(300)

            option = self.page.get_by_role("option", name=re.compile(rf"^\s*{re.escape(option_text)}\s*$", re.I)).first
            if not option.is_visible(timeout=1000):
                option = self.page.locator(
                    "li[role='option']:visible, .k-animation-container:visible li, .k-list-container:visible li"
                ).filter(has_text=re.compile(rf"^\s*{re.escape(option_text)}\s*$", re.I)).first

            if not option.is_visible(timeout=1000):
                option = self.page.locator(
                    "li[role='option']:visible, .k-animation-container:visible li, .k-list-container:visible li"
                ).filter(has_text=option_text).first

            if option.is_visible(timeout=timeout_ms):
                option.click(force=True)
                self.page.wait_for_timeout(300)
                return True
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_by_locator failed for '{option_text}': {e}")
        return False

    def select_by_id(self, field_id: str, option_text: Optional[str] = None, index: int = 1) -> bool:
        """
        Selects an option from a Kendo DropDownList by element ID using Kendo JS API.
        Supports varied dataSource text fields (Text, Definition, poc_name, etc.).
        """
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const jq = window.jQuery || window.$;
                    if (!jq) return false;
                    const ddl = jq('#{clean_id}').data('kendoDropDownList');
                    if (!ddl) return false;
                    const target = '{option_text or ""}'.toLowerCase().trim();
                    const textField = ddl.options.dataTextField || 'Text';
                    const data = ddl.dataSource.data();
                    if (target) {{
                        for (let i = 0; i < data.length; i++) {{
                            const item = data[i];
                            const text = (item[textField] || item.Definition || item.poc_name || item.Text || item.text || '').toString().toLowerCase();
                            if (text && (text.includes(target) || target.includes(text))) {{
                                ddl.select(i + (ddl.options.optionLabel ? 1 : 0));
                                ddl.trigger('change');
                                return true;
                            }}
                        }}
                    }}
                    if (data.length > 0) {{
                        const idx = ddl.options.optionLabel ? 1 : 0;
                        ddl.select(idx);
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

    def select_first_option(self, target: Optional[Union[Locator, str]] = None) -> bool:
        """
        Selects the first valid data option in a Kendo dropdown, skipping optionLabel/placeholder.
        """
        return self.select_option_by_index(target=target, index=0)

    def select_second_option(self, target: Optional[Union[Locator, str]] = None) -> bool:
        """
        Selects the 2nd valid data option in a Kendo dropdown, skipping optionLabel/placeholder.
        Falls back to 1st option if only 1 option is available.
        """
        return self.select_option_by_index(target=target, index=1)

    def select_option_by_index(self, target: Optional[Union[Locator, str]] = None, index: int = 1) -> bool:
        """
        Selects an option from a Kendo dropdown by 0-based index among valid data options,
        skipping placeholder/optionLabel (e.g. index=1 selects the 2nd valid data option).
        """
        try:
            if target:
                loc = target if isinstance(target, Locator) else self.page.locator(target)
                if loc.first.is_visible():
                    loc.first.click(force=True)
                    self.page.wait_for_timeout(350)

            self.page.wait_for_selector(
                "ul.k-list[role='listbox']:visible, .k-list-container:visible, .k-animation-container:visible",
                timeout=5000,
            )
            options = self.page.locator(
                ".k-animation-container:visible li[role='option'], .k-list-container:visible li[role='option'], ul[role='listbox']:visible li[role='option'], .k-animation-container:visible li"
            )
            count = options.count()
            valid_opts = []
            for i in range(count):
                opt = options.nth(i)
                txt = opt.inner_text().strip()
                if txt and not txt.startswith("--") and not txt.lower().startswith("select") and "no data" not in txt.lower():
                    valid_opts.append(opt)

            if valid_opts:
                target_idx = index if index < len(valid_opts) else 0
                chosen = valid_opts[target_idx]
                self.logger.info(f"KendoDropdown selected option ({target_idx}): '{chosen.inner_text().strip()}'")
                chosen.click(force=True)
                self.page.wait_for_timeout(300)
                return True
            elif count > 0:
                target_idx = index if index < count else 0
                options.nth(target_idx).click(force=True)
                self.page.wait_for_timeout(300)
                return True
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_option_by_index({index}) failed: {e}")
        return False

    def select(self, target: Union[Locator, str], option_text: str, timeout_ms: int = 5000) -> bool:
        """
        Polymorphic select: tries select_by_id if target is an ID, falls back to select_by_locator.
        """
        if isinstance(target, str) and (target.isalnum() or target.startswith("#")):
            if self.select_by_id(target, option_text):
                return True
        return self.select_by_locator(target, option_text, timeout_ms=timeout_ms)


class KendoDatePicker:
    """
    Dedicated Page Component representing Kendo UI DatePicker widgets.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def set_date_by_id(self, field_id: str, date_str: str) -> bool:
        """Sets date string in a Kendo DatePicker and triggers change event."""
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const jq = window.jQuery || window.$;
                    if (!jq) return false;
                    const dp = jq('#{clean_id}').data('kendoDatePicker');
                    if (dp) {{
                        dp.value('{date_str}');
                        dp.trigger('change');
                        return true;
                    }}
                    jq('#{clean_id}').val('{date_str}').trigger('change');
                    return true;
                }})();
                """
            )
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoDatePicker set_date_by_id failed for #{clean_id}: {e}")
            return False

    def pick_date(self, trigger_locator: Optional[Union[Locator, str]] = None, day_text: Optional[str] = None, timeout_ms: int = 5000) -> bool:
        """
        Interacts with Kendo DatePicker UI: clicks the calendar icon and selects today
        or a specific day number link.
        """
        try:
            if trigger_locator:
                loc = trigger_locator if isinstance(trigger_locator, Locator) else self.page.locator(trigger_locator)
                loc.first.click(force=True)
                self.page.wait_for_timeout(400)

            # Strategy 1: User codegen pattern via aria-label 'Current focused date is'
            focused_cell = self.page.get_by_label(re.compile(r"Current focused date is", re.I))
            if focused_cell.count() > 0:
                day_link = focused_cell.first.get_by_role("link")
                if day_link.count() > 0:
                    day_link.first.click(force=True)
                    self.page.wait_for_timeout(300)
                    return True

            # Strategy 2: Specific day text inside visible popup container
            if day_text:
                day_link = self.page.locator(
                    f".k-animation-container:visible a:text-is('{day_text}'), .k-calendar:visible a:text-is('{day_text}')"
                ).first
                if day_link.is_visible(timeout=1500):
                    day_link.click(force=True)
                    self.page.wait_for_timeout(300)
                    return True

            # Strategy 3: Selected cell or today's link in visible calendar
            selected_cell = self.page.locator(
                ".k-animation-container:visible td.k-state-selected a, .k-animation-container:visible td.k-state-focused a, .k-animation-container:visible a.k-nav-today, [id*='cell_selected'] a"
            ).first
            if selected_cell.is_visible(timeout=1500):
                selected_cell.click(force=True)
                self.page.wait_for_timeout(300)
                return True

            # Strategy 4: Fallback to any day link in the calendar table
            first_day = self.page.locator(".k-animation-container:visible table.k-content td:not(.k-other-month) a").first
            if first_day.is_visible(timeout=1500):
                first_day.click(force=True)
                self.page.wait_for_timeout(300)
                return True

        except Exception as e:
            self.logger.warning(f"KendoDatePicker pick_date failed: {e}")
        return False

    def select_present_day(self, trigger_locator: Optional[Union[Locator, str]] = None, input_target: Optional[Union[Locator, str]] = None) -> bool:
        """
        Always selects the present day date in the Kendo DatePicker.
        Clicks the trigger and picks today's focused cell / date link,
        and ensures the date value (MM/DD/YYYY) is populated.
        """
        today = datetime.now()
        day_str = str(today.day)
        date_str = today.strftime("%m/%d/%Y")

        if trigger_locator:
            self.pick_date(trigger_locator=trigger_locator, day_text=day_str)

        if input_target:
            try:
                inp = input_target if isinstance(input_target, Locator) else self.page.locator(input_target)
                if inp.count() > 0 and inp.first.is_visible() and not inp.first.input_value():
                    inp.first.fill(date_str)
            except Exception:
                pass

        return True


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
                    const jq = window.jQuery || window.$;
                    if (!jq) return false;
                    const num = jq('#{clean_id}').data('kendoNumericTextBox');
                    if (num) {{
                        num.value({value});
                        num.trigger('change');
                    }}
                    jq('#{clean_id}').val('{value}').trigger('change');
                    return true;
                }})();
                """
            )
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoNumericTextBox set_value_by_id failed for #{clean_id}: {e}")
            return False

    def set_value(self, target: Union[Locator, str], value: float) -> bool:
        """Polymorphic setter for Kendo NumericTextBox."""
        if isinstance(target, str) and (target.startswith("#") or target.isalnum()):
            return self.set_value_by_id(target, value)
        try:
            loc = target if isinstance(target, Locator) else self.page.locator(target)
            if loc.is_visible():
                loc.fill(str(value))
                loc.press("Enter")
                return True
        except Exception as e:
            self.logger.warning(f"KendoNumericTextBox set_value failed: {e}")
        return False


class KendoCheckbox:
    """
    Dedicated Page Component representing Kendo UI Checkboxes.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def check(self, target: Union[Locator, str]) -> bool:
        """Checks a Kendo checkbox ensuring change event triggers."""
        try:
            loc = target if isinstance(target, Locator) else self.page.locator(target)
            if not loc.is_checked():
                loc.check(force=True)
                return True
        except Exception as e:
            self.logger.warning(f"KendoCheckbox check failed: {e}")
        return False


class KendoDialog:
    """
    Dedicated Page Component representing Kendo UI Dialogs, Windows, and Alerts.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def dismiss_alerts(self, timeout_ms: int = 3000) -> None:
        """Dismisses any open Kendo alert, dialog, or modal window."""
        try:
            dialogs = self.page.locator(".k-dialog:visible, .k-window:visible, .k-alert:visible")
            count = dialogs.count()
            if count > 0:
                for i in range(count):
                    dlg = dialogs.nth(i)
                    btn = dlg.locator("button:has-text('OK'), button:has-text('Cancel'), button:has-text('Close'), .k-i-close, .k-dialog-close").first
                    if btn.is_visible():
                        btn.click(force=True)
                        self.page.wait_for_timeout(200)
        except Exception as e:
            self.logger.debug(f"KendoDialog dismiss_alerts note: {e}")


class KendoControls:
    """
    Unified container aggregating all Kendo UI component handlers.
    """

    def __init__(self, page: Page):
        self.page = page
        self.dropdown = KendoDropdown(page)
        self.datepicker = KendoDatePicker(page)
        self.numeric = KendoNumericTextBox(page)
        self.checkbox = KendoCheckbox(page)
        self.dialog = KendoDialog(page)

