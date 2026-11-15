
"""
Two-Variable Real Estate IRR Sensitivity Analysis
------------------------------------------------
Analyze the impact of NOI growth and exit cap rates
on an unlevered Build-for-Rent acquisition.

All assumptions are hypothetical.
"""

from pathlib import Path

import numpy_financial as npf
import pandas as pd


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

holding_period = 5
selling_cost_rate = 0.02

gross_rent = (
    property_data["monthly_rent"]
    * property_data["units"]
    * 12
)

effective_income = (
    gross_rent * (1 - property_data["vacancy_rate"])
)

year_1_noi = (
    effective_income
    * (1 - property_data["operating_expense_ratio"])
)


# ============================================================
# 3. SENSITIVITY ASSUMPTIONS
# ============================================================

noi_growth_rates = [
    0.01,
    0.02,
    0.03,
    0.04,
    0.05
]

exit_cap_rates = [
    0.065,
    0.070,
    0.075,
    0.080,
    0.085
]


# ============================================================
# 4. CALCULATE IRR FOR EACH SCENARIO
# ============================================================

results = []

for growth_rate in noi_growth_rates:

    # Forecast annual operating cash flows
    annual_noi = [
        year_1_noi * (1 + growth_rate) ** (year - 1)
        for year in range(1, holding_period + 1)
    ]

    # Forecast Year 6 NOI for terminal valuation
    year_6_noi = (
        year_1_noi * (1 + growth_rate) ** holding_period
    )

    for exit_cap_rate in exit_cap_rates:

        # Estimate property sale value
        exit_value = year_6_noi / exit_cap_rate

        net_sale_proceeds = (
            exit_value * (1 - selling_cost_rate)
        )

        # Year 0 acquisition + operating cash flows
        cash_flows = [-acquisition_price] + annual_noi.copy()

        # Add sale proceeds to final year
        cash_flows[-1] += net_sale_proceeds

        # Calculate investment IRR
        irr = npf.irr(cash_flows)

        results.append({
            "noi_growth_rate": growth_rate,
            "exit_cap_rate": exit_cap_rate,
            "irr": irr
        })


# ============================================================
# 5. CREATE SENSITIVITY MATRIX
# ============================================================

results_df = pd.DataFrame(results)

sensitivity_matrix = results_df.pivot(
    index="noi_growth_rate",
    columns="exit_cap_rate",
    values="irr"
)

# Display percentages for readability
formatted_matrix = sensitivity_matrix.map(
    lambda value: f"{value:.2%}"
)

formatted_matrix.index = [
    f"{rate:.1%}" for rate in formatted_matrix.index
]

formatted_matrix.columns = [
    f"{rate:.1%}" for rate in formatted_matrix.columns
]


# ============================================================
# 6. DISPLAY RESULTS
# ============================================================

print("\nTWO-VARIABLE IRR SENSITIVITY ANALYSIS")
print("=" * 60)

print("\nRows: Annual NOI Growth Rate")
print("Columns: Exit Cap Rate\n")

print(formatted_matrix.to_string())


# ============================================================
# 7. EXPORT RESULTS
# ============================================================

output_path = (
    project_root / "data" / "two_variable_sensitivity.csv"
)

sensitivity_matrix.to_csv(output_path)

print("\nSensitivity matrix exported successfully!")