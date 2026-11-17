
from src.financial_model import calculate_levered_returns

results = calculate_levered_returns(
    acquisition_price=5_000_000,
    year_1_noi=350_000,
    noi_growth_rate=0.03,
    exit_cap_rate=0.055,
    ltv=0.70,
    interest_rate=0.065,
    annual_capex=25_000,
    holding_period=5,
)

for metric in [
    "loan_amount",
    "initial_equity",
    "unlevered_irr",
    "levered_irr",
    "equity_multiple",
    "remaining_loan_balance",
]:
    print(f"{metric}: {results[metric]:,.4f}")