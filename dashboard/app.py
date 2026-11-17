
"""
Real Estate Acquisition & IRR Analytics Dashboard

Interactive real estate investment underwriting platform.
Includes unlevered returns, sensitivity analysis,
debt financing, and discounted cash flow modeling.

Dataset: Synthetic Arizona Build-for-Rent properties.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Real Estate Investment Analytics",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.financial_model import (
    calculate_investment_returns,
    calculate_levered_returns,
)


# ============================================================
# 2. DESIGN SETTINGS
# ============================================================

TEAL = "#36C4A0"
BLUE = "#638BFF"
ORANGE = "#E5A365"
BACKGROUND = "#0B1220"
TEXT = "#E8EEF5"

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1450px;
        }

        div[data-testid="stMetric"] {
            background-color: #162235;
            border: 1px solid #293A51;
            border-radius: 12px;
            padding: 18px;
        }

        div[data-testid="stMetricLabel"] {
            color: #A7B8CD;
        }

        div[data-testid="stMetricValue"] {
            color: #F3F7FC;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. LOAD PROPERTY DATA
# ============================================================

@st.cache_data
def load_properties():
    return pd.read_csv(
        PROJECT_ROOT / "data" / "properties.csv"
    )


df = load_properties()


# ============================================================
# 4. SIDEBAR — INVESTMENT ASSUMPTIONS
# ============================================================

with st.sidebar:

    st.title("Investment Studio")
    st.caption("BUILD-FOR-RENT | UNDERWRITING")
    st.divider()

    selected_property = st.selectbox(
        "Investment Opportunity",
        df["property_id"].tolist(),
        format_func=lambda property_id: (
            f"{df.loc[df['property_id'] == property_id, 'city'].iloc[0]}"
            f" · {property_id}"
        ),
    )

    property_data = df.loc[
        df["property_id"] == selected_property
    ].iloc[0]

    st.subheader("Underwriting Assumptions")

    acquisition_price = st.number_input(
        "Acquisition Price ($)",
        min_value=100_000.0,
        value=float(property_data["acquisition_price"]),
        step=50_000.0,
        format="%.0f",
    )

    noi_growth_rate = st.slider(
        "Annual NOI Growth (%)",
        0.0, 8.0, 3.0, 0.5
    ) / 100

    exit_cap_rate = st.slider(
        "Exit Cap Rate (%)",
        5.0, 10.0, 7.5, 0.25
    ) / 100

    holding_period = st.slider(
        "Holding Period (Years)",
        3, 10, 5
    )

    required_return = st.slider(
        "Required Return (%)",
        5.0, 20.0, 10.0, 0.5
    ) / 100

    st.divider()

    # New financing assumptions
    with st.expander(
        "Debt Financing & DCF Inputs",
        expanded=False
    ):

        st.caption(
            "Adjust financing and capital expenditure assumptions."
        )

        ltv = st.slider(
            "Loan-to-Value (%)",
            0, 90, 70, 5
        ) / 100

        interest_rate = st.slider(
            "Annual Interest Rate (%)",
            0.0, 15.0, 6.5, 0.25
        ) / 100

        amortization_years = st.number_input(
            "Amortization Period (Years)",
            min_value=1,
            max_value=40,
            value=30,
            step=1,
        )

        annual_capex = st.number_input(
            "Year 1 Annual CapEx ($)",
            min_value=0.0,
            value=25_000.0,
            step=5_000.0,
        )

        capex_growth_rate = st.slider(
            "Annual CapEx Growth (%)",
            0.0, 10.0, 2.0, 0.5
        ) / 100

        acquisition_cost_rate = st.slider(
            "Acquisition Closing Costs (%)",
            0.0, 10.0, 1.0, 0.25
        ) / 100

        loan_fee_rate = st.slider(
            "Loan Origination Fees (%)",
            0.0, 5.0, 1.0, 0.25
        ) / 100

        equity_discount_rate = st.slider(
            "Required Equity Return (%)",
            5.0, 30.0, 12.0, 0.5
        ) / 100

    st.divider()

    st.caption(
        "Educational model using synthetic property data."
    )


# ============================================================
# 5. PROPERTY FINANCIAL CALCULATIONS
# ============================================================

annual_gross_rent = (
    property_data["monthly_rent"]
    * property_data["units"]
    * 12
)

effective_rental_income = (
    annual_gross_rent
    * (1 - property_data["vacancy_rate"])
)

year_1_noi = (
    effective_rental_income
    * (1 - property_data["operating_expense_ratio"])
)

going_in_cap_rate = year_1_noi / acquisition_price


# ============================================================
# 6. INVESTMENT RETURN CALCULATIONS
# ============================================================

# Original unlevered screening model
results = calculate_investment_returns(
    acquisition_price=acquisition_price,
    year_1_noi=year_1_noi,
    noi_growth_rate=noi_growth_rate,
    exit_cap_rate=exit_cap_rate,
    holding_period=holding_period,
    discount_rate=required_return,
)

meets_hurdle = results["irr"] >= required_return


# New leveraged DCF model
levered_results = calculate_levered_returns(
    acquisition_price=acquisition_price,
    year_1_noi=year_1_noi,
    noi_growth_rate=noi_growth_rate,
    exit_cap_rate=exit_cap_rate,
    ltv=ltv,
    interest_rate=interest_rate,
    amortization_years=int(amortization_years),
    holding_period=holding_period,
    annual_capex=annual_capex,
    capex_growth_rate=capex_growth_rate,
    selling_cost_rate=0.02,
    acquisition_cost_rate=acquisition_cost_rate,
    loan_fee_rate=loan_fee_rate,
    unlevered_discount_rate=required_return,
    equity_discount_rate=equity_discount_rate,
)


# ============================================================
# 7. BUILD CASH FLOW DATA
# ============================================================

annual_noi = [
    year_1_noi * (1 + noi_growth_rate) ** (year - 1)
    for year in range(1, holding_period + 1)
]

cash_flow_df = pd.DataFrame({
    "Year": range(holding_period + 1),
    "Cash Flow": results["cash_flows"],
})

operating_cash_flows = [0] + annual_noi

sale_cash_flows = (
    [0] * holding_period
    + [results["net_sale_proceeds"]]
)


# ============================================================
# 8. DASHBOARD HEADER
# ============================================================

st.caption(
    "INVESTMENT ANALYTICS / ACQUISITION UNDERWRITING"
)

st.title("Real Estate Investment Dashboard")

st.write(
    "Analyze acquisition opportunities, forecast "
    "investment performance, and evaluate financial risk."
)

st.divider()

header_left, header_right = st.columns([3, 1])

with header_left:
    st.subheader(
        f"{property_data['city']} | Build-for-Rent"
    )

    st.caption(
        f"Property ID: {selected_property} | "
        f"{int(property_data['units'])} Rental Units | "
        f"{holding_period}-Year Holding Period"
    )

with header_right:
    if meets_hurdle:
        st.success("Meets Return Hurdle")
    else:
        st.warning("Below Return Hurdle")


# ============================================================
# 9. INVESTMENT PERFORMANCE
# ============================================================

st.subheader("Investment Performance")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Projected Unlevered IRR",
    f"{results['irr']:.2%}",
    delta=(
        f"{(results['irr'] - required_return) * 100:+.2f} pp"
        " vs. required return"
    ),
)

col2.metric(
    f"NPV @ {required_return:.1%}",
    f"${results['npv']:,.0f}",
)

col3.metric(
    "Investment Multiple",
    f"{results['investment_multiple']:.2f}x",
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Acquisition Price",
    f"${acquisition_price / 1_000_000:.2f}M",
)

col5.metric(
    "Year 1 NOI",
    f"${year_1_noi:,.0f}",
)

col6.metric(
    "Going-In Cap Rate",
    f"{going_in_cap_rate:.2%}",
)

st.divider()


# ============================================================
# 10. DASHBOARD NAVIGATION
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Cash Flow Analysis",
    "Sensitivity Analysis",
    "Investment Summary",
    "Debt Financing & DCF",
])


# ============================================================
# TAB 1 — CASH FLOW ANALYSIS
# ============================================================

with tab1:

    st.subheader("Projected Investment Cash Flows")

    st.caption(
        "Operating cash flows, acquisition investment, "
        "and terminal sale proceeds."
    )

    cash_flow_chart = go.Figure()

    cash_flow_chart.add_bar(
        x=cash_flow_df["Year"],
        y=operating_cash_flows,
        name="Operating NOI",
        marker_color=TEAL,
    )

    cash_flow_chart.add_bar(
        x=cash_flow_df["Year"],
        y=sale_cash_flows,
        name="Net Sale Proceeds",
        marker_color=BLUE,
    )

    cash_flow_chart.add_bar(
        x=[0],
        y=[-acquisition_price],
        name="Acquisition Investment",
        marker_color=ORANGE,
    )

    cash_flow_chart.update_layout(
        barmode="relative",
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font_color=TEXT,
        height=430,
        xaxis_title="Investment Year",
        yaxis_title="Cash Flow ($)",
        legend=dict(
            orientation="h",
            y=-0.25,
        ),
    )

    cash_flow_chart.update_xaxes(dtick=1)

    st.plotly_chart(
        cash_flow_chart,
        width="stretch",
        theme=None,
    )

    st.subheader("Investment Cash Flow Schedule")

    st.dataframe(
        cash_flow_df.style.format({
            "Cash Flow": "${:,.2f}"
        }),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download Cash Flow CSV",
        data=cash_flow_df.to_csv(index=False),
        file_name=f"{selected_property}_cash_flows.csv",
        mime="text/csv",
    )


# ============================================================
# TAB 2 — IRR SENSITIVITY ANALYSIS
# ============================================================

with tab2:

    st.subheader("IRR Sensitivity Matrix")

    st.caption(
        "Analyze how NOI growth and exit capitalization "
        "rates impact projected investment IRR."
    )

    growth_rates = [
        0.01, 0.02, 0.03, 0.04, 0.05
    ]

    exit_cap_rates = [
        0.065, 0.070, 0.075, 0.080, 0.085
    ]

    sensitivity_results = []

    for growth in growth_rates:

        for cap in exit_cap_rates:

            scenario = calculate_investment_returns(
                acquisition_price=acquisition_price,
                year_1_noi=year_1_noi,
                noi_growth_rate=growth,
                exit_cap_rate=cap,
                holding_period=holding_period,
                discount_rate=required_return,
            )

            sensitivity_results.append({
                "NOI Growth": f"{growth:.1%}",
                "Exit Cap Rate": f"{cap:.1%}",
                "IRR": scenario["irr"],
            })

    sensitivity_df = pd.DataFrame(
        sensitivity_results
    )

    sensitivity_matrix = sensitivity_df.pivot(
        index="NOI Growth",
        columns="Exit Cap Rate",
        values="IRR",
    )

    heatmap = go.Figure(
        data=go.Heatmap(
            z=sensitivity_matrix.values * 100,
            x=sensitivity_matrix.columns.tolist(),
            y=sensitivity_matrix.index.tolist(),
            text=[
                [f"{value:.2%}" for value in row]
                for row in sensitivity_matrix.values
            ],
            texttemplate="%{text}",
            colorscale=[
                [0.0, "#B85C5C"],
                [0.5, "#243D54"],
                [1.0, TEAL],
            ],
            showscale=False,
        )
    )

    heatmap.update_layout(
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font_color=TEXT,
        height=430,
        xaxis_title="Exit Cap Rate",
        yaxis_title="Annual NOI Growth",
    )

    st.plotly_chart(
        heatmap,
        width="stretch",
        theme=None,
    )

    st.subheader("Sensitivity Data")

    formatted_matrix = sensitivity_matrix.map(
        lambda value: f"{value:.2%}"
    )

    st.dataframe(
        formatted_matrix,
        width="stretch",
    )


# ============================================================
# TAB 3 — INVESTMENT DECISION SUMMARY
# ============================================================

with tab3:

    st.subheader("Investment Decision Summary")

    if meets_hurdle:
        st.success(
            "The selected acquisition meets the "
            "required return under current assumptions."
        )
    else:
        st.warning(
            "The selected acquisition falls below the "
            "required return under current assumptions."
        )

    st.write(
        f"The **{property_data['city']}** acquisition "
        f"has a projected unlevered IRR of "
        f"**{results['irr']:.2%}**, compared with a "
        f"required return of **{required_return:.2%}**."
    )

    st.write(
        f"The property has an estimated exit value of "
        f"**${results['exit_value']:,.0f}**, "
        f"based on an exit cap rate of "
        f"**{exit_cap_rate:.2%}**."
    )

    st.subheader("Key Underwriting Assumptions")

    assumptions_df = pd.DataFrame({
        "Assumption": [
            "Acquisition Price",
            "Year 1 NOI",
            "Annual NOI Growth",
            "Exit Cap Rate",
            "Holding Period",
            "Required Return",
            "Selling Cost Rate",
        ],
        "Value": [
            f"${acquisition_price:,.0f}",
            f"${year_1_noi:,.0f}",
            f"{noi_growth_rate:.2%}",
            f"{exit_cap_rate:.2%}",
            f"{holding_period} years",
            f"{required_return:.2%}",
            "2.00%",
        ],
    })

    st.dataframe(
        assumptions_df,
        width="stretch",
        hide_index=True,
    )

    st.info(
        "This is a preliminary investment screening "
        "result, not an investment recommendation."
    )


# ============================================================
# TAB 4 — DEBT FINANCING & DCF ANALYSIS
# ============================================================

with tab4:

    st.subheader(
        "Debt Financing & Discounted Cash Flow"
    )

    st.caption(
        "Evaluate property-level and equity-level returns "
        "after financing, capital expenditures, "
        "closing costs, and debt repayment."
    )

    # --------------------------------------------------------
    # A. FINANCING METRICS
    # --------------------------------------------------------

    st.subheader("Financing Overview")

    a, b, c, d = st.columns(4)

    a.metric(
        "Loan Amount",
        f"${levered_results['loan_amount']:,.0f}",
    )

    b.metric(
        "Initial Equity",
        f"${levered_results['initial_equity']:,.0f}",
    )

    c.metric(
        "Unlevered IRR (After CapEx)",
        f"{levered_results['unlevered_irr']:.2%}",
    )

    d.metric(
        "Levered IRR",
        f"{levered_results['levered_irr']:.2%}",
    )

    e, f, g, h = st.columns(4)

    e.metric(
        "Equity Multiple",
        f"{levered_results['equity_multiple']:.2f}x",
    )

    f.metric(
        "Equity NPV",
        f"${levered_results['levered_npv']:,.0f}",
    )

    g.metric(
        "Remaining Debt at Exit",
        f"${levered_results['remaining_loan_balance']:,.0f}",
    )

    annual = pd.DataFrame(
        levered_results["annual_results"]
    )

    operating_dscr = annual.loc[
        annual["debt_service"] > 0, "dscr"
    ]

    minimum_dscr = (
        operating_dscr.min()
        if not operating_dscr.empty
        else None
    )

    h.metric(
        "Minimum Annual DSCR",
        (
            f"{minimum_dscr:.2f}x"
            if minimum_dscr is not None
            else "N/A"
        ),
    )

    st.info(
        "The unlevered IRR in this tab deducts "
        "capital expenditures and acquisition costs, "
        "unlike the original simplified screening model."
    )

    st.divider()

    # --------------------------------------------------------
    # B. LEVERED VS UNLEVERED CASH FLOWS
    # --------------------------------------------------------

    st.subheader("Investment Cash Flow Comparison")

    years = list(range(holding_period + 1))

    comparison_chart = go.Figure()

    comparison_chart.add_trace(
        go.Bar(
            name="Unlevered Cash Flow",
            x=years,
            y=levered_results["unlevered_cash_flows"],
            marker_color=TEAL,
        )
    )

    comparison_chart.add_trace(
        go.Bar(
            name="Levered Equity Cash Flow",
            x=years,
            y=levered_results["levered_cash_flows"],
            marker_color=BLUE,
        )
    )

    comparison_chart.update_layout(
        barmode="group",
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font_color=TEXT,
        height=430,
        xaxis_title="Investment Year",
        yaxis_title="Cash Flow ($)",
        legend=dict(
            orientation="h",
            y=-0.25,
        ),
    )

    comparison_chart.update_xaxes(dtick=1)

    st.plotly_chart(
        comparison_chart,
        width="stretch",
        theme=None,
    )

    st.divider()

    # --------------------------------------------------------
    # C. FIVE-YEAR DCF AND DEBT SCHEDULE
    # --------------------------------------------------------

    st.subheader(
        "Annual Operating Cash Flow & Debt Schedule"
    )

    operating_table = annual.rename(
        columns={
            "year": "Year",
            "noi": "NOI",
            "capex": "CapEx",
            "interest": "Interest",
            "principal": "Principal",
            "debt_service": "Debt Service",
            "dscr": "DSCR",
            "unlevered_cash_flow": "Unlevered CF",
            "levered_cash_flow": "Levered CF",
            "ending_loan_balance": "Ending Loan Balance",
        }
    )

    money_columns = [
        "NOI",
        "CapEx",
        "Interest",
        "Principal",
        "Debt Service",
        "Unlevered CF",
        "Levered CF",
        "Ending Loan Balance",
    ]

    format_columns = {
        col: "${:,.0f}"
        for col in money_columns
    }

    format_columns["DSCR"] = "{:.2f}x"

    st.dataframe(
        operating_table.style.format(
            format_columns,
            na_rep="N/A"
        ),
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Annual operating cash flows exclude sale proceeds. "
        "The schedule below includes the terminal sale "
        "and outstanding loan repayment."
    )

    # --------------------------------------------------------
    # D. COMPLETE INVESTMENT CASH FLOWS
    # --------------------------------------------------------

    st.subheader("DCF Investment Cash Flow Schedule")

    investment_cash_flows = pd.DataFrame({
        "Year": years,
        "Unlevered Investment CF":
            levered_results["unlevered_cash_flows"],
        "Levered Equity CF":
            levered_results["levered_cash_flows"],
    })

    st.dataframe(
        investment_cash_flows.style.format({
            "Unlevered Investment CF": "${:,.0f}",
            "Levered Equity CF": "${:,.0f}",
        }),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download Detailed DCF Schedule (CSV)",
        data=operating_table.to_csv(index=False),
        file_name=f"{selected_property}_debt_dcf.csv",
        mime="text/csv",
    )

    st.divider()

    # --------------------------------------------------------
    # E. TERMINAL VALUATION
    # --------------------------------------------------------

    st.subheader("Exit Valuation & Equity Proceeds")

    x1, x2, x3 = st.columns(3)

    x1.metric(
        "Gross Property Exit Value",
        f"${levered_results['exit_value']:,.0f}",
    )

    x2.metric(
        "Net Sale Proceeds",
        f"${levered_results['net_sale_proceeds']:,.0f}",
    )

    x3.metric(
        "Equity Sale Proceeds",
        f"${levered_results['equity_sale_proceeds']:,.0f}",
    )

    st.caption(
        "Model assumptions: Fixed-rate amortizing debt, "
        "monthly loan payments, growing annual NOI and CapEx, "
        "terminal valuation using forward NOI and exit cap rate, "
        "and 2% selling costs. Excludes taxes, refinancing, "
        "and additional reserves."
    )


    # ========================================================
    # F. INTEREST RATE SENSITIVITY ANALYSIS
    # ========================================================

    st.divider()

    st.subheader("Interest Rate Sensitivity Analysis")

    st.caption(
        "Evaluate how changes in borrowing costs affect "
        "leveraged investment returns and debt coverage."
    )

    # Generate interest rates around the selected assumption
    rate_changes = [
        -0.03, -0.025, -0.02, -0.015, -0.01,
        -0.005, 0, 0.005, 0.01, 0.015,
        0.02, 0.025, 0.03
    ]

    sensitivity_rates = sorted(set(
        max(0.0, interest_rate + change)
        for change in rate_changes
    ))

    interest_sensitivity = []

    for scenario_rate in sensitivity_rates:

        scenario_results = calculate_levered_returns(
            acquisition_price=acquisition_price,
            year_1_noi=year_1_noi,
            noi_growth_rate=noi_growth_rate,
            exit_cap_rate=exit_cap_rate,
            ltv=ltv,
            interest_rate=scenario_rate,
            amortization_years=int(amortization_years),
            holding_period=holding_period,
            annual_capex=annual_capex,
            capex_growth_rate=capex_growth_rate,
            selling_cost_rate=0.02,
            acquisition_cost_rate=acquisition_cost_rate,
            loan_fee_rate=loan_fee_rate,
            unlevered_discount_rate=required_return,
            equity_discount_rate=equity_discount_rate,
        )

        scenario_annual = pd.DataFrame(
            scenario_results["annual_results"]
        )

        debt_years = scenario_annual[
            scenario_annual["debt_service"] > 0
        ]

        scenario_min_dscr = (
            debt_years["dscr"].min()
            if not debt_years.empty
            else None
        )

        interest_sensitivity.append({
            "Interest Rate": scenario_rate * 100,
            "Levered IRR": (
                scenario_results["levered_irr"] * 100
            ),
            "Unlevered IRR": (
                scenario_results["unlevered_irr"] * 100
            ),
            "Minimum DSCR": scenario_min_dscr,
            "Equity NPV": scenario_results["levered_npv"],
        })

    interest_df = pd.DataFrame(interest_sensitivity)

    # --------------------------------------------------------
    # CHART 1 — INTEREST RATE VS INVESTMENT IRR
    # --------------------------------------------------------

    st.subheader("Borrowing Costs vs. Investment Returns")

    irr_chart = go.Figure()

    irr_chart.add_trace(
        go.Scatter(
            x=interest_df["Interest Rate"],
            y=interest_df["Levered IRR"],
            mode="lines+markers",
            name="Levered IRR",
            line=dict(color=TEAL, width=3),
            hovertemplate=(
                "Interest Rate: %{x:.2f}%<br>"
                "Levered IRR: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    irr_chart.add_trace(
        go.Scatter(
            x=interest_df["Interest Rate"],
            y=interest_df["Unlevered IRR"],
            mode="lines",
            name="Unlevered IRR",
            line=dict(
                color=BLUE,
                width=2,
                dash="dash"
            ),
            hovertemplate=(
                "Interest Rate: %{x:.2f}%<br>"
                "Unlevered IRR: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    irr_chart.add_vline(
        x=interest_rate * 100,
        line_dash="dot",
        line_color=ORANGE,
        annotation_text="Current Rate",
        annotation_position="top right",
    )

    irr_chart.update_layout(
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font_color=TEXT,
        height=440,
        xaxis_title="Annual Interest Rate (%)",
        yaxis_title="Projected IRR (%)",
        legend=dict(
            orientation="h",
            y=-0.25,
        ),
        hovermode="x unified",
    )

    st.plotly_chart(
        irr_chart,
        width="stretch",
        theme=None,
    )

    # --------------------------------------------------------
    # CHART 2 — INTEREST RATE VS DSCR
    # --------------------------------------------------------

    st.subheader("Interest Rate vs. Debt Coverage")

    st.caption(
        "Debt Service Coverage Ratio measures the "
        "property's NOI relative to required debt payments."
    )

    dscr_chart = go.Figure()

    dscr_chart.add_trace(
        go.Scatter(
            x=interest_df["Interest Rate"],
            y=interest_df["Minimum DSCR"],
            mode="lines+markers",
            name="Minimum DSCR",
            line=dict(color=TEAL, width=3),
            hovertemplate=(
                "Interest Rate: %{x:.2f}%<br>"
                "Minimum DSCR: %{y:.2f}x"
                "<extra></extra>"
            ),
        )
    )

    # Illustrative underwriting threshold
    dscr_threshold = 1.25

    dscr_chart.add_hline(
        y=dscr_threshold,
        line_dash="dash",
        line_color=ORANGE,
        annotation_text="Illustrative 1.25x Threshold",
        annotation_position="top right",
    )

    dscr_chart.add_vline(
        x=interest_rate * 100,
        line_dash="dot",
        line_color=BLUE,
    )

    dscr_chart.update_layout(
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font_color=TEXT,
        height=400,
        xaxis_title="Annual Interest Rate (%)",
        yaxis_title="Minimum Annual DSCR (x)",
    )

    st.plotly_chart(
        dscr_chart,
        width="stretch",
        theme=None,
    )

    # --------------------------------------------------------
    # SENSITIVITY RESULTS TABLE
    # --------------------------------------------------------

    st.subheader("Interest Rate Sensitivity Table")

    st.dataframe(
        interest_df.style.format({
            "Interest Rate": "{:.2f}%",
            "Levered IRR": "{:.2f}%",
            "Unlevered IRR": "{:.2f}%",
            "Minimum DSCR": "{:.2f}x",
            "Equity NPV": "${:,.0f}",
        }, na_rep="N/A"),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download Interest Rate Sensitivity CSV",
        data=interest_df.to_csv(index=False),
        file_name=(
            f"{selected_property}_interest_sensitivity.csv"
        ),
        mime="text/csv",
    )

    # --------------------------------------------------------
    # AUTOMATIC FINANCING INSIGHT
    # --------------------------------------------------------

    st.subheader("Financing Risk Assessment")

    irr_difference = (
        levered_results["levered_irr"]
        - levered_results["unlevered_irr"]
    ) * 100

    if irr_difference > 0:
        st.success(
            f"Financing increases projected IRR by "
            f"{irr_difference:.2f} percentage points."
        )
    elif irr_difference < 0:
        st.warning(
            f"Financing decreases projected IRR by "
            f"{abs(irr_difference):.2f} percentage points."
        )
    else:
        st.info(
            "Levered and unlevered IRRs are equal "
            "under current assumptions."
        )

    if minimum_dscr is None:
        st.info(
            "No debt service is required under "
            "the selected financing assumptions."
        )
    elif minimum_dscr < dscr_threshold:
        st.warning(
            f"Minimum DSCR is {minimum_dscr:.2f}x, "
            f"below the illustrative "
            f"{dscr_threshold:.2f}x threshold."
        )
    else:
        st.success(
            f"Minimum DSCR is {minimum_dscr:.2f}x, "
            f"above the illustrative "
            f"{dscr_threshold:.2f}x threshold."
        )

    if levered_results["levered_npv"] < 0:
        st.warning(
            "Equity NPV is negative at the selected "
            "required equity return."
        )
    else:
        st.success(
            "Equity NPV is non-negative at the "
            "selected required equity return."
        )

    st.caption(
        "Sensitivity analysis assumes fixed-rate, "
        "fully amortizing financing. Each scenario "
        "models a different loan origination rate, "
        "not a floating-rate loan. The 1.25x DSCR "
        "benchmark is illustrative, not a universal "
        "lending requirement."
    )

# ============================================================
# 11. FOOTER
# ============================================================

st.divider()

st.caption(
    "REAL ESTATE INVESTMENT ANALYTICS | "
    "Python · SQL · Pandas · Streamlit · Plotly"
)

st.caption(
    "Educational project using synthetic Arizona "
    "property data. Original screening uses simplified "
    "unlevered cash flows. The DCF module incorporates "
    "CapEx, financing, loan repayments, and fees."
)
