import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "analysis_table.csv")

# dashboard configs

st.set_page_config(page_title="Financial Risk Dashboard", layout="wide")
st.title("💳 Financial Transactions Risk Dashboard")
st.caption("Rule-based risk classification using Python + SQL (SQLite) + Streamlit")

st.markdown(
    "This dashboard demonstrates a **rule-based baseline risk classification** approach "
    "using transaction amount and payment delay (**delay_days**)."
)

# loading data with caching
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Parse dates csv can contain invalid dates
    df["txn_date"] = pd.to_datetime(df["txn_date"], errors="coerce")
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")

    # Ensure expected columns exist
    if "is_paid" not in df.columns:
        df["is_paid"] = df["payment_date"].notna()

    return df

df = load_data(DATA_PATH)

# sidebar filters configs
st.sidebar.header("Filters")

risk_options = ["Low", "Medium", "High"]
selected_risks = st.sidebar.multiselect("Risk Level", risk_options, default=risk_options)

sector_options = sorted(df["sector"].dropna().unique().tolist())
selected_sectors = st.sidebar.multiselect("Sector", sector_options, default=sector_options)

min_date = df["txn_date"].min().date()
max_date = df["txn_date"].max().date()

date_range = st.sidebar.date_input(
    "Transaction Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# If user selects a single date, make it a valid range
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Prevent inverted range
if start_date > end_date:
    st.sidebar.error("Start date cannot be after end date.")
    st.stop()

st.sidebar.caption("Tip: Narrow filters to focus on High risk behavior.")

# applying filters
filtered = df[
    (df["risk_level"].isin(selected_risks)) &
    (df["sector"].isin(selected_sectors)) &
    (df["txn_date"].dt.date >= start_date) &
    (df["txn_date"].dt.date <= end_date)
].copy()

# if empty data entered, give warning and stop
if filtered.empty:
    st.warning("No data was found matching the selected date and filters.")
    st.stop()

# KPIs layout
total_txn = len(filtered)
total_amount = filtered["amount"].sum()
avg_delay = filtered["delay_days"].mean() if total_txn > 0 else 0
high_cnt = (filtered["risk_level"] == "High").sum()

paid_rate = (filtered["is_paid"].mean() * 100) if total_txn > 0 else 0
late_rate = ((filtered["delay_days"] > 0).mean() * 100) if total_txn > 0 else 0
high_ratio = ((filtered["risk_level"] == "High").mean() * 100) if total_txn > 0 else 0

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
c1.metric("Total Transactions", f"{total_txn:,}")
c2.metric("Total Amount", f"{total_amount:,.2f}")
c3.metric("Average Delay (days)", f"{avg_delay:.2f}")
c4.metric("High Risk Count", f"{high_cnt:,}")
c5.metric("High Risk Ratio (%)", f"{high_ratio:.2f}")
c6.metric("Paid Rate (%)", f"{paid_rate:.2f}")
c7.metric("Late Payment Rate (%)", f"{late_rate:.2f}")

st.divider()

# charts and tables layout
left, right = st.columns([1, 1])

with left:
    st.subheader("1) Risk Distribution")
    fig1, ax1 = plt.subplots()
    sns.countplot(data=filtered, x="risk_level", order=["Low", "Medium", "High"], ax=ax1)
    ax1.set_xlabel("Risk Level")
    ax1.set_ylabel("Count")
    st.pyplot(fig1)

    st.subheader("2) Delay Days Distribution")
    fig2, ax2 = plt.subplots()
    sns.histplot(data=filtered, x="delay_days", bins=40, kde=True, ax=ax2)
    ax2.set_xlabel("Delay Days")
    ax2.set_ylabel("Frequency")
    st.pyplot(fig2)

    st.subheader("3) Amount by Risk Level (Boxplot)")
    fig3, ax3 = plt.subplots()
    sns.boxplot(data=filtered, x="risk_level", y="amount", order=["Low", "Medium", "High"], ax=ax3)
    ax3.set_xlabel("Risk Level")
    ax3.set_ylabel("Amount")
    st.pyplot(fig3)

with right:
    st.subheader("4) Top 10 Customers (High Risk)")
    top_high = (
        filtered[filtered["risk_level"] == "High"]
        .groupby("customer_name")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="high_cnt")
    )

    if top_high.empty:
        st.info("No High Risk transactions for current filters.")
    else:
        fig4, ax4 = plt.subplots()
        sns.barplot(data=top_high, x="high_cnt", y="customer_name", ax=ax4)
        ax4.set_xlabel("High Risk Count")
        ax4.set_ylabel("Customer")
        st.pyplot(fig4)

    st.subheader("5) Transactions Table")
    show_cols = [
        "txn_id", "customer_name", "sector", "country",
        "txn_type", "currency", "amount",
        "txn_date", "due_date", "payment_date",
        "is_paid", "delay_days", "risk_level"
    ]
    available_cols = [c for c in show_cols if c in filtered.columns]
    st.dataframe(
        filtered[available_cols].sort_values("txn_date", ascending=False),
        use_container_width=True
    )

st.divider()

# extra analysis + visualizations

filtered["month"] = filtered["txn_date"].dt.to_period("M").astype(str)

with st.expander("More Analysis (Monthly Trend & Heatmap)", expanded=False):

    st.subheader("6) Monthly Total Amount Trend")
    monthly_amount = filtered.groupby("month")["amount"].sum().reset_index()

    fig5, ax5 = plt.subplots(figsize=(8, 3))
    sns.lineplot(data=monthly_amount, x="month", y="amount", marker="o", ax=ax5)
    ax5.set_xlabel("Month")
    ax5.set_ylabel("Total Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig5)

    st.subheader("7) Sector vs Risk Heatmap")
    pivot = pd.pivot_table(
        filtered,
        index="sector",
        columns="risk_level",
        values="txn_id",
        aggfunc="count",
        fill_value=0
    )

    for col in ["Low", "Medium", "High"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[["Low", "Medium", "High"]]

    fig6, ax6 = plt.subplots(figsize=(8, 3.2))
    sns.heatmap(pivot, annot=True, fmt="d", ax=ax6)
    ax6.set_xlabel("Risk Level")
    ax6.set_ylabel("Sector")
    plt.tight_layout()
    st.pyplot(fig6)


st.divider()

# Download filtered data

st.subheader("Download Filtered Data")
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download CSV",
    data=csv_data,
    file_name="filtered_transactions.csv",
    mime="text/csv"
)
