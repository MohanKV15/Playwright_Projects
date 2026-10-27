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
    face_w = round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=2.0, max_value=5.0), 1)
    face_h = round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=1.0, max_value=3.0), 1)
    molding = round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=1.0, max_value=3.0), 1)
    height_top = round(fake.pyfloat(left_digits=2, right_digits=1, positive=True, min_value=10.0, max_value=15.0), 1)
    phone_number = f"{fake.random_int(200, 999)}-{fake.random_int(200, 999)}-{fake.random_int(1000, 9999)}"

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
        "owner_name": f"{fake.company()}",
        "owner_address": fake.street_address(),
        "owner_city": fake.city(),
        "owner_zip": f"60{fake.random_int(100, 999)}",
        "owner_phone": phone_number,
        "owner_email": fake.email(),
        "signer_name": f"{fake.first_name()} {fake.last_name()}",
        "signer_title": f"{fake.job()[:25]}",
        "signature_date": present_day,
    }
