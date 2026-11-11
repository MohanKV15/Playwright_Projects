import random
from typing import Dict
from faker import Faker

fake = Faker("en_US")


class TestDataFactory:
    """
    Factory for generating dynamic test data using Faker to prevent collisions
    and eliminate hardcoded test values across parallel test runs.
    """

    @staticmethod
    def get_random_email() -> str:
        """Generates a random unique email address."""
        return fake.unique.email()

    @staticmethod
    def get_random_password(length: int = 12) -> str:
        """Generates a secure random password."""
        return fake.password(length=length, special_chars=True, digits=True, upper_case=True, lower_case=True)

    @staticmethod
    def get_random_invalid_credentials() -> Dict[str, str]:
        """Returns random unauthenticated credentials."""
        return {
            "email": fake.unique.email(),
            "password": fake.password(length=10, special_chars=True),
            "pin": str(random.randint(10, 99)),
        }

    @staticmethod
    def get_user_profile() -> Dict[str, str]:
        """Generates a full user identity dataset."""
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.numerify("###-###-####"),
            "company": fake.company(),
            "address": fake.street_address(),
            "city": fake.city(),
            "state": "NC",
            "zip_code": fake.zipcode(),
        }

    @staticmethod
    def get_new_project_data() -> Dict[str, str]:
        """
        Generates dynamic project creation data using Faker,
        strictly maintaining required format 'ABC12.1.ADE' for WBS.
        """
        return {
            "project_id": str(random.randint(10000000, 99999999)),
            "division": "01",
            "letting_type": "Constr. by State Forces (CSF)",
            "stip_non_stip": "NON-STIP",
            "acquisition_type": "AA-EARLY ACQUISTION",
            "wbs": "ABC12.1.ADE",
            "county": "Bertie",
            "parcel_no": str(random.randint(1000, 9999)),
            "property_tax_id": str(random.randint(1000, 9999)),
            "deed_book_page": f"test{random.randint(10, 99)}",
            "task_assignment": "Acquisition Agent",
            "internal_staff": "Dustin Johnson",
        }

