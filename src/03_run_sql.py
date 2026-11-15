
"""
Run multiple SQL analysis queries against the
real estate acquisition database.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Define project paths
project_root = Path(__file__).resolve().parent.parent

db_path = project_root / "data" / "real_estate.db"
sql_path = project_root / "sql" / "01_property_analysis.sql"

# Read SQL file
sql_script = sql_path.read_text(encoding="utf-8")

# Split SQL statements at semicolons
queries = [
    query.strip()
    for query in sql_script.split(";")
    if query.strip()
]

# Execute queries
with sqlite3.connect(db_path) as conn:

    for i, query in enumerate(queries, start=1):
        print("\n" + "=" * 60)
        print(f"SQL ANALYSIS {i}")
        print("=" * 60)

        results = pd.read_sql_query(query, conn)

        print(results.to_string(index=False))

print("\nAll SQL analyses completed successfully!")