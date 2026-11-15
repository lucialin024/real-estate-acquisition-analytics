
"""
Reusable Real Estate Underwriting Functions

Calculate unlevered investment returns for
hypothetical Build-for-Rent acquisitions.
"""

import numpy_financial as npf


def calculate_investment_returns(
    acquisition_price,
    year_1_noi,
    noi_growth_rate,
    exit_cap_rate,
    holding_period=5,
    selling_cost_rate=0.02,
    discount_rate=0.10
):
    """
    Calculate projected investment returns.

    Returns:
        dict: IRR, NPV, investment multiple,
              exit value, and annual cash flows.
    """

    # Validate model assumptions
    if acquisition_price <= 0:
        raise ValueError("Acquisition price must be positive.")

    if year_1_noi < 0:
        raise ValueError("Year 1 NOI cannot be negative in this model.")

    if exit_cap_rate <= 0:
        raise ValueError("Exit cap rate must be positive.")

    if holding_period < 1 or not isinstance(holding_period, int):
        raise ValueError("Holding period must be a positive integer.")

    if not 0 <= selling_cost_rate < 1:
        raise ValueError("Selling cost rate must be between 0 and 1.")

    if noi_growth_rate <= -1:
        raise ValueError("NOI growth rate must be greater than -100%.")

    if discount_rate <= -1:
        raise ValueError("Discount rate must be greater than -100%.")

    # Forecast annual NOI
    annual_noi = [
        year_1_noi * (1 + noi_growth_rate) ** (year - 1)
        for year in range(1, holding_period + 1)
    ]

    # Estimate Year 6 NOI for a five-year holding period
    forward_noi = (
        year_1_noi * (1 + noi_growth_rate) ** holding_period
    )

    # Calculate terminal value
    exit_value = forward_noi / exit_cap_rate

    net_sale_proceeds = exit_value * (
        1 - selling_cost_rate
    )

    # Build cash flow series
    cash_flows = [-acquisition_price] + annual_noi.copy()

    cash_flows[-1] += net_sale_proceeds

    # Investment return metrics
    irr = npf.irr(cash_flows)
    npv = npf.npv(discount_rate, cash_flows)

    investment_multiple = (
        sum(cf for cf in cash_flows if cf > 0)
        / acquisition_price
    )

    return {
        "irr": irr,
        "npv": npv,
        "investment_multiple": investment_multiple,
        "exit_value": exit_value,
        "net_sale_proceeds": net_sale_proceeds,
        "cash_flows": cash_flows
    }