# Financial Transactions Risk Classification Using Python and SQL

This project analyzes financial transaction data and classifies transactions into
Low, Medium, and High risk categories using a rule-based approach.

The goal is to demonstrate data handling, analysis, visualization, SQL integration,
and a simple presentation layer as required in the course project.

This project was developed as an individual final assignment for a Python & SQL course.
---

## Project Goal

- Classify financial transactions based on:
  - Transaction amount
  - Payment delay (delay_days)
- Perform exploratory data analysis (EDA)
- Use SQL for aggregation and querying
- Visualize insights using Python
- Build an interactive dashboard using Streamlit

---

## Dataset

- Synthetic dataset generated using Python
- Simulates real-world financial transactions
- Includes:
  - Customers
  - Transactions
  - Payment delays
- Used to ensure privacy and reproducibility

---

## Technologies Used

- Python (Pandas, NumPy)
- SQLite (SQL queries and aggregations)
- Matplotlib & Seaborn (visualizations)
- Streamlit (interactive dashboard)

---

## Project Structure
financial-risk-project/
│
├── app/
│   └── app.py                # Streamlit dashboard
│
├── src/
│   ├── 01_generate_data.py
│   ├── 02_clean_and_engineer.py
│   ├── 03_sql_load_and_queries.py
│   └── 04_visualizations.py
│
├── reports/
│   └── figures/              # Generated plots
│
├── requirements.txt
└── README.md

---

## How to Run the Project

1. Install dependencies:
```bash
pip install -r requirements.txt

2. Run data pipeline scripts
python src/01_generate_data.py
python src/02_clean_and_engineer.py
python src/03_sql_load_and_queries.py
python src/04_visualizations.py

3. Launch Streamlit dashboard:
streamlit run app/app.py

## Key Findings

- High-risk transactions represent a significant portion of total activity
- Payment delay is a stronger risk indicator than transaction amount
- Certain sectors and customers concentrate higher risk
- Risk patterns change over time

⸻

Author
	•	Name: Kaan Öztürk
	•	Course: Python & SQL Final Project
	•	Type: Individual project
