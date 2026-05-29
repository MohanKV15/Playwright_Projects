import pytest
from pages.applications_history.applications_history_page import ApplicationsHistoryPage

def test_applications_history_search_and_export(authenticated_page):
    """
    Validates navigating to Applications History, searching, paginating, 
    exporting records, and returning safely.
    """
    # 1. Initialize POM
    history_page = ApplicationsHistoryPage(authenticated_page)
    
    # 2. Open the Applications History module
    history_page.open()
    
    # 3. Perform a dynamic search to ensure future-proofing
    search_term = history_page.get_first_record_text()
    history_page.perform_search(search_term)
    
    # 4. Clear the search to show all results
    history_page.clear_search()
    
    # 5. Paginate through all the records
    history_page.validate_pagination()
    
    # 6. Test the Export functionality (downloads file)
    history_page.export_history()
    
    # 7. Click back to return to the dashboard
    history_page.go_back()
    
    print("[INFO] Applications History functionality tested successfully!")
