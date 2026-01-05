import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "analysis_table.csv")
FIG_DIR = os.path.join(BASE_DIR, "reports", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# parse date columns and handle potential errors
df["txn_date"] = pd.to_datetime(df["txn_date"])
df["due_date"] = pd.to_datetime(df["due_date"])
df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")

print("✅ Data loaded:", df.shape)

# 1) Risk level distribution
plt.figure()
sns.countplot(data=df, x="risk_level", order=["Low", "Medium", "High"])
plt.title("Risk Level Distribution")
plt.xlabel("Risk Level")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "01_risk_distribution.png"), dpi=200)
plt.close()

# 2) Transaction amount distribution by risk level
plt.figure()
sns.boxplot(data=df, x="risk_level", y="amount", order=["Low", "Medium", "High"])
plt.title("Amount Distribution by Risk Level")
plt.xlabel("Risk Level")
plt.ylabel("Amount")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "02_amount_by_risk_boxplot.png"), dpi=200)
plt.close()

# 3) Payment delay distribution (histogram)
plt.figure()
sns.histplot(data=df, x="delay_days", bins=40, kde=True)
plt.title("Delay Days Distribution")
plt.xlabel("Delay Days")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "03_delay_days_hist.png"), dpi=200)
plt.close()

# 4) Monthly trend of high-risk transactions
df["month"] = df["txn_date"].dt.to_period("M").astype(str)
high_trend = (
    df[df["risk_level"] == "High"]
    .groupby("month")
    .size()
    .reset_index(name="high_cnt")
)

plt.figure()
sns.lineplot(data=high_trend, x="month", y="high_cnt", marker="o")
plt.title("Monthly High-Risk Transaction Trend")
plt.xlabel("Month")
plt.ylabel("High Risk Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "04_high_risk_monthly_trend.png"), dpi=200)
plt.close()

# 5) Risk distribution by sector
plt.figure()
sns.countplot(
    data=df,
    y="sector",
    hue="risk_level",
    hue_order=["Low", "Medium", "High"]
)
plt.title("Risk Level Counts by Sector")
plt.xlabel("Count")
plt.ylabel("Sector")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "05_risk_by_sector.png"), dpi=200)
plt.close()


# 6) Top 10 customers by number of high-risk transactions
top_high = (
    df[df["risk_level"] == "High"]
    .groupby("customer_name")
    .size()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="high_cnt")
)

plt.figure()
sns.barplot(data=top_high, x="high_cnt", y="customer_name")
plt.title("Top 10 Customers by High-Risk Transactions")
plt.xlabel("High Risk Count")
plt.ylabel("Customer")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "06_top10_customers_high_risk.png"), dpi=200)
plt.close()

print("🎉 Figures generated and saved:")
for f in sorted(os.listdir(FIG_DIR)):
    print(" -", f)
