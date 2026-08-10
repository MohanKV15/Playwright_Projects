import datetime
import logging
import re
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)


class KendoControls:
    """
    Utility class providing reusable interactions for Kendo UI components
    such as Dropdowns, DatePickers, NumericTextBoxes, and Loading Overlays.
    Designed for professional enterprise test automation frameworks.
    """

    @staticmethod
    def wait_for_loader(page: Page, timeout: int = 15000) -> None:
        """
        Waits for active Kendo loading overlay masks or spinners to detach from the DOM.
        
        :param page: Active Playwright Page instance.
        :param timeout: Maximum wait time in milliseconds.
        """
        try:
            page.wait_for_selector(
                ".k-loading-mask, .k-loading-image, #loading, .spinner-border",
                state="detached",
                timeout=timeout,
            )
        except Exception as e:
            logger.debug(f"Kendo loading overlay wait completed or timed out: {e}")

    @staticmethod
    def fill_numeric(page: Page, element_id: str, value: float) -> None:
        """
        Sets value of a Kendo NumericTextBox using internal Kendo JS API.
        
        :param page: Active Playwright Page instance.
        :param element_id: DOM ID of the Kendo numeric input element.
        :param value: Numeric value to populate.
        """
        page.evaluate(f"""
            () => {{
                var numeric = $('#{element_id}').data('kendoNumericTextBox');
                if (numeric) {{
                    numeric.value({value});
                    numeric.trigger('change');
                }}
            }}
        """)
        logger.info(f"Set Kendo NumericTextBox '#{element_id}' to value: {value}")

    @staticmethod
    def select_all_dropdowns(page: Page) -> None:
        """
        Iterates through all visible Kendo dropdowns on the page and selects
        the first valid (non-placeholder) option using smart Kendo JS API and UI fallbacks.
        
        :param page: Active Playwright Page instance.
        """
        KendoControls.wait_for_loader(page)

        # 1. Fast, instant selection via Kendo JS API (< 50ms)
        page.evaluate("""
            () => {
                var jq = window.jQuery || window.$;
                if (!jq) return;
                jq('span.k-widget.k-dropdown, span.k-dropdown, select, input[data-role="dropdownlist"]').each(function() {
                    var $el = jq(this);
                    if (!$el.is(':visible') && !$el.closest('.k-dropdown, .k-widget').is(':visible')) return;
                    var ddl = $el.find('input, select').data('kendoDropDownList') || $el.data('kendoDropDownList');
                    if (!ddl && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                        try { ddl = window.kendo.widgetInstance($el); } catch (e) {}
                    }
                    if (ddl) {
                        if (typeof ddl.enable === 'function') ddl.enable(true);
                        var curVal = typeof ddl.value === 'function' ? ddl.value() : '';
                        var curText = (typeof ddl.text === 'function' ? ddl.text() : '').trim();
                        if (!curVal || curVal === '' || curText.startsWith('--') || curText.toLowerCase().startsWith('select')) {
                            if (ddl.dataSource && typeof ddl.dataSource.data === 'function') {
                                var items = ddl.dataSource.data();
                                if (items && items.length > 0) {
                                    var targetVal = null;
                                    var targetTxt = '';
                                    for (var i = 0; i < items.length; i++) {
                                        var item = items[i];
                                        if (!item) continue;
                                        var txt = (item.text || item.Text || item.name || item.Name || item.value || item.Value || Object.values(item)[0] || '').toString().trim();
                                        var val = (item.value !== undefined && item.value !== null && item.value !== '') ? item.value : ((item.Value !== undefined && item.Value !== null && item.Value !== '') ? item.Value : txt);
                                        if (txt && val !== undefined && val !== null && val !== '' && !txt.startsWith('--') && !txt.toLowerCase().startsWith('select') && !txt.toLowerCase().includes('no data')) {
                                            targetVal = val;
                                            targetTxt = txt;
                                            break;
                                        }
                                    }
                                    if (targetVal !== null) {
                                        if (typeof ddl.value === 'function') ddl.value(targetVal);
                                        if (typeof ddl.trigger === 'function') ddl.trigger('change');
                                        if (ddl.wrapper && ddl.wrapper.length) {
                                            ddl.wrapper.find('.k-input').text(targetTxt);
                                        }
                                    }
                                }
                            }
                        }
                    }
                });

                var staffVal = jq('#inspected_by_staff').val() || jq('#inspected_by_consultant').val();
                if (staffVal && jq('#inspected_by').length) {
                    jq('#inspected_by').val(staffVal).trigger('change');
                }
            }
        """)

        # 2. Fast UI Click Fallback only for dropdowns still showing placeholder text
        dropdowns = page.locator("span.k-dropdown:visible, span.k-widget.k-dropdown:visible")
        count = dropdowns.count()
        for i in range(count):
            try:
                dd = dropdowns.nth(i)
                if not dd.is_visible():
                    continue
                selected_text = dd.inner_text().strip()
                if selected_text.startswith("--") or selected_text.lower().startswith("select"):
                    KendoControls.select_first_dropdown_option(page, dd)
            except Exception as e:
                logger.warning(f"Dropdown index {i} iteration note: {e}")

    @staticmethod
    def select_first_dropdown_option(page: Page, trigger_locator: Locator = None) -> None:
        """
        Selects the first valid option in a Kendo dropdown menu.
        Applies Kendo JS API selection first for speed and falls back to UI clicks.
        
        :param page: Active Playwright Page instance.
        :param trigger_locator: Optional Locator of the dropdown element/button.
        """
        KendoControls.wait_for_loader(page)
        selected = False

        if trigger_locator is not None and trigger_locator.is_visible():
            # Try JS API first
            try:
                handle = trigger_locator.element_handle()
                if handle:
                    selected = page.evaluate("""
                        (el) => {
                            var jq = window.jQuery || window.$;
                            if (!jq) return false;
                            var $el = jq(el);
                            var ddl = $el.find('input, select').data('kendoDropDownList') || $el.data('kendoDropDownList');
                            if (!ddl && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                                try { ddl = window.kendo.widgetInstance($el); } catch (e) {}
                            }
                            if (ddl && ddl.dataSource && typeof ddl.dataSource.data === 'function') {
                                if (typeof ddl.enable === 'function') ddl.enable(true);
                                var items = ddl.dataSource.data();
                                for (var i = 0; i < items.length; i++) {
                                    var item = items[i];
                                    if (!item) continue;
                                    var txt = (item.text || item.Text || item.name || item.Name || item.value || item.Value || Object.values(item)[0] || '').toString().trim();
                                    var val = (item.value !== undefined && item.value !== null && item.value !== '') ? item.value : ((item.Value !== undefined && item.Value !== null && item.Value !== '') ? item.Value : txt);
                                    if (txt && val !== undefined && val !== null && val !== '' && !txt.startsWith('--') && !txt.toLowerCase().startsWith('select') && !txt.toLowerCase().includes('no data')) {
                                        if (typeof ddl.value === 'function') ddl.value(val);
                                        if (typeof ddl.trigger === 'function') ddl.trigger('change');
                                        if (ddl.wrapper && ddl.wrapper.length) {
                                            ddl.wrapper.find('.k-input').text(txt);
                                        }
                                        return true;
                                    }
                                }
                            }
                            return false;
                        }
                    """, handle)
            except Exception as e:
                logger.debug(f"JS API dropdown selection note: {e}")

        if not selected and trigger_locator is not None and trigger_locator.is_visible():
            try:
                is_disabled = trigger_locator.evaluate(
                    "el => el.getAttribute('aria-disabled') === 'true' || el.classList.contains('k-state-disabled') || el.disabled === true"
                )
                if not is_disabled:
                    trigger_locator.click(timeout=1500)
                    page.wait_for_timeout(150)
                    options = page.locator(
                        ".k-animation-container:visible li, .k-list-container:visible li, ul.k-list:visible li, [role='option']:visible"
                    )
                    count = options.count()
                    if count > 0:
                        for i in range(count):
                            opt = options.nth(i)
                            txt = opt.inner_text().strip()
                            if txt and not txt.startswith("--") and not txt.lower().startswith("select") and "no data" not in txt.lower():
                                logger.info(f"Selected 1st valid dropdown option: '{txt}'")
                                opt.click()
                                page.wait_for_timeout(150)
                                selected = True
                                break
            except Exception as e:
                logger.warning(f"Dropdown click interaction note: {e}")

        if not selected:
            # Smart Kendo API Fallback: enables & selects first non-placeholder option in dataSource
            page.evaluate("""
                () => {
                    var jq = window.jQuery || window.$;
                    if (!jq) return;
                    jq('span.k-widget.k-dropdown, span.k-dropdown, select, input[data-role="dropdownlist"]').each(function() {
                        var $el = jq(this);
                        if (!$el.is(':visible') && !$el.closest('.k-dropdown, .k-widget').is(':visible')) return;
                        var ddl = $el.find('input, select').data('kendoDropDownList') || $el.data('kendoDropDownList');
                        if (!ddl && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                            try { ddl = window.kendo.widgetInstance($el); } catch (e) {}
                        }
                        if (ddl) {
                            if (typeof ddl.enable === 'function') ddl.enable(true);
                            if (ddl.dataSource && typeof ddl.dataSource.data === 'function') {
                                var items = ddl.dataSource.data();
                                if (items && items.length > 0) {
                                    var targetVal = null;
                                    var targetTxt = '';
                                    for (var i = 0; i < items.length; i++) {
                                        var item = items[i];
                                        if (!item) continue;
                                        var txt = (item.text || item.Text || item.name || item.Name || item.value || item.Value || Object.values(item)[0] || '').toString().trim();
                                        var val = (item.value !== undefined && item.value !== null && item.value !== '') ? item.value : ((item.Value !== undefined && item.Value !== null && item.Value !== '') ? item.Value : txt);
                                        if (txt && val !== undefined && val !== null && val !== '' && !txt.startsWith('--') && !txt.toLowerCase().startsWith('select') && !txt.toLowerCase().includes('no data')) {
                                            targetVal = val;
                                            targetTxt = txt;
                                            break;
                                        }
                                    }
                                    if (targetVal !== null) {
                                        if (typeof ddl.value === 'function') ddl.value(targetVal);
                                        if (typeof ddl.trigger === 'function') ddl.trigger('change');
                                        if (ddl.wrapper && ddl.wrapper.length) {
                                            ddl.wrapper.find('.k-input').text(targetTxt);
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            """)
            page.wait_for_timeout(300)

    @staticmethod
    def select_location_dropdowns(page: Page) -> None:
        """
        Sequentially selects the 1st valid option for Route, Suffix, and Direction
        in location containers or direct dropdown fields (#RouteSldNameDD, #route_suffix, #direction),
        waiting for Kendo AJAX DataSource binding.
        
        :param page: Active Playwright Page instance.
        """
        KendoControls.wait_for_loader(page, timeout=5000)
        selectors = ['#RouteSldNameDD', '#route_suffix', '#direction', '#ApplicationLocationInfoDiv .k-dropdown, #ApplicationLocationInfoDiv input[data-role="dropdownlist"], #ApplicationLocationInfoDiv select']
        for sel in selectors:
            try:
                page.evaluate(
                    """
                    (selector) => {
                        var jq = window.jQuery || window.$;
                        if (!jq) return;
                        var targets = jq(selector);
                        targets.each(function() {
                            var target = jq(this);
                            var dd = target.data("kendoDropDownList") || target.find("input, select").data("kendoDropDownList") || target.closest(".k-dropdown, .k-widget").find("input, select").data("kendoDropDownList");
                            if (!dd && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                                try { dd = window.kendo.widgetInstance(target); } catch(e) {}
                            }
                            if (dd && dd.dataSource && typeof dd.dataSource.data === "function") {
                                if (typeof dd.enable === 'function') dd.enable(true);
                                var items = dd.dataSource.data();
                                if (items && items.length > 0) {
                                    var targetVal = null;
                                    var targetTxt = "";
                                    for (var i = 0; i < items.length; i++) {
                                        var item = items[i];
                                        if (!item) continue;
                                        var txt = (item.text || item.Text || item.name || item.Name || item.value || item.Value || Object.values(item)[0] || "").toString().trim();
                                        var val = (item.value !== undefined && item.value !== null && item.value !== '') ? item.value : ((item.Value !== undefined && item.Value !== null && item.Value !== '') ? item.Value : txt);
                                        if (txt && val !== undefined && val !== null && val !== '' && !txt.startsWith("--") && !txt.toLowerCase().includes("select") && !txt.toLowerCase().includes("no data") && txt !== "0") {
                                            targetVal = val;
                                            targetTxt = txt;
                                            break;
                                        }
                                    }
                                    if (targetVal !== null) {
                                        if (typeof dd.value === "function") dd.value(targetVal);
                                        if (typeof dd.trigger === "function") dd.trigger("change");
                                        if (dd.wrapper && dd.wrapper.length) {
                                            dd.wrapper.find('.k-input').text(targetTxt);
                                        }
                                    }
                                }
                            }
                        });
                    }
                    """,
                    sel,
                )
                page.wait_for_timeout(300)
            except Exception as e:
                logger.warning(f"Location dropdown selector '{sel}' note: {e}")

    @staticmethod
    def set_today_date(page: Page, trigger_locator: Locator = None) -> str:
        """
        Universal Kendo date picker helper:
        Calculates today's date dynamically, opens calendar picker if available,
        or injects formatted date string (MM/DD/YYYY).
        
        :param page: Active Playwright Page instance.
        :param trigger_locator: Optional Locator of datepicker calendar trigger icon.
        :return: Formatted date string (MM/DD/YYYY).
        """
        today = datetime.date.today()
        day_str = str(today.day)
        date_full = today.strftime("%m/%d/%Y")

        if trigger_locator is not None and trigger_locator.is_visible():
            try:
                trigger_locator.evaluate("el => el.click()")
                page.wait_for_timeout(300)

                day_link = page.get_by_label(re.compile(r"Current focused date", re.I)).get_by_role("link", name=day_str).or_(
                    page.locator(".k-calendar-container:visible, .k-animation-container:visible").get_by_role("link", name=day_str, exact=True)
                ).first
                if day_link.is_visible():
                    day_link.evaluate("el => el.click()")
                    return date_full
            except Exception as e:
                logger.warning(f"Calendar popup interaction note: {e}")

        # Direct input injection fallback
        try:
            KendoControls.set_all_datefields_to_current(page)
        except Exception as e:
            logger.warning(f"Direct date injection note: {e}")

        return date_full

    @staticmethod
    def set_all_datefields_to_current(page: Page) -> None:
        """
        Injects current date directly into all Kendo DatePicker controls across the page.
        
        :param page: Active Playwright Page instance.
        """
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        page.evaluate(f"""
            (dateStr) => {{
                var jq = window.jQuery || window.$;
                if (!jq) return;
                jq('input[data-role="datepicker"], input[id*="Date"], input[name*="Date"], input[id*="date"], input[name*="date"], .k-datepicker input, [data-val-required*="Date"]').each(function() {{
                    var id = (jq(this).attr('id') || '').toLowerCase();
                    var name = (jq(this).attr('name') || '').toLowerCase();
                    var role = (jq(this).attr('data-role') || '').toLowerCase();
                    if (id.includes('time') || name.includes('time') || role.includes('maskedtextbox') || id.includes('selectdropdown') || name.includes('selectdropdown')) {{
                        return;
                    }}
                    var dp = jq(this).data("kendoDatePicker") || jq(this).closest(".k-datepicker").find("input").data("kendoDatePicker");
                    if (!dp && window.kendo && typeof window.kendo.widgetInstance === 'function') {{
                        try {{ dp = window.kendo.widgetInstance(jq(this)); }} catch(e) {{}}
                    }}
                    if (dp && typeof dp.value === "function") {{
                        dp.value(dateStr);
                        if (typeof dp.trigger === "function") dp.trigger("change");
                    }}
                    jq(this).val(dateStr).attr("value", dateStr).trigger("input").trigger("change").trigger("blur");
                }});
            }}
        """, current_date_str)

    @staticmethod
    def assert_no_validation_errors(page: Page, timeout: int = 5000) -> None:
        """
        Checks if any mandatory field validation error messages are visible on the page.
        If validation errors are present, raises AssertionError to fail the test immediately.
        
        :param page: Active Playwright Page instance.
        :param timeout: Loading wait timeout in milliseconds.
        """
        KendoControls.wait_for_loader(page, timeout=timeout)
        error_locators = page.locator(
            ".field-validation-error:visible, "
            "span.text-danger:visible, "
            ".k-tooltip-validation:visible, "
            "[data-valmsg-summary='true']:visible li, "
            ".validation-summary-errors:visible li"
        )
        count = error_locators.count()
        visible_errors = []
        for i in range(count):
            err = error_locators.nth(i)
            txt = err.inner_text().strip()
            if txt and not txt.startswith("--") and "success" not in txt.lower():
                visible_errors.append(txt)

        if visible_errors:
            err_msg = "; ".join(visible_errors)
            logger.error(f"Form validation error(s) present: {err_msg}")
            raise AssertionError(f"Mandatory form validation error(s) present on page: {err_msg}")

