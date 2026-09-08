import pytest
from IDOT_ODA_Staff_Portal.pages.GIS_navigation.GIS_page import GISPage


@pytest.mark.gis
@pytest.mark.smoke
def test_gis_navigation_and_map_display(authenticated_gis: GISPage):
    """
    Test Case ID: TC_STAFF_GIS_001
    Workflow:
    1. Authenticate into IDOT Outdoor Advertising Staff Portal.
    2. Navigate to GIS Information page by clicking 'GIS' in the sidebar navigation.
    3. Verify GIS instruction guidance text is visible:
       'Zoom in on the area where you want your permit to be located...'
    4. Verify browser support container / GIS iframe element is visible.
    5. Wait until the GIS map is fully displayed (iframe rendered, map container visible,
       tiles loaded, and Location Finder toolbar ready).
    6. Validate interactive map toolbar controls (Location Finder, Zoom-in, Zoom-out, Pan).
    """
    # 1. Navigate to GIS module
    authenticated_gis.navigate_to_gis()

    # 2. Verify instruction text is displayed
    authenticated_gis.verify_gis_instructions_displayed()

    # 3. Verify browser support fallback container for iframe
    authenticated_gis.verify_browser_support_container()

    # 4. Wait for map to display and verify tiles/controls are rendered
    authenticated_gis.wait_for_map_to_display()

    # 5. Verify map controls are active and visible
    authenticated_gis.verify_gis_map_controls()
