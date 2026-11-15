
"""
Five-Year Real Estate Cash Flow Forecast
---------------------------------------
Project: Real Estate Acquisition Analytics
Model: Simplified unlevered Build-for-Rent investment

All financial assumptions are hypothetical.
"""

import numpy_financial as npf
import pandas as pd
from pathlib import Path


# ============================================================
# 1. LOAD PROPERTY DATA
# ============================================================

project_root = Path(__file__).resolve().parent.parent

df = pd.read_csv(
    project_root / "data" / "properties.csv"
)

# Select Tempe as our first underwriting case
property_data = df.loc[
    df["property_id"] == "BFR001"
].iloc[0]


# ============================================================
# 2. INVESTMENT ASSUMPTIONS
# ============================================================

acquisition_price = property_data["acquisition_price"]

monthly_rent = property_data["monthly_rent"]
units = property_data["units"]

vacancy_rate = property_data["vacancy_rate"]
expense_ratio = property_data["operating_expense_ratio"]

annual_growth = 0.03
holding_period = 5
exit_cap_rate = 0.075
selling_cost_rate = 0.02


# ============================================================
# 3. CALCULATE YEAR 1 NOI
# ============================================================

annual_gross_rent = monthly_rent * units * 12

effective_income = annual_gross_rent * (1 - vacancy_rate)

year_1_noi = effective_income * (1 - expense_ratio)


# ============================================================
# 4. FORECAST ANNUAL NOI
# ============================================================

forecast = []

for year in range(1, holding_period + 1):

    projected_noi = year_1_noi * (
        (1 + annual_growth) ** (year - 1)
    )

    forecast.append({
        "year": year,
        "projected_noi": projected_noi
    })

forecast_df = pd.DataFrame(forecast)


# ============================================================
# 5. ESTIMATE EXIT VALUE
# ============================================================

year_6_noi = year_1_noi * (
    (1 + annual_growth) ** holding_period
)

exit_value = year_6_noi / exit_cap_rate

selling_costs = exit_value * selling_cost_rate

net_sale_proceeds = exit_value - selling_costs


# ============================================================
# 6. CALCULATE ANNUAL CASH FLOWS
# ============================================================

forecast_df["cash_flow"] = forecast_df["projected_noi"]

# Add sale proceeds to final year's cash flow
forecast_df.loc[
    forecast_df["year"] == holding_period,
    "cash_flow"
] += net_sale_proceeds



# ============================================================
# 7. INVESTMENT RETURN ANALYSIS
# ============================================================

# Year 0 is the acquisition cost (cash outflow)
initial_investment = -acquisition_price

# Combine Year 0 and Years 1-5 cash flows
cash_flows = [
    initial_investment,
    *forecast_df["cash_flow"].tolist()
]

# Required rate of return
discount_rate = 0.10

# Internal Rate of Return
irr = npf.irr(cash_flows)

# Net Present Value
npv = npf.npv(discount_rate, cash_flows)

# Investment multiple
total_distributions = sum(
    cash_flow for cash_flow in cash_flows
    if cash_flow > 0
)

investment_multiple = (
    total_distributions / acquisition_price
)

print("\nINVESTMENT RETURN ANALYSIS")
print("=" * 50)

print(f"IRR: {irr:.2%}")
print(f"NPV (10% Discount Rate): ${npv:,.2f}")
print(f"Investment Multiple: {investment_multiple:.2f}x")

# ============================================================
# 8. DISPLAY RESULTS
# ============================================================

print("\nFIVE-YEAR CASH FLOW FORECAST")
print("=" * 50)

print(f"Property: {property_data['city']}")
print(f"Acquisition Price: ${acquisition_price:,.2f}")
print(f"Year 1 NOI: ${year_1_noi:,.2f}")

print("\nANNUAL CASH FLOWS:")

print(
    forecast_df.round(2).to_string(index=False)
)

print(f"\nEstimated Exit Value: ${exit_value:,.2f}")
print(f"Net Sale Proceeds: ${net_sale_proceeds:,.2f}")


# ============================================================
# 9. EXPORT FORECAST
# ============================================================

output_path = (
    project_root / "data" / "tempe_cash_flow_forecast.csv"
)

forecast_df.to_csv(output_path, index=False)

print("\nCash flow forecast exported successfully!")