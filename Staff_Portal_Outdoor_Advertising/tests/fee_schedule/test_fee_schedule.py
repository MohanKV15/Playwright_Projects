import pytest
from playwright.sync_api import Page, expect
from pages.fee_schedule.fee_schedule_page import FeeSchedulePage


class TestFeeSchedule:

    def test_fee_schedule_flow(self, authenticated_page: Page):
        """
        Verifies the complete Fee Schedule workflow:
        1. Navigates to Fee Schedule page and validates initial layout elements.
        2. Cycles search criteria through 'Permit', 'License', and 'Renewal' types and runs Search.
        3. Clears search types back to 'Select Type' and runs Search.
        4. Clicks 'Add Fee Schedule' to open details form and validates details layout containers.
        5. Cycles details selection through 'Permit', 'License', and 'Renewal' types.
        6. Clicks Save and then Cancel.
        """
        fee_page = FeeSchedulePage(authenticated_page)

        # 1. Navigate to Fee Schedule page and validate layout
        fee_page.navigate_to_fee_schedule()
        expect(fee_page.fee_schedule_heading).to_be_visible(timeout=10000)
        expect(fee_page.partial_form_first).to_be_visible(timeout=10000)
        expect(fee_page.results_grid_container).to_be_visible(timeout=10000)

        # 2. Select search type: Permit -> Search
        fee_page.select_search_type_by_text(current_text="Select Type", next_type="Permit")
        fee_page.click_search()
        fee_page.click_search()  # Double click search as recorded by user

        # 3. Select search type: License -> Search
        fee_page.select_search_type_by_text(current_text="Permit", next_type="License")
        fee_page.click_search()

        # 4. Select search type: Renewal -> Search
        fee_page.select_search_type_by_text(current_text="License", next_type="Renewal")
        fee_page.click_search()
        expect(fee_page.results_grid_container).to_be_visible(timeout=10000)

        # 5. Clear search types to Select Type -> Search
        fee_page.select_search_type_by_text(current_text="Renewal", next_type="Select Type")
        fee_page.click_search()

        # 6. Click Add Fee Schedule and validate details view elements
        fee_page.click_add_fee_schedule()
        expect(fee_page.fee_schedule_heading).to_be_visible(timeout=10000)
        expect(fee_page.partial_form_first).to_be_visible(timeout=10000)
        expect(fee_page.form_wrapper_nth4).to_be_visible(timeout=10000)
        expect(fee_page.form_wrapper_nth1).to_be_visible(timeout=10000)

        # 7. Cycles details selection: Permit -> License -> Renewal
        fee_page.select_details_type_by_text(current_text="Select Type", next_type="Permit")
        expect(fee_page.form_wrapper_nth1).to_be_visible(timeout=10000)

        fee_page.select_details_type_by_text(current_text="Permit", next_type="License")
        expect(fee_page.form_wrapper_nth1).to_be_visible(timeout=10000)

        fee_page.select_details_type_by_text(current_text="License", next_type="Renewal")
        expect(fee_page.form_wrapper_nth1).to_be_visible(timeout=10000)

        # 8. Save and Cancel
        fee_page.click_save()
        fee_page.click_cancel()
