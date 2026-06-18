import pandas as pd
from faker import Faker
import random

# Fake data generator, UK style (names, emails, etc.)
fake = Faker('en_GB')

# "Seed" lagane se har baar same random data banega - testing ke liye useful
random.seed(42)
Faker.seed(42)

NUM_CUSTOMERS = 18000

customers = []

for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        "customer_id": f"cust_{i:06d}",
        "full_name": fake.name(),
        "email": fake.email(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80),
        "signup_date": fake.date_between(start_date="-2y", end_date="-1y"),
        "country": "GB"
    })

df_customers = pd.DataFrame(customers)
df_customers.to_csv("data/customers.csv", index=False)

print(f"Done! {len(df_customers)} customers saved to data/customers.csv")