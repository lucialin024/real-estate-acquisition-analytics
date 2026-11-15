
"""
Real Estate Acquisition & Investment Analytics
-----------------------------------------------
This script analyzes hypothetical Build-for-Rent (BFR)
investment opportunities using Python and Pandas.

Key Features:
    1. Property data exploration
    2. Financial performance calculations
    3. Acquisition screening and ranking
    4. Investment portfolio summary
    5. CSV report generation
"""

import pandas as pd


# ============================================================
# 1. DATA LOADING & EXPLORATION
# ============================================================

# Load property-level investment data
df = pd.read_csv("data/properties.csv")

print("\n" + "=" * 60)
print("REAL ESTATE ACQUISITION ANALYTICS")
print("=" * 60)

print("\nDATASET OVERVIEW")
print(f"Total Properties: {len(df)}")
print(f"Total Columns: {df.shape[1]}")

print("\nMISSING VALUES")
print(df.isnull().sum())


# ============================================================
# 2. PROPERTY VALUATION METRICS
# ============================================================

# Acquisition price per rental unit
df["price_per_unit"] = (
    df["acquisition_price"] / df["units"]
)

# Annual potential rental revenue
df["annual_gross_rent"] = (
    df["monthly_rent"] * df["units"] * 12
)

# Gross rental yield (stored as a decimal)
df["gross_rental_yield"] = (
    df["annual_gross_rent"] / df["acquisition_price"]
)


# ============================================================
# 3. NET OPERATING INCOME (NOI)
# ============================================================

# Adjust potential rental revenue for vacancy
df["effective_rental_income"] = (
    df["annual_gross_rent"] * (1 - df["vacancy_rate"])
)

# Annual operating expenses
df["operating_expenses"] = (
    df["effective_rental_income"]
    * df["operating_expense_ratio"]
)

# Annual Net Operating Income
df["noi"] = (
    df["effective_rental_income"]
    - df["operating_expenses"]
)


# ============================================================
# 4. CAPITALIZATION RATE
# ============================================================

# Cap rate = NOI / Acquisition Price
df["cap_rate"] = (
    df["noi"] / df["acquisition_price"]
)


# ============================================================
# 5. ACQUISITION SCREENING
# ============================================================

# Hypothetical investment criteria:
# - Minimum cap rate: 8%
# - Maximum acquisition price: $7 million
# - Maximum vacancy rate: 6%

qualified_deals = df[
    (df["cap_rate"] >= 0.08)
    & (df["acquisition_price"] <= 7_000_000)
    & (df["vacancy_rate"] <= 0.06)
].copy()

# Rank qualified deals by highest cap rate
ranked_deals = qualified_deals.sort_values(
    by="cap_rate",
    ascending=False
)


# ============================================================
# 6. INVESTMENT PORTFOLIO SUMMARY
# ============================================================

total_deals = len(ranked_deals)

total_investment = (
    ranked_deals["acquisition_price"].sum()
)

average_cap_rate = (
    ranked_deals["cap_rate"].mean()
)


# ============================================================
# 7. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PROPERTY FINANCIAL PERFORMANCE")
print("=" * 60)

# Create a formatted copy for reporting
report = df[
    [
        "city",
        "price_per_unit",
        "annual_gross_rent",
        "noi",
        "gross_rental_yield",
        "cap_rate",
    ]
].copy()

# Format financial metrics
for column in [
    "price_per_unit",
    "annual_gross_rent",
    "noi",
]:
    report[column] = report[column].map(
        lambda x: f"${x:,.2f}"
    )

for column in [
    "gross_rental_yield",
    "cap_rate",
]:
    report[column] = report[column].map(
        lambda x: f"{x:.2%}"
    )

print(report.to_string(index=False))


# Display qualified investments
print("\n" + "=" * 60)
print("QUALIFIED ACQUISITION OPPORTUNITIES")
print("=" * 60)

if ranked_deals.empty:
    print("No properties meet the investment criteria.")
else:
    qualified_report = ranked_deals[
        [
            "city",
            "acquisition_price",
            "noi",
            "cap_rate",
        ]
    ].copy()

    qualified_report["acquisition_price"] = (
        qualified_report["acquisition_price"].map(
            lambda x: f"${x:,.2f}"
        )
    )

    qualified_report["noi"] = (
        qualified_report["noi"].map(
            lambda x: f"${x:,.2f}"
        )
    )

    qualified_report["cap_rate"] = (
        qualified_report["cap_rate"].map(
            lambda x: f"{x:.2%}"
        )
    )

    print(qualified_report.to_string(index=False))


# Display investment summary
print("\n" + "=" * 60)
print("INVESTMENT PORTFOLIO SUMMARY")
print("=" * 60)

print(f"Qualified Deals: {total_deals}")
print(f"Total Acquisition Value: ${total_investment:,.2f}")
print(f"Average Cap Rate: {average_cap_rate:.2%}")


# ============================================================
# 8. EXPORT RESULTS
# ============================================================

# Export numerical results without display formatting
ranked_deals.to_csv(
    "data/qualified_acquisitions.csv",
    index=False
)

print("\nQualified acquisitions exported successfully!")