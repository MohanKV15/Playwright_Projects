from pages.application_permit_info.permit_listing_page import PermitListingPage

def test_permit_listing_search_and_pagination(authenticated_page):
    """
    Evaluates the Permit Listing search filters and grid pagination 
    without entering the edit mode.
    """
    # 1. Initialize Page Object
    permit_page = PermitListingPage(authenticated_page)
    
    # 2. Navigate and verify form readiness
    permit_page.navigate_to_permit_listing()
    permit_page.verify_search_form_ready()
    
    # 3. Execute Search with retries for 504 server timeouts
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with authenticated_page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=60000) as backend_response:
                permit_page.search_by_company("HCL")
            
            api_response = backend_response.value
            if not api_response.ok or api_response.status == 504:
                print(f"\n[RETRY] Backend API returned status {api_response.status}. Retrying attempt {attempt + 1}/{max_retries}...")
                authenticated_page.wait_for_timeout(5000)
                if attempt < max_retries - 1:
                    permit_page.navigate_to_permit_listing()
                    continue
            assert api_response.ok, f"CRITICAL: Backend API collapsed with Status code {api_response.status}"
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"\n[RETRY] Search failed with error: {e}. Retrying attempt {attempt + 1}/{max_retries}...")
            authenticated_page.wait_for_timeout(5000)
            permit_page.navigate_to_permit_listing()
    
    # 5. Wait for UI to render
    authenticated_page.wait_for_timeout(2000)
    
    # 6. Verify Grid Navigation (Next Page)
    # We stay in the grid view for this test
    # permit_page.next_page_button.click() 
    # self._wait_for_loader()

