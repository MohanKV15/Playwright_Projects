from datetime import datetime
from typing import Dict, Any, Tuple
from faker import Faker

fake = Faker()


class TestDataFactory:
    """
    Centralized Test Data Factory for the IDOT ODA Customer Portal.
    Provides realistic, dynamically generated test data using Faker with zero hardcoding.
    """

    @staticmethod
    def today() -> str:
        """Returns the current date formatted as MM/DD/YYYY."""
        return datetime.now().strftime("%m/%d/%Y")

    @staticmethod
    def us_phone() -> str:
        """Generates a valid 10-digit US phone number in 000-000-0000 format."""
        return f"{fake.random_int(200, 999)}-{fake.random_int(200, 999)}-{fake.random_int(1000, 9999)}"

    @staticmethod
    def illinois_coordinates() -> Tuple[str, str]:
        """
        Generates realistic GPS coordinates bounded within the state of Illinois:
        Latitude: 37.5°N - 42.0°N
        Longitude: -91.0°W - -88.0°W
        """
        lat = str(round(fake.pyfloat(min_value=37.5, max_value=42.0, right_digits=4), 4))
        lon = str(round(fake.pyfloat(min_value=-91.0, max_value=-88.0, right_digits=4), 4))
        return lat, lon

    @classmethod
    def create_account(cls) -> Dict[str, Any]:
        """Generates dynamic Company Registration test data using Faker."""
        email = f"test_{fake.hexify(text='^^^^^^')}@gmail.com"
        phone = cls.us_phone()
        return {
            "company_name": f"Test {fake.company()[:20]} Corp",
            "address_1": fake.street_address(),
            "city": fake.city(),
            "zip_code": fake.zipcode()[:5],
            "phone": phone,
            "email": email,
            "billing_address_1": fake.street_address(),
            "billing_city": fake.city(),
            "billing_zip_code": fake.zipcode()[:5],
            "poc_fname": fake.first_name(),
            "poc_lname": fake.last_name(),
            "poc_email": email,
            "com_phone": phone,
        }

    @classmethod
    def primary_highway(cls) -> Dict[str, Any]:
        """
        Generates dynamic test data for Primary and Interstate Highway permit applications.
        All measurements, dates, and property owner details are dynamically created via Faker.
        """
        present_day = cls.today()
        phone = cls.us_phone()
        dist1 = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2)
        dist2 = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2)
        face_w = round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=2.0, max_value=5.0), 1)
        face_h = round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=1.0, max_value=3.0), 1)
        molding = round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=1.0, max_value=3.0), 1)
        height_top = round(fake.pyfloat(left_digits=2, right_digits=1, positive=True, min_value=10.0, max_value=15.0), 1)

        return {
            "erection_date": present_day,
            "face_width": face_w,
            "face_height": face_h,
            "height_to_molding": molding,
            "height_to_top": height_top,
            "airport_name": f"{fake.city()[:12]} Municipal Airport",
            "municipality": f"{fake.city()[:15]}",
            "zoning": f"Commercial C-{fake.random_int(1, 5)}",
            "zoning_1959": f"Commercial C-{fake.random_int(1, 5)}",
            "sign_distance1": f"{dist1:.2f}",
            "sign_distance2": f"{dist2:.2f}",
            "landmarks": f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}",
            "owner_name": fake.company(),
            "owner_address": fake.street_address(),
            "owner_city": fake.city(),
            "owner_zip": fake.zipcode()[:5],
            "owner_phone": phone,
            "owner_email": fake.email(),
            "signer_name": f"{fake.first_name()} {fake.last_name()}",
            "signer_title": f"{fake.job()[:25]}",
            "signature_date": present_day,
        }

    @classmethod
    def directional_sign(cls) -> Dict[str, Any]:
        """
        Generates dynamic test data for Directional Sign permit applications.
        Inherits structure from primary_highway and customizes directional properties.
        """
        data = cls.primary_highway()
        data["landmarks"] = f"Scenic Route Marker {fake.random_int(100, 999)} near Milepost {fake.random_int(10, 80)}"
        return data

    @classmethod
    def junkyard(cls) -> Dict[str, Any]:
        """
        Generates dynamic test data for Junkyard permit applications.
        All coordinates, establishment dates, distances, and owner details are dynamically created via Faker.
        """
        present_day = cls.today()
        phone = cls.us_phone()
        lat, lon = cls.illinois_coordinates()
        dist = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=0.5, max_value=8.5), 2)
        established_date = fake.date_between(start_date="-5y", end_date="today").strftime("%m/%d/%Y")

        return {
            "sec_of_state": f"UDL{fake.random_int(100000, 999999)}",
            "date_yard_established": established_date,
            "latitude": lat,
            "longitude": lon,
            "location_distance": dist,
            "route_landmarks": f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}",
            "municipality": f"{fake.city()[:15]}",
            "zoning_class": f"Commercial C-{fake.random_int(1, 5)}",
            "owner_name": fake.name(),
            "owner_address": fake.street_address(),
            "owner_city": fake.city(),
            "owner_zip": fake.zipcode()[:5],
            "owner_phone": phone,
            "owner_email": fake.email(),
            "signer_name": f"{fake.first_name()} {fake.last_name()}",
            "signer_title": f"{fake.job()[:25]}",
            "signature_date": present_day,
        }

    @classmethod
    def payment_card(cls) -> Dict[str, str]:
        """
        Generates dynamic cardholder and billing details for the test payment gateway.
        Uses standard sandbox test card token with realistic Faker customer information.
        """
        return {
            "card_number": "4111111111111111",
            "cvv": "111",
            "name": f"{fake.first_name()} {fake.last_name()}",
            "exp_month": "03",
            "exp_year": "2029",
            "zip_code": fake.zipcode()[:5],
        }

    @classmethod
    def permit_transfer(cls) -> Dict[str, Any]:
        """
        Generates dynamic test data for Permit Transfer applications.
        Permit number, company names, and signer details are dynamically created via Faker.
        """
        present_day = cls.today()
        return {
            "permit_number": str(fake.random_number(digits=6, fix_len=True)),
            "from_company": f"{fake.company()} LLC",
            "signer_name": f"{fake.first_name()} {fake.last_name()}",
            "signer_title": f"{fake.job()[:25]}",
            "signature_date": present_day,
        }


# ---------------------------------------------------------------------
# Top-level functional aliases for direct invocation and backward compatibility
# ---------------------------------------------------------------------
def generate_company_registration_data() -> Dict[str, Any]:
    return TestDataFactory.create_account()


def generate_primary_highway_test_data() -> Dict[str, Any]:
    return TestDataFactory.primary_highway()


def generate_directional_sign_test_data() -> Dict[str, Any]:
    return TestDataFactory.directional_sign()


def generate_junkyard_test_data() -> Dict[str, Any]:
    return TestDataFactory.junkyard()


def generate_payment_card_data() -> Dict[str, str]:
    return TestDataFactory.payment_card()


def generate_permit_transfer_test_data() -> Dict[str, Any]:
    return TestDataFactory.permit_transfer()
