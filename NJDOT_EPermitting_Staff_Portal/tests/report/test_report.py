import pytest
from pages.report.report_page import ReportPage


def test_reports_workflow(authenticated_page):
    """
    Verifies the complete Reports module workflow per user codegen sequence:
    1. Navigate to Reports page and verify initial layout headers.
    2. Select 'Bond/Payment Report' and verify Power BI iframe content loaded.
    3. Select 'Permit Report' and verify visual style loaded.
    4. Select 'Reviewer Report' and verify 'Permit No' column header in iframe.
    5. Select 'LONI Report' and verify Power BI report region.
    6. Select 'Pre-Application Report' and verify Power BI report region.
    7. Select 'EPERMIT_FINAL_CLEVEL' report option.
    8. Select 'EPERMIT_PM' report option.
    9. Fill spinbutton with '11' and select 'NJ EP Migration Dashboard'.
    10. Fill spinbutton with '11' and select 'PRE/LONI (DC TEST)'.
    11. Verify 'App. Recvd. Date' column header in iframe.
    12. Interact with 'New Report' and 'Back' action buttons.
    """
    report_page = ReportPage(authenticated_page)

    # 1. Navigation & Layout Verification
    report_page.navigate_to_reports()
    report_page.verify_initial_layout()

    # 2. Bond/Payment Report
    report_page.select_report_option("Bond/Payment Report")
    report_page.verify_powerbi_report_loaded()

    # 3. Permit Report
    report_page.select_report_option("Permit Report")
    report_page.verify_powerbi_report_loaded()

    # 4. Reviewer Report
    report_page.select_report_option("Reviewer Report")
    report_page.verify_column_header_in_iframe("Permit No Can be sorted")

    # 5. LONI Report
    report_page.select_report_option("LONI Report")
    report_page.verify_powerbi_report_loaded()

    # 6. Pre-Application Report
    report_page.select_report_option("Pre-Application Report")
    report_page.verify_powerbi_report_loaded()

    # 7. EPERMIT_FINAL_CLEVEL Report
    report_page.select_report_option("EPERMIT_FINAL_CLEVEL")

    # 8. EPERMIT_PM Report
    report_page.navigate("https://u-njhtsp.bemcorp.net/Home/Report")
    report_page.select_report_option("EPERMIT_PM")

    # 9. NJ EP Migration Dashboard
    report_page.navigate("https://u-njhtsp.bemcorp.net/Home/Report")
    report_page.fill_spinbutton_and_select_report("11", "NJ EP Migration Dashboard")

    # 10. PRE/LONI (DC TEST) Report
    report_page.navigate("https://u-njhtsp.bemcorp.net/Home/Report")
    report_page.fill_spinbutton_and_select_report("11", "PRE/LONI (DC TEST)")
    report_page.verify_column_header_in_iframe("App. Recvd. Date Can be sorted")

    # 11. New Report & Back Buttons
    report_page.click_new_report()
    report_page.click_back()
