from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, Pattern

import pytest
from playwright.sync_api import Page, Request, Response


DEFAULT_RESOURCE_TYPES = {"xhr", "fetch"}
DEFAULT_SUCCESS_STATUSES = tuple(range(200, 400))
DEFAULT_IGNORED_FAILURE_PATTERNS = ("net::ERR_ABORTED",)
MAX_RESPONSE_BODY_LENGTH = 2000
REPORTS_DIR = Path(__file__).resolve().parent / "reports"


@dataclass
class ApiCallRecord:
    url: str
    method: str
    resource_type: str
    request_payload: str | None = None
    response_status: int | None = None
    response_body: str | None = None
    request_headers: dict[str, str] | None = None
    response_headers: dict[str, str] | None = None
    failure_text: str | None = None


class ApiCaptureHelper:
    """Capture and validate API traffic triggered by Playwright UI actions."""

    def __init__(
        self,
        page: Page,
        expected_statuses: Iterable[int] | None = None,
        include_resource_types: Iterable[str] | None = None,
        url_patterns: Iterable[str | Pattern[str]] | None = None,
        ignored_failure_patterns: Iterable[str] | None = None,
        print_console: bool = True,
    ):
        self.page = page
        self.context = page.context
        self.expected_statuses = tuple(expected_statuses or DEFAULT_SUCCESS_STATUSES)
        self.include_resource_types = {
            resource_type.lower() for resource_type in (include_resource_types or DEFAULT_RESOURCE_TYPES)
        }
        self.url_patterns = tuple(url_patterns or ())
        self.ignored_failure_patterns = tuple(ignored_failure_patterns or DEFAULT_IGNORED_FAILURE_PATTERNS)
        self.print_console = print_console
        self.records: list[ApiCallRecord] = []
        self._records_by_request_id: dict[int, ApiCallRecord] = {}
        self._started = False
        self._last_activity = 0.0
        self._report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def start(self) -> "ApiCaptureHelper":
        if self._started:
            return self
        self.context.on("request", self._on_request)
        self.context.on("response", self._on_response)
        self.context.on("requestfailed", self._on_request_failed)
        self._last_activity = time.time()
        self._started = True
        self._emit_console("API capture enabled.")
        return self

    def stop(self) -> None:
        if not self._started:
            return
        self.context.remove_listener("request", self._on_request)
        self.context.remove_listener("response", self._on_response)
        self.context.remove_listener("requestfailed", self._on_request_failed)
        self._started = False
        self._emit_console("API capture disabled.")

    def wait_for_api_idle(self, idle_ms: int = 1000, timeout_ms: int = 15000) -> None:
        end_time = time.time() + (timeout_ms / 1000)
        idle_window = idle_ms / 1000
        while time.time() < end_time:
            if time.time() - self._last_activity >= idle_window:
                return
            self.page.wait_for_timeout(200)

    def assert_all_responses_successful(
        self,
        expected_statuses_by_url: dict[str, Iterable[int]] | None = None,
    ) -> None:
        failures: list[str] = []
        per_url_expectations = expected_statuses_by_url or {}

        for record in self.records:
            if record.failure_text:
                if self._should_ignore_failure(record.failure_text):
                    continue
                failures.append(
                    f"{record.method} {record.url} failed before response was received: {record.failure_text}"
                )
                continue

            if record.response_status is None:
                failures.append(f"{record.method} {record.url} did not produce a response.")
                continue

            expected_statuses = self._get_expected_statuses(record.url, per_url_expectations)
            if record.response_status not in expected_statuses:
                failures.append(
                    f"{record.method} {record.url} returned {record.response_status}; "
                    f"expected one of {sorted(expected_statuses)}"
                )

        if failures:
            raise AssertionError("API validation failed:\n" + "\n".join(failures))

    def summary(self) -> list[dict[str, object]]:
        return [
            {
                "url": record.url,
                "method": record.method,
                "resource_type": record.resource_type,
                "request_payload": record.request_payload,
                "response_status": record.response_status,
                "response_body": record.response_body,
                "failure_text": record.failure_text,
            }
            for record in self.records
        ]

    def write_json_report(self, test_name: str) -> Path:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        safe_test_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", test_name).strip("_") or "test"
        report_path = REPORTS_DIR / f"{safe_test_name}_{self._report_timestamp}.json"
        report_data = {
            "test_name": test_name,
            "timestamp": self._report_timestamp,
            "api_calls": [
                {
                    "api_name": self._derive_api_name(record.url),
                    "request": {
                        "url": record.url,
                        "method": record.method,
                        "resource_type": record.resource_type,
                        "headers": record.request_headers,
                        "payload": record.request_payload,
                    },
                    "response": {
                        "status_code": record.response_status,
                        "headers": record.response_headers,
                        "body": record.response_body,
                    },
                    "failure": {
                        "details": record.failure_text,
                    },
                }
                for record in self.records
            ],
        }
        report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=True), encoding="utf-8")
        return report_path

    def _get_expected_statuses(
        self,
        url: str,
        expected_statuses_by_url: dict[str, Iterable[int]],
    ) -> tuple[int, ...]:
        for pattern, expected in expected_statuses_by_url.items():
            if fnmatch(url, pattern):
                return tuple(expected)
        return self.expected_statuses

    def _should_capture(self, request: Request) -> bool:
        if request.resource_type.lower() not in self.include_resource_types:
            return False

        if not self.url_patterns:
            return True

        for pattern in self.url_patterns:
            if isinstance(pattern, str) and fnmatch(request.url, pattern):
                return True
            if hasattr(pattern, "search") and pattern.search(request.url):
                return True
        return False

    def _should_ignore_failure(self, failure_text: str) -> bool:
        return any(pattern in failure_text for pattern in self.ignored_failure_patterns)

    def _on_request(self, request: Request) -> None:
        if not self._should_capture(request):
            return

        request_payload = self._format_payload(request.post_data)
        record = ApiCallRecord(
            url=request.url,
            method=request.method,
            resource_type=request.resource_type,
            request_payload=request_payload,
            request_headers=dict(request.headers),
        )
        self.records.append(record)
        self._records_by_request_id[id(request)] = record
        self._last_activity = time.time()

    def _on_response(self, response: Response) -> None:
        request = response.request
        if not self._should_capture(request):
            return

        record = self._records_by_request_id.get(id(request))
        if record is None:
            record = ApiCallRecord(
                url=request.url,
                method=request.method,
                resource_type=request.resource_type,
            )
            self.records.append(record)
            self._records_by_request_id[id(request)] = record

        record.response_status = response.status
        record.response_headers = dict(response.headers)
        record.response_body = self._safe_response_body(response)
        self._last_activity = time.time()
        self._log_record(record)

    def _on_request_failed(self, request: Request) -> None:
        if not self._should_capture(request):
            return

        record = self._records_by_request_id.get(id(request))
        if record is None:
            record = ApiCallRecord(
                url=request.url,
                method=request.method,
                resource_type=request.resource_type,
                request_payload=self._format_payload(request.post_data),
                request_headers=dict(request.headers),
            )
            self.records.append(record)
            self._records_by_request_id[id(request)] = record

        record.failure_text = request.failure or "request failed"
        self._last_activity = time.time()
        self._log_record(record)

    def _safe_response_body(self, response: Response) -> str:
        content_type = response.headers.get("content-type", "")
        try:
            if "application/json" in content_type:
                body = json.dumps(response.json(), indent=2, ensure_ascii=True)
            else:
                body = response.text()
            return self._trim_text(body)
        except Exception as exc:
            return f"<unable to read response body: {exc}>"

    def _format_payload(self, payload: str | None) -> str | None:
        if not payload:
            return None

        try:
            return json.dumps(json.loads(payload), indent=2, ensure_ascii=True)
        except Exception:
            return payload

    def _log_record(self, record: ApiCallRecord) -> None:
        if not self.print_console:
            return

        request_payload = record.request_payload if record.request_payload else "<no payload>"
        response_status = record.response_status if record.response_status is not None else "<no status>"
        response_body = record.response_body if record.response_body else "<no response body>"
        failure_text = record.failure_text if record.failure_text else "<none>"

        message = (
            "\n" + "=" * 80 +
            "\n[API CAPTURE]"
            f"\nURL            : {record.url}"
            f"\nMethod         : {record.method}"
            f"\nRequest Payload: {request_payload}"
            f"\nResponse Status: {response_status}"
            f"\nResponse Body  : {response_body}"
            f"\nFailure Details: {failure_text}"
            "\n" + "=" * 80
        )
        self._emit_console(message)

    def _emit_console(self, message: str) -> None:
        if not self.print_console:
            return
        print(message, flush=True)

    def _trim_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) <= MAX_RESPONSE_BODY_LENGTH:
            return value
        return value[:MAX_RESPONSE_BODY_LENGTH] + "... <trimmed>"

    def _derive_api_name(self, url: str) -> str:
        clean_url = url.split("?", 1)[0].rstrip("/")
        match = re.search(r"/([^/]+)$", clean_url)
        if not match:
            return "unknown_api"
        return match.group(1)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Optional pytest plugin hook for auto-capturing API traffic in tests using the page fixture.

    Enable it without changing project code by running pytest with:
    pytest -p NJDOT_EPermitting_System.api_validation.api_helper
    """

    helper = None
    page = item.funcargs.get("page")
    if page is not None:
        helper = ApiCaptureHelper(page=page)
        helper.start()

    outcome = yield

    if helper is None:
        return

    report_path = None
    try:
        helper.wait_for_api_idle()
    finally:
        helper.stop()

    report_path = helper.write_json_report(item.name)
    helper._emit_console(f"API JSON report: {report_path}")

    helper.assert_all_responses_successful()
    item.api_capture_records = helper.summary()

    outcome.get_result()