import pandas as pd
import random

random.seed(42)

# ---- MERCHANTS SEED ----

merchant_data = [
    # (merchant_name, category, mcc_code)
    # Groceries
    ("Tesco", "groceries", 5411),
    ("Sainsbury's", "groceries", 5411),
    ("Asda", "groceries", 5411),
    ("Morrisons", "groceries", 5411),
    ("Lidl", "groceries", 5411),
    ("Aldi", "groceries", 5411),
    ("Waitrose", "groceries", 5411),
    ("Co-op", "groceries", 5411),
    ("Iceland", "groceries", 5411),
    ("M&S Food", "groceries", 5411),
    # Transport
    ("TfL", "transport", 4111),
    ("National Rail", "transport", 4112),
    ("Uber", "transport", 4121),
    ("Trainline", "transport", 4112),
    ("EasyJet", "transport", 4511),
    ("British Airways", "transport", 4511),
    ("Ryanair", "transport", 4511),
    ("Avanti West Coast", "transport", 4112),
    ("Greater Anglia", "transport", 4112),
    ("CrossCountry Trains", "transport", 4112),
    # Dining
    ("McDonald's", "dining", 5812),
    ("KFC", "dining", 5812),
    ("Subway", "dining", 5812),
    ("Nando's", "dining", 5812),
    ("Wagamama", "dining", 5812),
    ("Pret A Manger", "dining", 5812),
    ("Greggs", "dining", 5812),
    ("Pizza Hut", "dining", 5812),
    ("Domino's", "dining", 5812),
    ("Five Guys", "dining", 5812),
    # Entertainment
    ("Netflix", "entertainment", 7841),
    ("Spotify", "entertainment", 7922),
    ("Amazon Prime", "entertainment", 7841),
    ("Disney+", "entertainment", 7841),
    ("Apple TV+", "entertainment", 7841),
    ("Sky", "entertainment", 7922),
    ("Vue Cinema", "entertainment", 7832),
    ("Odeon", "entertainment", 7832),
    ("Cineworld", "entertainment", 7832),
    ("NOW TV", "entertainment", 7841),
    # Shopping
    ("Amazon", "shopping", 5999),
    ("ASOS", "shopping", 5691),
    ("Next", "shopping", 5691),
    ("H&M", "shopping", 5691),
    ("Zara", "shopping", 5691),
    ("Primark", "shopping", 5691),
    ("John Lewis", "shopping", 5311),
    ("Marks & Spencer", "shopping", 5311),
    ("Argos", "shopping", 5999),
    ("Currys", "shopping", 5734),
    # Bills/Utilities
    ("British Gas", "bills", 4900),
    ("EDF Energy", "bills", 4900),
    ("Thames Water", "bills", 4941),
    ("BT", "bills", 4813),
    ("Virgin Media", "bills", 4813),
    ("Sky Broadband", "bills", 4813),
    ("Council Tax", "bills", 9311),
    ("TV Licence", "bills", 7922),
    ("E.ON", "bills", 4900),
    ("Scottish Power", "bills", 4900),
    # Health
    ("Boots", "health", 5912),
    ("LloydsPharmacy", "health", 5912),
    ("Superdrug", "health", 5912),
    ("BUPA", "health", 8011),
    ("NHS Prescription", "health", 5912),
    ("PureGym", "health", 7941),
    ("The Gym Group", "health", 7941),
    ("David Lloyd", "health", 7941),
    ("Holland & Barrett", "health", 5912),
    ("Vision Express", "health", 8042),
]

# Expand to 200 merchants
expanded_merchants = list(merchant_data)
merchant_counter = len(expanded_merchants) + 1

categories_fill = [
    ("groceries", 5411), ("dining", 5812), ("shopping", 5999),
    ("transport", 4111), ("entertainment", 7841), ("bills", 4900),
    ("health", 5912)
]

while merchant_counter <= 200:
    cat, mcc = random.choice(categories_fill)
    expanded_merchants.append((f"Merchant {merchant_counter}", cat, mcc))
    merchant_counter += 1

merchants_rows = []
for i, (name, category, mcc) in enumerate(expanded_merchants, start=1):
    merchants_rows.append({
        "merchant_id": f"merch_{i:04d}",
        "merchant_name": name,
        "category": category,
        "mcc_code": mcc
    })

df_merchants = pd.DataFrame(merchants_rows)
df_merchants.to_csv("fenzo_dbt/seeds/merchants.csv", index=False)
print(f"Done! {len(df_merchants)} merchants saved to fenzo_dbt/seeds/merchants.csv")


# ---- FX RATES SEED ----
import datetime

# Approximate real historical rates for our date range
# Base rates (approximate averages for 2024-2025)
base_rates = {
    "EUR": 0.8521,  # EUR to GBP
    "USD": 0.7834,  # USD to GBP
}

fx_rows = []
start_date = datetime.date(2024, 6, 1)
end_date = datetime.date(2025, 5, 31)
date_range = [
    start_date + datetime.timedelta(days=x)
    for x in range((end_date - start_date).days + 1)
]

for rate_date in date_range:
    for currency, base_rate in base_rates.items():
        # Small daily fluctuation — realistic market movement
        daily_variation = random.uniform(-0.008, 0.008)
        rate = round(base_rate + daily_variation, 4)

        fx_rows.append({
            "rate_date": rate_date,
            "currency": currency,
            "rate_to_gbp": rate
        })

df_fx = pd.DataFrame(fx_rows)
df_fx.to_csv("fenzo_dbt/seeds/fx_rates.csv", index=False)
print(f"Done! {len(df_fx)} fx rates saved to fenzo_dbt/seeds/fx_rates.csv")