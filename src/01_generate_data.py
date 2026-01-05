import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

rng = np.random.default_rng(42)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 1) CUSTOMERS // creating customers and setting attributes
n_customers = 120
sectors = ["Manufacturing", "Retail", "Services", "Technology", "Logistics"]
countries = ["PL", "TR", "DE", "FR", "NL"]

customers = pd.DataFrame({
    "customer_id": np.arange(1, n_customers + 1),
    "customer_name": [f"Customer_{i:03d}" for i in range(1, n_customers + 1)],
    "sector": rng.choice(sectors, size=n_customers),
    "country": rng.choice(countries, size=n_customers),
})

# 2) TRANSACTIONS
n_txn = 20000
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
days_range = (end_date - start_date).days

txn_dates = [start_date + timedelta(days=int(rng.integers(0, days_range))) for _ in range(n_txn)]
txn_types = rng.choice(["SALE", "PURCHASE"], size=n_txn, p=[0.6, 0.4])

amounts = rng.lognormal(mean=10.3, sigma=0.7, size=n_txn)
amounts = np.round(amounts, 2)

currencies = rng.choice(["PLN", "EUR", "USD"], size=n_txn, p=[0.75, 0.15, 0.10])

due_days = rng.integers(7, 61, size=n_txn)
due_dates = [d + timedelta(days=int(x)) for d, x in zip(txn_dates, due_days)]

transactions = pd.DataFrame({
    "txn_id": np.arange(1, n_txn + 1),
    "customer_id": rng.integers(1, n_customers + 1, size=n_txn),
    "txn_date": pd.to_datetime(txn_dates),
    "txn_type": txn_types,
    "amount": amounts,
    "currency": currencies,
    "due_date": pd.to_datetime(due_dates),
})

# Simulate data quality issues by introducing duplicate transactions

dup_n = int(0.005 * len(transactions))  # 0.5% duplicates
dups = transactions.sample(dup_n, random_state=42)
transactions = pd.concat([transactions, dups], ignore_index=True)

# 3) PAYMENTS
paid_prob = 0.88

n_rows = len(transactions)   # after adding duplicates
is_paid = rng.random(n_rows) < paid_prob

# payment delay relative to due_date: -5 to +60 days some early, some late ones.
delay_days = rng.integers(-5, 61, size=n_rows)

payment_dates = []
paid_amounts = []
for i in range(n_rows):
    if is_paid[i]:
        pdate = pd.to_datetime(transactions.loc[i, "due_date"]) + timedelta(days=int(delay_days[i]))
        payment_dates.append(pdate)
        paid_amounts.append(np.round(transactions.loc[i, "amount"] * rng.uniform(0.85, 1.0), 2))
    else:
        payment_dates.append(pd.NaT)
        paid_amounts.append(np.nan)

payments = pd.DataFrame({
    "payment_id": np.arange(1, n_rows + 1),
    "txn_id": transactions["txn_id"],
    "payment_date": pd.to_datetime(payment_dates),
    "paid_amount": paid_amounts,
})


customers.to_csv(os.path.join(DATA_DIR, "customers.csv"), index=False)
transactions.to_csv(os.path.join(DATA_DIR, "transactions.csv"), index=False)
payments.to_csv(os.path.join(DATA_DIR, "payments.csv"), index=False)

print("✅ Generated:")
print(" - data/customers.csv")
print(" - data/transactions.csv")
print(" - data/payments.csv")
