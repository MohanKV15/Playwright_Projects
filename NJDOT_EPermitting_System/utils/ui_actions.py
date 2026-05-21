import time
from pathlib import Path



class UIActions:
    """Reusable low-level UI actions with flaky-UI safeguards."""

    def __init__(self, page, logger=None):
        self.page = page
        self.logger = logger

    def wait_for_loader(self, timeout_ms: int = 5000) -> None:
        self._wait_until_hidden(".k-loading-mask:visible, #loader.k-loading-image", timeout_ms)

    def wait_for_overlay(self, timeout_ms: int = 5000) -> None:
        self._wait_until_hidden(".k-overlay:visible", timeout_ms)

    def wait_for_visible(self, locator, timeout_ms: int = 15000):
        locator.wait_for(state="visible", timeout=timeout_ms)
        return locator

    def safe_fill(self, locator, value: str, timeout_ms: int = 15000, retry: int = 2) -> None:
        self.wait_for_visible(locator, timeout_ms)
        last_error = None
        for _ in range(max(1, retry)):
            try:
                self.wait_for_loader(min(timeout_ms, 5000))
                self.wait_for_overlay(min(timeout_ms, 5000))
                locator.fill(value, timeout=timeout_ms)
                return
            except Exception as ex:
                last_error = ex
                self.page.wait_for_timeout(200)
        raise last_error

    def click(self, locator, timeout_ms: int = 15000, retry: int = 2) -> None:
        self.wait_for_visible(locator, timeout_ms)
        last_error = None
        for _ in range(max(1, retry)):
            try:
                self.wait_for_loader(min(timeout_ms, 5000))
                self.wait_for_overlay(min(timeout_ms, 5000))
                locator.click(timeout=timeout_ms)
                return
            except Exception as ex:
                last_error = ex
                self.page.wait_for_timeout(250)
        raise last_error

    def scroll_and_click(self, locator, timeout_ms: int = 15000, retry: int = 2) -> None:
        self.wait_for_visible(locator, timeout_ms)
        last_error = None
        for _ in range(max(1, retry)):
            try:
                self.wait_for_loader(min(timeout_ms, 5000))
                self.wait_for_overlay(min(timeout_ms, 5000))
                locator.scroll_into_view_if_needed()
                locator.click(timeout=timeout_ms)
                return
            except Exception as ex:
                last_error = ex
                self.page.wait_for_timeout(250)

        locator.scroll_into_view_if_needed()
        locator.click(timeout=timeout_ms, force=True)

    def _wait_until_hidden(self, selector: str, timeout_ms: int) -> None:
        end = time.time() + (timeout_ms / 1000)
        while time.time() < end:
            if self.page.locator(selector).count() == 0:
                return
            self.page.wait_for_timeout(150)

# def download_file(page, button, folder="downloads"):
#     """
#     Always keep ONLY the latest downloaded file (overwrite mode)
#     """

#     download_dir = Path(folder)
#     download_dir.mkdir(exist_ok=True)

#     file_path = download_dir / "permit_export.xlsx"

#     # Remove old file
#     if file_path.exists():
#         file_path.unlink()

#     # Download
#     with page.expect_download() as download_info:
#         button.click()

#     download = download_info.value
#     download.save_as(file_path)

#     return file_path


# def download_file(page, button, folder="downloads"):
#     """
#     Always keep ONLY ONE latest downloaded file (any type)
#     """

#     download_dir = Path(folder).resolve()
#     download_dir.mkdir(exist_ok=True)

#     # 🔥 Remove ALL old files (important)
#     for old_file in download_dir.glob("*"):
#         try:
#             old_file.unlink()
#         except:
#             pass

#     # Start download
#     with page.expect_download() as download_info:
#         button.click()

#     download = download_info.value

#     # Save using actual filename
#     file_path = download_dir / download.suggested_filename
#     download.save_as(file_path)

#     return file_path


from pathlib import Path


def download_file(page, button, module, folder="downloads"):
    """
    Download file per module (payment / permit)
    Keeps only latest file inside that module folder
    """

    # 📂 Create module-specific folder
    download_dir = Path(folder).resolve() / module
    download_dir.mkdir(parents=True, exist_ok=True)

    # 🔥 Remove old files ONLY in that module
    for old_file in download_dir.glob("*"):
        try:
            old_file.unlink()
        except:
            pass

    # Start download
    with page.expect_download() as download_info:
        button.click()

    download = download_info.value

    # Save with actual name
    file_path = download_dir / download.suggested_filename
    download.save_as(file_path)

    return file_path