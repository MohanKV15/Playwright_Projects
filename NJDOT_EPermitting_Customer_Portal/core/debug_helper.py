import re
from datetime import datetime
from pathlib import Path


class DebugHelper:
    """Capture reusable debug artifacts for flaky UI diagnostics."""

    def __init__(self, page, artifacts_dir: Path, logger=None):
        self.page = page
        self.artifacts_dir = artifacts_dir
        self.logger = logger
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, label: str, script_name: str, location_div=None, diagnostics: dict | None = None) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_script = re.sub(r"[^a-zA-Z0-9_-]+", "_", script_name).strip("_") or "test_script"
        safe_label = re.sub(r"[^a-zA-Z0-9_-]+", "_", label).strip("_") or "debug"
        prefix = self.artifacts_dir / f"{timestamp}_{safe_script}_{safe_label}"

        try:
            self.page.screenshot(path=str(prefix.with_suffix(".png")), full_page=True)
        except Exception as ex:
            if self.logger:
                self.logger.warning("Failed to capture full-page screenshot for %s: %s", label, ex)

        try:
            prefix.with_suffix(".html").write_text(self.page.content(), encoding="utf-8")
        except Exception as ex:
            if self.logger:
                self.logger.warning("Failed to write page HTML for %s: %s", label, ex)

        if location_div is not None:
            try:
                location_div.screenshot(path=str(prefix.with_name(prefix.name + "_location.png")))
                prefix.with_name(prefix.name + "_location.html").write_text(
                    location_div.inner_html(), encoding="utf-8"
                )
            except Exception as ex:
                if self.logger:
                    self.logger.warning("Failed to capture location artifacts for %s: %s", label, ex)

        lines = [f"label={label}", f"url={self.page.url}"]
        if diagnostics:
            for key, value in diagnostics.items():
                lines.append(f"{key}={value}")
        try:
            prefix.with_name(prefix.name + "_diagnostics.txt").write_text("\n".join(lines), encoding="utf-8")
        except Exception as ex:
            if self.logger:
                self.logger.warning("Failed to write diagnostics for %s: %s", label, ex)
        return prefix

    def collect_visible_validation_messages(self) -> list[str]:
        visible_errors = self.page.locator(
            ".field-validation-error:visible, .validation-summary-errors li:visible, .k-invalid-msg:visible"
        )
        messages = []
        for i in range(visible_errors.count()):
            text = visible_errors.nth(i).inner_text().strip()
            if text:
                messages.append(text)
        return sorted(set(messages))

    def collect_invalid_required_fields(self) -> list[str]:
        labels = []
        invalid_controls = self.page.locator(
            "input[aria-invalid='true'], select[aria-invalid='true'], textarea[aria-invalid='true']"
        )
        for i in range(min(invalid_controls.count(), 30)):
            control = invalid_controls.nth(i)
            label = (
                control.get_attribute("aria-label")
                or control.get_attribute("name")
                or control.get_attribute("id")
                or ""
            ).strip()
            if label:
                labels.append(label)
        return sorted(set(labels))
