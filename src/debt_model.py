def calculate_debt_schedule(
    purchase_price,
    ltv,
    annual_interest_rate,
    amortization_years=30,
    holding_years=5,
):
    """Calculate annual debt payments and loan balances."""

    loan_amount = purchase_price * ltv
    monthly_rate = annual_interest_rate / 12
    number_of_payments = amortization_years * 12

    if monthly_rate == 0:
        monthly_payment = loan_amount / number_of_payments
    else:
        monthly_payment = (
            loan_amount
            * monthly_rate
            / (1 - (1 + monthly_rate) ** (-number_of_payments))
        )

    balance = loan_amount
    schedule = []

    for year in range(1, holding_years + 1):
        annual_interest = 0.0
        annual_principal = 0.0

        for month in range(12):
            interest = balance * monthly_rate
            principal = min(monthly_payment - interest, balance)
            balance = max(0.0, balance - principal)

            annual_interest += interest
            annual_principal += principal

        schedule.append({
            "year": year,
            "interest": annual_interest,
            "principal": annual_principal,
            "debt_service": annual_interest + annual_principal,
            "ending_loan_balance": balance,
        })

    return {
        "loan_amount": loan_amount,
        "initial_equity": purchase_price - loan_amount,
        "monthly_payment": monthly_payment,
        "schedule": schedule,
    }