import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "finance.db")
CSV_PATH = os.path.join(DATA_DIR, "analysis_table.csv")

# read data from CSV
df = pd.read_csv(CSV_PATH)

# SQlite connection and setup
conn = sqlite3.connect(DB_PATH)

# write dataframe to SQL table
table_name = "transactions_analysis"
df.to_sql(table_name, conn, if_exists="replace", index=False)

print("✅ SQLite DB created and table added:")
print(f"➡ DB: {DB_PATH}")
print(f"➡ Table: {table_name}")
print(f"➡ Rows: {len(df)}")

# Define SQL queries for analysis
# These queries support the main exploratory questions of the project

# Define SQL queries used for exploratory analysis
queries = {
    "1) Risk level distribution (count)": """
        SELECT risk_level, COUNT(*) AS cnt
        FROM transactions_analysis
        GROUP BY risk_level
        ORDER BY cnt DESC;
    """,

    "2) Average transaction amount by risk level": """
        SELECT risk_level, ROUND(AVG(amount), 2) AS avg_amount
        FROM transactions_analysis
        GROUP BY risk_level
        ORDER BY avg_amount DESC;
    """,

    "3) Top 10 customers by number of high-risk transactions": """
        SELECT customer_name, COUNT(*) AS high_cnt
        FROM transactions_analysis
        WHERE risk_level = 'High'
        GROUP BY customer_name
        ORDER BY high_cnt DESC
        LIMIT 10;
    """,

    "4) Risk distribution by sector": """
        SELECT sector, risk_level, COUNT(*) AS cnt
        FROM transactions_analysis
        GROUP BY sector, risk_level
        ORDER BY sector, cnt DESC;
    """,

    "5) Monthly trend of high-risk transactions": """
        SELECT
            strftime('%Y-%m', txn_date) AS month,
            COUNT(*) AS high_cnt
        FROM transactions_analysis
        WHERE risk_level = 'High'
        GROUP BY month
        ORDER BY month;
    """
}


# run and print query results
for title, q in queries.items():
    print("\n" + "="*70)
    print(title)
    result = pd.read_sql_query(q, conn)
    print(result.head(20))

conn.close()
print("\n🎉 SQL query work complete!")
