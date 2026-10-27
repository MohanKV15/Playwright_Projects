from datetime import datetime
from typing import Dict, Any
from faker import Faker

fake = Faker()


def generate_primary_highway_test_data() -> Dict[str, Any]:
    """
    Generates realistic, dynamic test data for Primary Highway permit application using Faker
    and always uses the present day for dates.
    """
    present_day = datetime.now().strftime("%m/%d/%Y")
    dist1 = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2)
    dist2 = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2)
    return {
        "erection_date": present_day,
        "face_width": 2.0,
        "face_height": 1.0,
        "height_to_molding": 1.0,
        "height_to_top": 10.0,
        "airport_name": f"{fake.city()[:12]} Municipal Airport",
        "municipality": f"{fake.city()[:15]}",
        "zoning": f"Commercial C-{fake.random_int(1, 5)}",
        "sign_distance1": f"{dist1:.2f}",
        "sign_distance2": f"{dist2:.2f}",
        "landmarks": f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}",
        "owner_name": f"{fake.company()}",
        "owner_address": fake.street_address(),
        "owner_city": fake.city(),
        "owner_zip": f"60{fake.random_int(100, 999)}",
        "owner_phone": "999-999-9999",
        "owner_email": fake.email(),
        "signer_name": f"{fake.first_name()} {fake.last_name()}",
        "signer_title": "Authorized Representative",
        "signature_date": present_day,
    }
