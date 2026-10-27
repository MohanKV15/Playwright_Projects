from typing import Dict, Any
from faker import Faker

fake = Faker()


def generate_company_registration_data() -> Dict[str, Any]:
    """Generates dynamic Company Registration test data using Faker."""
    email = f"test_{fake.hexify(text='^^^^^^')}@gmail.com"
    return {
        "company_name": f"Test {fake.company()[:20]} Corp",
        "address_1": fake.street_address(),
        "city": fake.city(),
        "zip_code": fake.zipcode()[:5],
        "phone": "999-999-9999",
        "email": email,
        "billing_address_1": fake.street_address(),
        "billing_city": fake.city(),
        "billing_zip_code": fake.zipcode()[:5],
        "poc_fname": fake.first_name(),
        "poc_lname": fake.last_name(),
        "poc_email": email,
        "com_phone": "999-999-9999",
    }
