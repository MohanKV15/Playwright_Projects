import pytest
from pages.payment_activity.payment_activity_page import PaymentActivityPage


@pytest.mark.authenticated
def test_payment_activity_flow(authenticated_page):
    """
    Payment Activity Flow:
    - Open page
    - Navigate to last page (efficient)
    - Export file
    - Validate download
    - Navigate back
    """

    payment_page = PaymentActivityPage(authenticated_page)

    # Step 1: Open payment activity
    payment_page.open_payment_activity()

    # Step 2: Go to last page (optimized)
    payment_page.go_to_last_page()

    # Step 3: Export data
    file_path = payment_page.export_payment_data()

    # Step 4: Validate download
    assert file_path.exists(), "❌ File not downloaded"
    assert file_path.stat().st_size > 0, "❌ File is empty"

    # Step 5: Back navigation
    payment_page.go_back()