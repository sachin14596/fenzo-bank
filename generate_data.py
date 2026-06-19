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

# ---- ACCOUNTS ----

account_types = ["current", "savings"]
tiers = ["standard", "plus", "premium"]
tier_weights = [0.7, 0.2, 0.1]
currencies = ["GBP", "EUR", "USD"]
currency_weights = [0.92, 0.05, 0.03]
statuses = ["active", "closed"]
status_weights = [0.95, 0.05]

accounts = []
account_counter = 1

for customer in customers:
    num_accounts = 2 if random.random() < 0.15 else 1

    for n in range(num_accounts):
        acc_type = "current" if n == 0 else "savings"

        accounts.append({
            "account_id": f"acc_{account_counter:06d}",
            "customer_id": customer["customer_id"],
            "account_type": acc_type,
            "currency": random.choices(currencies, weights=currency_weights)[0],
            "opened_at": fake.date_between(start_date=customer["signup_date"], end_date="today"),
            "status": random.choices(statuses, weights=status_weights)[0],
            "tier": random.choices(tiers, weights=tier_weights)[0],
        })
        account_counter += 1

df_accounts = pd.DataFrame(accounts)
df_accounts.to_csv("data/accounts.csv", index=False)

print(f"Done! {len(df_accounts)} accounts saved to data/accounts.csv")

# ---- POTS ----

pot_names = [
    "Holiday Fund", "Emergency Savings", "New Laptop", 
    "House Deposit", "Car Fund", "Wedding", "Christmas",
    "Rainy Day", "Investment Pot", "Side Hustle"
]

pots = []
pot_counter = 1

for account in accounts:
    # Sirf current accounts ke pots bante hain (savings account ke nahi)
    if account["account_type"] != "current":
        continue
    
    # 40% current accounts ka koi pot nahi
    if random.random() < 0.40:
        continue

    # 1-3 pots per account
    num_pots = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]

    for _ in range(num_pots):
        created = fake.date_between(
            start_date=account["opened_at"],
            end_date="today"
        )

        # 15% pots closed hain
        is_closed = random.random() < 0.15
        closed_at = fake.date_between(
            start_date=created,
            end_date="today"
        ) if is_closed else None

        pots.append({
            "pot_id": f"pot_{pot_counter:06d}",
            "account_id": account["account_id"],
            "pot_name": random.choice(pot_names),
            "created_at": created,
            "closed_at": closed_at,
            "target_amount_minor_units": random.choice([
                None, 
                random.randint(50000, 1000000)  # £500 to £10,000
            ])
        })
        pot_counter += 1

df_pots = pd.DataFrame(pots)
df_pots.to_csv("data/pots.csv", index=False)

print(f"Done! {len(df_pots)} pots saved to data/pots.csv")

# ---- EVENTS ----
import datetime

# Date range: 12 months
start_date = datetime.date(2024, 6, 1)
end_date = datetime.date(2025, 5, 31)
date_range = [
    start_date + datetime.timedelta(days=x)
    for x in range((end_date - start_date).days + 1)
]

# Sirf active current accounts events generate karenge
current_accounts = [
    a for a in accounts
    if a["account_type"] == "current" and a["status"] == "active"
]

# Active pot IDs
active_pot_ids = [p["pot_id"] for p in pots if p["closed_at"] is None]

# Merchant IDs (seeds me properly define karenge, abhi placeholder)
merchant_ids = [f"merch_{i:04d}" for i in range(1, 201)]

events = []
event_counter = 1

# Pending authorisations tracker:
# {account_id: [(auth_event_id, amount, merchant_id, auth_date)]}
# Yeh track karega ki kaunsa auth abhi settle nahi hua
pending_auths = {}

