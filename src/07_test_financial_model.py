
import math
from financial_model import calculate_investment_returns


def test_financial_model():
    # Simple investment with known expected results
    result = calculate_investment_returns(
        acquisition_price=1000000,
        year_1_noi=100000,
        noi_growth_rate=0.0,
        exit_cap_rate=0.10,
        holding_period=5,
        selling_cost_rate=0.0,
        discount_rate=0.10
    )

    # Expected: $100,000 NOI per year, $1M sale in year 5
    expected_cash_flows = [
        -1000000,
        100000,
        100000,
        100000,
        100000,
        1100000
    ]

    assert len(result["cash_flows"]) == 6

    for actual, expected in zip(
        result["cash_flows"], expected_cash_flows
    ):
        assert math.isclose(
            actual, expected, rel_tol=1e-9
        )

    assert math.isclose(
        result["irr"], 0.10, abs_tol=1e-9
    ), "IRR calculation is incorrect"

    assert math.isclose(
        result["npv"], 0.0, abs_tol=1e-6
    ), "NPV calculation is incorrect"

    assert math.isclose(
        result["investment_multiple"], 1.5,
        abs_tol=1e-9
    ), "Investment multiple calculation is incorrect"

    assert math.isclose(
        result["exit_value"], 1000000,
        abs_tol=1e-9
    ), "Exit valuation is incorrect"

    print("All financial model tests passed!")


if __name__ == "__main__":
    test_financial_model()
