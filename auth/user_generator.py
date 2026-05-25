from faker import Faker
import uuid

from config import DEFAULT_USER_PASSWORD

fake = Faker()



def generate_user():

    return {
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "email": f"bot_{uuid.uuid4().hex[:8]}@mail.com",
        "password": DEFAULT_USER_PASSWORD,
        "company": fake.company(),
        "addressline": fake.street_address(),
        "apartment": fake.secondary_address(),
        "city": fake.city(),
        "country": "United States",
        "postalcode": fake.postcode()
    }