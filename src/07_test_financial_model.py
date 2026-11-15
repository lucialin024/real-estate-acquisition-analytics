
from financial_model import calculate_investment_returns


# Test the hypothetical Tempe acquisition
results = calculate_investment_returns(
    acquisition_price=4_200_000,
    year_1_noi=326_040,
    noi_growth_rate=0.03,
    exit_cap_rate=0.075,
    holding_period=5
)

print("\nREAL ESTATE INVESTMENT RETURN ANALYSIS")
print("=" * 50)

print(f"IRR: {results['irr']:.2%}")
print(f"NPV: ${results['npv']:,.2f}")
print(f"Investment Multiple: {results['investment_multiple']:.2f}x")
print(f"Exit Value: ${results['exit_value']:,.2f}")

print("\nAnnual Cash Flows:")
for year, cash_flow in enumerate(results["cash_flows"]):
    print(f"Year {year}: ${cash_flow:,.2f}")