"""
Financial Transactions Risk Classification (Rule-Based)

This script:
1) Loads raw CSV files (customers, transactions, payments)
2) Merges them into a single analysis table
3) Cleans common data issues (missing values, duplicates)
4) Engineers features (delay_days, is_paid)
5) Assigns a risk label (Low/Medium/High) using transparent business rules
6) Saves the final analysis table for SQL + Streamlit usage
"""

import os
import pandas as pd
import numpy as np


# configurable thresholds for risk assignment
HIGH_AMOUNT_THRESHOLD = 100_000
MEDIUM_AMOUNT_THRESHOLD = 50_000

HIGH_DELAY_THRESHOLD = 30
MEDIUM_DELAY_THRESHOLD = 10


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CUSTOMERS_CSV = os.path.join(DATA_DIR, "customers.csv")
TRANSACTIONS_CSV = os.path.join(DATA_DIR, "transactions.csv")
PAYMENTS_CSV = os.path.join(DATA_DIR, "payments.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "analysis_table.csv")


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load raw datasets from CSV and parse date columns."""
    customers = pd.read_csv(CUSTOMERS_CSV)
    transactions = pd.read_csv(TRANSACTIONS_CSV)
    payments = pd.read_csv(PAYMENTS_CSV)

    # Parse date columns and handle potential errors
    transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
    transactions["due_date"] = pd.to_datetime(transactions["due_date"])
    payments["payment_date"] = pd.to_datetime(payments["payment_date"], errors="coerce")

    return customers, transactions, payments


def assign_risk_level(amount: float, delay_days: float) -> str:
    """
    Assign a risk label using simple, explainable rules.

    High:
      - amount >= HIGH_AMOUNT_THRESHOLD OR delay_days >= HIGH_DELAY_THRESHOLD
    Medium:
      - amount >= MEDIUM_AMOUNT_THRESHOLD OR delay_days >= MEDIUM_DELAY_THRESHOLD
    Low:
      - otherwise
    """
    if amount >= HIGH_AMOUNT_THRESHOLD or delay_days >= HIGH_DELAY_THRESHOLD:
        return "High"
    if amount >= MEDIUM_AMOUNT_THRESHOLD or delay_days >= MEDIUM_DELAY_THRESHOLD:
        return "Medium"
    return "Low"


def main() -> None:
    # 1) Load raw data
    customers, transactions, payments = load_raw_data()
    print("✅ Loaded raw CSVs")

    # 2) Merge transactions + payments
    df = transactions.merge(payments, on="txn_id", how="left")
    print("✅ Merged transactions with payments")

    # 3) Basic cleaning: duplicates + missing values
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"✅ Dropped duplicates: {before - after} removed")

    # If payment_date is missing => unpaid
    df["is_paid"] = df["payment_date"].notna()

    # delay_days: payment_date - due_date
    df["delay_days"] = (df["payment_date"] - df["due_date"]).dt.days

    # For unpaid transactions, set delay_days to 0 (for risk calculation)
    df["delay_days"] = df["delay_days"].fillna(0)

    # 4) Add customer data (sector/country etc.)
    df = df.merge(customers, on="customer_id", how="left")
    print("✅ Added customer attributes")

    # Fill missing categorical values 
    df["sector"] = df["sector"].fillna("Unknown")
    df["country"] = df["country"].fillna("Unknown")

    # 5) Risk level assignment
    df["risk_level"] = df.apply(
        lambda r: assign_risk_level(float(r["amount"]), float(r["delay_days"])),
        axis=1
    )
    print("✅ Computed risk_level")

    # 6) Save the final analysis table
    df.to_csv(OUTPUT_CSV, index=False)
    print("🎉 Saved analysis table:", OUTPUT_CSV)

    # 7) Quick sanity outputs for verification
    print("\n--- Quick checks ---")
    print("Rows:", len(df))
    print("\nRisk distribution:")
    print(df["risk_level"].value_counts())

    print("\nTop 5 high-risk customers:")
    top_high = (
        df[df["risk_level"] == "High"]
        .groupby("customer_name")
        .size()
        .sort_values(ascending=False)
        .head(5)
    )
    print(top_high)


if __name__ == "__main__":
    main()
