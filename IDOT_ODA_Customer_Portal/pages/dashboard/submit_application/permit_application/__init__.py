"""
Permit Application Page Object Models.
Includes Primary Highway, Interstate Highway, and related permit workflows.
"""

from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.primary_highway_page import (
    PrimaryHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.interstate_highway_page import (
    InterstateHighwayPage,
)

__all__ = ["PrimaryHighwayPage", "InterstateHighwayPage"]