for current_date in date_range:
    is_weekend = current_date.weekday() >= 5
    daily_target = int(random.randint(35000, 42000) * (0.6 if is_weekend else 1.0))

    for _ in range(daily_target):
        account = random.choice(current_accounts)
        acc_id = account["account_id"]

        # Weighted event type
        event_type = random.choices([
            "card_payment_authorised",
            "card_payment_declined",
            "faster_payment_in",
            "faster_payment_out",
            "direct_debit_collected",
            "fx_conversion",
            "pot_transfer_in",
            "pot_transfer_out",
        ], weights=[30, 3, 15, 12, 8, 4, 5, 5])[0]

        # Random timestamp us din ka
        event_time = datetime.datetime.combine(current_date, datetime.time(
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59)
        ))

        merchant_id = None
        pot_id = None
        currency = "GBP"
        amount = 0

        # ---- CARD PAYMENT AUTHORISED ----
        if event_type == "card_payment_authorised":
            amount = -random.randint(50, 50000)
            merchant_id = random.choice(merchant_ids)

            # ~2% duplicate (microservice retry)
            is_duplicate = random.random() < 0.02
            evt_id = f"evt_{event_counter:08d}" if not is_duplicate else f"evt_{event_counter:08d}_dup"

            events.append({
                "event_id": evt_id,
                "event_timestamp": event_time,
                "account_id": acc_id,
                "event_type": "card_payment_authorised",
                "amount_minor_units": amount,
                "currency": currency,
                "merchant_id": merchant_id,
                "pot_id": None,
            })
            event_counter += 1

            # Pending auths me daalo — 95% settle honge baad me, 5% expire
            will_settle = random.random() > 0.05
            if will_settle:
                if acc_id not in pending_auths:
                    pending_auths[acc_id] = []
                pending_auths[acc_id].append({
                    "amount": amount,
                    "merchant_id": merchant_id,
                    "auth_date": current_date,
                })
            continue

        # ---- CARD PAYMENT DECLINED ----
        elif event_type == "card_payment_declined":
            amount = 0  # Declined — koi amount nahi
            merchant_id = random.choice(merchant_ids)

        # ---- FASTER PAYMENT IN ----
        elif event_type == "faster_payment_in":
            amount = random.randint(1000, 500000)

        # ---- FASTER PAYMENT OUT ----
        elif event_type == "faster_payment_out":
            amount = -random.randint(1000, 200000)

        # ---- DIRECT DEBIT ----
        elif event_type == "direct_debit_collected":
            # ~8% direct debits fail hote hain
            is_failed = random.random() < 0.08
            if is_failed:
                events.append({
                    "event_id": f"evt_{event_counter:08d}",
                    "event_timestamp": event_time,
                    "account_id": acc_id,
                    "event_type": "direct_debit_failed",
                    "amount_minor_units": 0,
                    "currency": "GBP",
                    "merchant_id": random.choice(merchant_ids),
                    "pot_id": None,
                })
                event_counter += 1

                # 3 din baad retry
                retry_date = current_date + datetime.timedelta(days=3)
                if retry_date <= end_date:
                    events.append({
                        "event_id": f"evt_{event_counter:08d}",
                        "event_timestamp": datetime.datetime.combine(
                            retry_date,
                            datetime.time(random.randint(6, 10), random.randint(0, 59))
                        ),
                        "account_id": acc_id,
                        "event_type": "direct_debit_collected",
                        "amount_minor_units": -random.randint(500, 150000),
                        "currency": "GBP",
                        "merchant_id": random.choice(merchant_ids),
                        "pot_id": None,
                    })
                    event_counter += 1
                continue
            else:
                amount = -random.randint(500, 150000)
                merchant_id = random.choice(merchant_ids)

        # ---- FX CONVERSION ----
        elif event_type == "fx_conversion":
            amount = -random.randint(1000, 100000)
            currency = random.choices(["EUR", "USD"], weights=[0.6, 0.4])[0]

        # ---- POT TRANSFERS ----
        elif event_type in ["pot_transfer_in", "pot_transfer_out"]:
            if not active_pot_ids:
                continue
            pot_id = random.choice(active_pot_ids)
            amount = random.randint(1000, 50000) if event_type == "pot_transfer_in" else -random.randint(1000, 50000)

        events.append({
            "event_id": f"evt_{event_counter:08d}",
            "event_timestamp": event_time,
            "account_id": acc_id,
            "event_type": event_type,
            "amount_minor_units": amount,
            "currency": currency,
            "merchant_id": merchant_id,
            "pot_id": pot_id,
        })
        event_counter += 1

    # ---- SETTLED PAYMENTS (pending auths process karo) ----
    # Har din check karo — jo auths 1-5 din purane hain, unhe settle karo
    to_remove = {}
    for acc_id, auth_list in pending_auths.items():
        settled = []
        remaining = []
        for auth in auth_list:
            days_pending = (current_date - auth["auth_date"]).days
            if days_pending >= random.randint(1, 5):
                # Settle karo
                events.append({
                    "event_id": f"evt_{event_counter:08d}",
                    "event_timestamp": datetime.datetime.combine(
                        current_date,
                        datetime.time(random.randint(0, 23), random.randint(0, 59))
                    ),
                    "account_id": acc_id,
                    "event_type": "card_payment_settled",
                    "amount_minor_units": auth["amount"],
                    "currency": "GBP",
                    "merchant_id": auth["merchant_id"],
                    "pot_id": None,
                })
                event_counter += 1
            else:
                remaining.append(auth)
        pending_auths[acc_id] = remaining

    # Progress print — har mahine
    if current_date.day == 1:
        print(f"  {current_date.strftime('%b %Y')} done — {len(events):,} events so far")

