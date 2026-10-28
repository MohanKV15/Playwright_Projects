"""
Test data management package.
Exposes the unified TestDataFactory and functional data generation aliases.
"""

from IDOT_ODA_Customer_Portal.testdata.test_data_factory import (
    TestDataFactory,
    generate_company_registration_data,
    generate_primary_highway_test_data,
    generate_junkyard_test_data,
)

__all__ = [
    "TestDataFactory",
    "generate_company_registration_data",
    "generate_primary_highway_test_data",
    "generate_junkyard_test_data",
]
