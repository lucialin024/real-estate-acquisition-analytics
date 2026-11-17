
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


from src.debt_model import calculate_debt_schedule


def calculate_levered_returns(
    acquisition_price,
    year_1_noi,
    noi_growth_rate,
    exit_cap_rate,
    ltv=0.70,
    interest_rate=0.065,
    amortization_years=30,
    holding_period=5,
    annual_capex=0,
    capex_growth_rate=0,
    selling_cost_rate=0.02,
    acquisition_cost_rate=0,
    loan_fee_rate=0,
    unlevered_discount_rate=0.10,
    equity_discount_rate=0.12,
):
    """
    Calculate property-level and equity-level
    discounted cash flows and investment returns.

    Assumes fixed-rate, fully amortizing debt
    and no refinancing during the hold period.
    """

    if acquisition_price <= 0 or year_1_noi < 0:
        raise ValueError("Invalid acquisition price or NOI.")

    if exit_cap_rate <= 0:
        raise ValueError("Exit cap rate must be positive.")

    if not isinstance(holding_period, int) or holding_period < 1:
        raise ValueError("Invalid holding period.")

    if not isinstance(amortization_years, int) or amortization_years < 1:
        raise ValueError("Invalid amortization period.")

    if not 0 <= ltv <= 1:
        raise ValueError("LTV must be between 0 and 1.")

    if interest_rate < 0 or annual_capex < 0:
        raise ValueError("Interest and CapEx cannot be negative.")

    if noi_growth_rate <= -1 or capex_growth_rate <= -1:
        raise ValueError("Growth rates must exceed -100%.")

    for rate in (
        selling_cost_rate, acquisition_cost_rate, loan_fee_rate
    ):
        if not 0 <= rate < 1:
            raise ValueError("Cost rates must be between 0 and 1.")

    if min(unlevered_discount_rate, equity_discount_rate) <= -1:
        raise ValueError("Invalid discount rate.")

    debt = calculate_debt_schedule(
        acquisition_price,
        ltv,
        interest_rate,
        amortization_years,
        holding_period,
    )

    loan_amount = debt["loan_amount"]
    initial_equity = (
        acquisition_price
        - loan_amount
        + acquisition_price * acquisition_cost_rate
        + loan_amount * loan_fee_rate
    )

    annual_results = []
    unlevered_cash_flows = [
        -acquisition_price * (1 + acquisition_cost_rate)
    ]
    levered_cash_flows = [-initial_equity]

    for year in range(1, holding_period + 1):
        noi = year_1_noi * (1 + noi_growth_rate) ** (year - 1)
        capex = annual_capex * (1 + capex_growth_rate) ** (year - 1)

        debt_year = debt["schedule"][year - 1]
        debt_service = debt_year["debt_service"]

        unlevered_cf = noi - capex
        levered_cf = unlevered_cf - debt_service

        dscr = noi / debt_service if debt_service > 0 else None

        annual_results.append({
            "year": year,
            "noi": noi,
            "capex": capex,
            "interest": debt_year["interest"],
            "principal": debt_year["principal"],
            "debt_service": debt_service,
            "dscr": dscr,
            "unlevered_cash_flow": unlevered_cf,
            "levered_cash_flow": levered_cf,
            "ending_loan_balance": debt_year["ending_loan_balance"],
        })

        unlevered_cash_flows.append(unlevered_cf)
        levered_cash_flows.append(levered_cf)

    # Terminal valuation uses the following year's NOI.
    forward_noi = year_1_noi * (
        1 + noi_growth_rate
    ) ** holding_period

    exit_value = forward_noi / exit_cap_rate
    net_sale_proceeds = exit_value * (1 - selling_cost_rate)

    remaining_loan = debt["schedule"][-1]["ending_loan_balance"]
    equity_sale_proceeds = net_sale_proceeds - remaining_loan

    unlevered_cash_flows[-1] += net_sale_proceeds
    levered_cash_flows[-1] += equity_sale_proceeds

    equity_contributions = -sum(
        min(cf, 0) for cf in levered_cash_flows
    )
    equity_distributions = sum(
        max(cf, 0) for cf in levered_cash_flows
    )

    return {
        "loan_amount": loan_amount,
        "initial_equity": initial_equity,
        "exit_value": exit_value,
        "net_sale_proceeds": net_sale_proceeds,
        "remaining_loan_balance": remaining_loan,
        "equity_sale_proceeds": equity_sale_proceeds,
        "unlevered_irr": npf.irr(unlevered_cash_flows),
        "levered_irr": npf.irr(levered_cash_flows),
        "unlevered_npv": npf.npv(
            unlevered_discount_rate, unlevered_cash_flows
        ),
        "levered_npv": npf.npv(
            equity_discount_rate, levered_cash_flows
        ),
        "equity_multiple": (
            equity_distributions / equity_contributions
            if equity_contributions > 0 else None
        ),
        "unlevered_cash_flows": unlevered_cash_flows,
        "levered_cash_flows": levered_cash_flows,
        "annual_results": annual_results,
    }
