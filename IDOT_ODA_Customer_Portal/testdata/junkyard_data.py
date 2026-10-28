from datetime import datetime
from typing import Dict, Any
from faker import Faker

fake = Faker()


def generate_junkyard_test_data() -> Dict[str, Any]:
    """
    Generates realistic, dynamic test data for Junkyard permit application using Faker
    and always uses the present day for dates.
    """
    present_day = datetime.now().strftime("%m/%d/%Y")
    phone_number = f"{fake.random_int(200, 999)}-{fake.random_int(200, 999)}-{fake.random_int(1000, 9999)}"

    # Generate dynamic coordinates within Illinois bounding box, distance, direction, and date via Faker
    lat = str(round(fake.pyfloat(min_value=37.5, max_value=42.0, right_digits=4), 4))
    lon = str(round(fake.pyfloat(min_value=-91.0, max_value=-88.0, right_digits=4), 4))
    dist = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=0.5, max_value=8.5), 2)
    direction = fake.random_element(elements=("East", "West", "North", "South"))
    established_date = fake.date_between(start_date="-5y", end_date="today").strftime("%m/%d/%Y")

    return {
        "sec_of_state": f"UDL{fake.random_int(100000, 999999)}",
        "date_yard_established": established_date,
        "latitude": lat,
        "longitude": lon,
        "location_distance": dist,
        "location_direction": direction,
        "route_landmarks": f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}",
        "municipality": f"{fake.city()[:15]}",
        "zoning_class": f"Commercial C-{fake.random_int(1, 5)}",
        "owner_name": fake.name(),
        "owner_address": fake.street_address(),
        "owner_city": fake.city(),
        "owner_zip": fake.zipcode(),
        "owner_phone": phone_number,
        "owner_email": fake.email(),
        "signer_name": f"{fake.first_name()} {fake.last_name()}",
        "signer_title": f"{fake.job()[:25]}",
        "signature_date": present_day,
    }
