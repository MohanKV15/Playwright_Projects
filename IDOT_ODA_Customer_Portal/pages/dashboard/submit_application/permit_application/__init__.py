"""
Permit Application Page Object Models.
Includes BasePermitApplicationPage, Primary Highway, Interstate Highway, Directional Sign, and Junkyard workflows.
"""

from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.base_permit_page import (
    BasePermitApplicationPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.primary_highway_page import (
    PrimaryHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.interstate_highway_page import (
    InterstateHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.directional_sign_page import (
    DirectionalSignPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.junkyard_page import (
    JunkyardPage,
)

__all__ = [
    "BasePermitApplicationPage",
    "PrimaryHighwayPage",
    "InterstateHighwayPage",
    "DirectionalSignPage",
    "JunkyardPage",
]
