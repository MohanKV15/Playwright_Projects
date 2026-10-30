import logging
import re
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

            # Find option in visible popup listbox
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
        try:
            if target:
                loc = target if isinstance(target, Locator) else self.page.locator(target)
                if loc.first.is_visible():
                    loc.first.click()
                    self.page.wait_for_timeout(300)

            self.page.wait_for_selector(
                "ul.k-list[role='listbox']:visible, .k-list-container:visible, .k-animation-container:visible",
                timeout=5000
            )
            options = self.page.locator(
                ".k-animation-container:visible li[role='option'], .k-list-container:visible li[role='option'], ul[role='listbox']:visible li[role='option']"
            )
            count = options.count()
            if count > 0:
                for i in range(count):
                    opt = options.nth(i)
                    txt = opt.inner_text().strip()
                    if txt and not txt.startswith("--") and not txt.lower().startswith("select") and "no data" not in txt.lower():
                        self.logger.info(f"KendoDropdown selected option: '{txt}'")
                        opt.click()
                        self.page.wait_for_timeout(300)
                        return True
                idx = 1 if count > 1 else 0
                options.nth(idx).click()
                self.page.wait_for_timeout(300)
                return True
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_first_option failed: {e}")
        return False

    def select(self, target: Union[Locator, str], option_text: str, timeout_ms: int = 5000) -> bool:
        """
        Polymorphic select: tries select_by_id if target is an ID, falls back to select_by_locator.
        """
        if isinstance(target, str) and (target.isalnum() or target.startswith("#")):
            if self.select_by_id(target, option_text):
                return True
        return self.select_by_locator(target, option_text, timeout_ms=timeout_ms)

    def get_options(self, field_id: str) -> List[str]:
        """Returns all text options available in the Kendo DropDownList dataSource."""
        clean_id = field_id.lstrip("#")
        try:
            return self.page.evaluate(
                f"""
                (() => {{
                    const jq = window.jQuery || window.$;
                    if (!jq) return [];
                    const ddl = jq('#{clean_id}').data('kendoDropDownList');
                    if (!ddl) return [];
                    const textField = ddl.options.dataTextField || 'Text';
                    return ddl.dataSource.data().map(x => x[textField] || x.Definition || x.poc_name || x.Text || '');
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
                    const jq = window.jQuery || window.$;
                    if (!jq) return '';
                    const ddl = jq('#{clean_id}').data('kendoDropDownList');
                    return ddl ? ddl.text() : '';
                }})();
                """
            ) or ""
        except Exception:
            return ""


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
