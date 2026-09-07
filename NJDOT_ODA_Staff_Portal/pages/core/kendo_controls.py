import logging
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
            loc.wait_for(state="visible", timeout=timeout_ms)
            loc.click(force=True)
            self.page.wait_for_timeout(300)

            # Find option in visible popup listbox
            option = self.page.locator(
                "li[role='option']:visible, .k-animation-container:visible li, .k-list-container:visible li, [role='listbox']:visible li"
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
                    const dp = $('#{clean_id}').data('kendoDatePicker');
                    if (dp) {{
                        dp.value('{date_str}');
                        dp.trigger('change');
                        return true;
                    }}
                    $('#{clean_id}').val('{date_str}').trigger('change');
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
