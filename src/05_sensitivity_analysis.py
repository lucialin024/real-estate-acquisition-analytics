
"""
Real Estate Acquisition Sensitivity Analysis
--------------------------------------------
Evaluate how different exit cap rates affect
the projected investment IRR.

All financial assumptions are hypothetical.
"""

import pandas as pd
import numpy_financial as npf
from pathlib import Path


# ============================================================
# 1. LOAD PROPERTY DATA
# ============================================================

project_root = Path(__file__).resolve().parent.parent

df = pd.read_csv(
    project_root / "data" / "properties.csv"
)

property_data = df.loc[
    df["property_id"] == "BFR001"
].iloc[0]


# ============================================================
# 2. BASE INVESTMENT ASSUMPTIONS
# ============================================================

acquisition_price = property_data["acquisition_price"]

annual_growth = 0.03
holding_period = 5
selling_cost_rate = 0.02

gross_rent = (
    property_data["monthly_rent"]
    * property_data["units"]
    * 12
)

effective_income = gross_rent * (
    1 - property_data["vacancy_rate"]
)

year_1_noi = effective_income * (
    1 - property_data["operating_expense_ratio"]
)


# ============================================================
# 3. PROJECT ANNUAL OPERATING CASH FLOWS
# ============================================================

annual_noi = [
    year_1_noi * (1 + annual_growth) ** (year - 1)
    for year in range(1, holding_period + 1)
]

year_6_noi = year_1_noi * (
    (1 + annual_growth) ** holding_period
)


# ============================================================
# 4. EXIT CAP RATE SENSITIVITY
# ============================================================

exit_cap_rates = [
    0.060,
    0.065,
    0.070,
    0.075,
    0.080,
    0.085,
    0.090
]

results = []

for exit_cap_rate in exit_cap_rates:

    exit_value = year_6_noi / exit_cap_rate

    net_sale_proceeds = exit_value * (
        1 - selling_cost_rate
    )

    # Initial acquisition outflow + Years 1-5 NOI
    cash_flows = [-acquisition_price] + annual_noi.copy()

    # Add net sale proceeds in Year 5
    cash_flows[-1] += net_sale_proceeds

    irr = npf.irr(cash_flows)

    results.append({
        "exit_cap_rate": exit_cap_rate,
        "exit_value": exit_value,
        "irr": irr
    })


# ============================================================
# 5. DISPLAY RESULTS
# ============================================================

results_df = pd.DataFrame(results)

print("\nEXIT CAP RATE SENSITIVITY ANALYSIS")
print("=" * 55)

display_df = results_df.copy()

display_df["exit_cap_rate"] = display_df[
    "exit_cap_rate"
].map("{:.2%}".format)

display_df["exit_value"] = display_df[
    "exit_value"
].map("${:,.0f}".format)

display_df["irr"] = display_df[
    "irr"
].map("{:.2%}".format)

print(display_df.to_string(index=False))


# ============================================================
# 6. EXPORT RESULTS
# ============================================================

output_path = (
    project_root / "data" / "exit_cap_sensitivity.csv"
)

results_df.to_csv(output_path, index=False)

print("\nSensitivity analysis exported successfully!")