# ---- ACCOUNT OPENED EVENTS ----
# Har account ke liye pehla event account_opened hona chahiye
for account in current_accounts:
    events.append({
        "event_id": f"evt_open_{account['account_id']}",
        "event_timestamp": datetime.datetime.combine(
            account["opened_at"],
            datetime.time(random.randint(9, 17), random.randint(0, 59))
        ),
        "account_id": account["account_id"],
        "event_type": "account_opened",
        "amount_minor_units": 0,
        "currency": "GBP",
        "merchant_id": None,
        "pot_id": None,
    })

print(f"  Sorting events by timestamp...")
events.sort(key=lambda x: x["event_timestamp"])

# ---- SAVE ----
df_events = pd.DataFrame(events)
df_events.to_csv("data/events.csv", index=False)

print(f"Done! {len(df_events):,} events saved to data/events.csv")

# ---- LEDGER SNAPSHOTS ----

# Month-end dates for our date range
month_end_dates = []
for month_offset in range(12):
    year = 2024 + (6 + month_offset - 1) // 12
    month = (6 + month_offset - 1) % 12 + 1
    # Last day of each month
    if month == 12:
        last_day = datetime.date(year, 12, 31)
    else:
        last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    month_end_dates.append(last_day)

# Build a lookup: account_id -> list of settled movements by date
# (simplified — sum all settled/payment events per account per day)
print("  Building balance lookup from events...")

from collections import defaultdict
account_daily_balance = defaultdict(lambda: defaultdict(int))

for event in events:
    # Sirf balance-affecting events
    if event["event_type"] in [
        "card_payment_settled",
        "faster_payment_in",
        "faster_payment_out",
        "direct_debit_collected",
        "fx_conversion",
        "pot_transfer_in",
        "pot_transfer_out",
    ]:
        event_date = event["event_timestamp"].date()
        account_daily_balance[event["account_id"]][event_date] += event["amount_minor_units"]

snapshots = []

for account in accounts:
    acc_id = account["account_id"]
    running_balance = random.randint(10000, 500000)  # Opening balance £100-£5000

    for snap_date in month_end_dates:
        # Skip if account opened after this snapshot date
        if account["opened_at"] > snap_date:
            continue

        # Add all daily movements up to snap_date
        for day_offset in range(31):
            check_date = snap_date.replace(day=1) + datetime.timedelta(days=day_offset)
            if check_date > snap_date:
                break
            running_balance += account_daily_balance[acc_id].get(check_date, 0)

        # Floor at 0 (no overdrafts in this simulation)
        running_balance = max(0, running_balance)

        # ~2% rows me deliberate mismatch
        is_mismatched = random.random() < 0.02
        stated_balance = running_balance
        if is_mismatched:
            # Off by £1 to £500 (pence)
            error = random.randint(100, 50000) * random.choice([1, -1])
            stated_balance = max(0, running_balance + error)

        snapshots.append({
            "account_id": acc_id,
            "snapshot_date": snap_date,
            "stated_balance_minor_units": stated_balance,
            "is_mismatched": is_mismatched,  # Hum jaante hain kahan galti daali — debug ke liye
        })

df_snapshots = pd.DataFrame(snapshots)
df_snapshots.to_csv("data/ledger_snapshots.csv", index=False)

print(f"Done! {len(df_snapshots):,} snapshots saved to data/ledger_snapshots.csv")