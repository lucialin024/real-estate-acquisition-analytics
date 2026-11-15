import sqlite3
import pandas as pd
from pathlib import Path

# Define project paths
project_root = Path(__file__).resolve().parent.parent

csv_path = project_root / "data" / "properties.csv"
db_path = project_root / "data" / "real_estate.db"

# Load property dataset
df = pd.read_csv(csv_path)

# Connect to SQLite database
with sqlite3.connect(db_path) as conn:

    # Create or replace the properties table
    df.to_sql(
        "properties",
        conn,
        if_exists="replace",
        index=False
    )

    # Verify the data
    result = pd.read_sql_query(
        "SELECT * FROM properties",
        conn
    )

print("DATABASE CREATED SUCCESSFULLY!")
print(f"Properties loaded: {len(result)}")
print(result.head())
