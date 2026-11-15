
"""
Real Estate Acquisition & IRR Analytics Dashboard
-------------------------------------------------
Interactive investment underwriting platform using
Streamlit, Pandas, Plotly, and NumPy Financial.

Dataset: Synthetic Arizona Build-for-Rent properties
Model: Simplified unlevered real estate acquisition

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
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from financial_model import calculate_investment_returns


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
    """Load the synthetic acquisition dataset."""
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

    # Select property
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

    # Acquisition price
    acquisition_price = st.number_input(
        "Acquisition Price ($)",
        min_value=100_000.0,
        value=float(property_data["acquisition_price"]),
        step=50_000.0,
        format="%.0f",
    )

    # NOI growth
    noi_growth_rate = st.slider(
        "Annual NOI Growth (%)",
        min_value=0.0,
        max_value=8.0,
        value=3.0,
        step=0.5,
    ) / 100

    # Exit cap rate
    exit_cap_rate = st.slider(
        "Exit Cap Rate (%)",
        min_value=5.0,
        max_value=10.0,
        value=7.5,
        step=0.25,
    ) / 100

    # Holding period
    holding_period = st.slider(
        "Holding Period (Years)",
        min_value=3,
        max_value=10,
        value=5,
    )

    # Required return
    required_return = st.slider(
        "Required Return (%)",
        min_value=5.0,
        max_value=20.0,
        value=10.0,
        step=0.5,
    ) / 100

    st.divider()

    st.caption(
        "Educational model using synthetic property data."
    )


# ============================================================
# 5. PROPERTY FINANCIAL CALCULATIONS
# ============================================================

# Annual gross rental income
annual_gross_rent = (
    property_data["monthly_rent"]
    * property_data["units"]
    * 12
)

# Effective rental income after vacancy
effective_rental_income = (
    annual_gross_rent
    * (1 - property_data["vacancy_rate"])
)

# Annual Net Operating Income
year_1_noi = (
    effective_rental_income
    * (1 - property_data["operating_expense_ratio"])
)

# Going-in capitalization rate
going_in_cap_rate = year_1_noi / acquisition_price


# ============================================================
# 6. INVESTMENT RETURN CALCULATIONS
# ============================================================

results = calculate_investment_returns(
    acquisition_price=acquisition_price,
    year_1_noi=year_1_noi,
    noi_growth_rate=noi_growth_rate,
    exit_cap_rate=exit_cap_rate,
    holding_period=holding_period,
    discount_rate=required_return,
)

meets_hurdle = results["irr"] >= required_return


# ============================================================
# 7. BUILD CASH FLOW DATA
# ============================================================

# Annual operating cash flows
annual_noi = [
    year_1_noi * (1 + noi_growth_rate) ** (year - 1)
    for year in range(1, holding_period + 1)
]

# Cash flow schedule including initial investment
cash_flow_df = pd.DataFrame({
    "Year": range(holding_period + 1),
    "Cash Flow": results["cash_flows"],
})

# Components used in stacked cash flow chart
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
        f"Property ID: {selected_property}  |  "
        f"{int(property_data['units'])} Rental Units  |  "
        f"{holding_period}-Year Holding Period"
    )

with header_right:

    if meets_hurdle:
        st.success("Meets Return Hurdle")
    else:
        st.warning("Below Return Hurdle")


# ============================================================
# 9. INVESTMENT PERFORMANCE METRICS
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

tab1, tab2, tab3 = st.tabs([
    "Cash Flow Analysis",
    "Sensitivity Analysis",
    "Investment Summary",
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

    # Create cash flow chart
    cash_flow_chart = go.Figure()

    # Operating NOI
    cash_flow_chart.add_bar(
        x=cash_flow_df["Year"],
        y=operating_cash_flows,
        name="Operating NOI",
        marker_color=TEAL,
    )

    # Net sale proceeds
    cash_flow_chart.add_bar(
        x=cash_flow_df["Year"],
        y=sale_cash_flows,
        name="Net Sale Proceeds",
        marker_color=BLUE,
    )

    # Initial acquisition outflow
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
        margin=dict(
            l=10, r=10, t=20, b=20
        ),
    )

    cash_flow_chart.update_xaxes(dtick=1)

    st.plotly_chart(
        cash_flow_chart,
        width="stretch",
        theme=None,
    )

    # Cash flow table
    st.subheader("Investment Cash Flow Schedule")

    st.dataframe(
        cash_flow_df.style.format({
            "Cash Flow": "${:,.2f}"
        }),
        width="stretch",
        hide_index=True,
    )

    # Export forecast
    st.download_button(
        label="Download Cash Flow CSV",
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
        "Evaluate how annual NOI growth rates and "
        "exit capitalization rates impact projected IRR."
    )

    # Sensitivity assumptions
    growth_rates = [
        0.01, 0.02, 0.03, 0.04, 0.05
    ]

    exit_cap_rates = [
        0.065, 0.070, 0.075, 0.080, 0.085
    ]

    sensitivity_results = []

    # Calculate IRR under each scenario
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

    # Build sensitivity DataFrame
    sensitivity_df = pd.DataFrame(
        sensitivity_results
    )

    # Pivot into a matrix
    sensitivity_matrix = sensitivity_df.pivot(
        index="NOI Growth",
        columns="Exit Cap Rate",
        values="IRR",
    )

    # Create interactive heatmap
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
                [1.0, "#36C4A0"],
            ],
            showscale=False,
            hovertemplate=(
                "Exit Cap Rate: %{x}<br>"
                "NOI Growth: %{y}<br>"
                "IRR: %{text}<extra></extra>"
            ),
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
        margin=dict(
            l=10, r=10, t=20, b=20
        ),
    )

    st.plotly_chart(
        heatmap,
        width="stretch",
        theme=None,
    )

    # Show sensitivity results
    st.subheader("Sensitivity Data")

    formatted_matrix = sensitivity_matrix.map(
        lambda value: f"{value:.2%}"
    )

    st.dataframe(
        formatted_matrix,
        width="stretch",
    )

    st.caption(
        "Results are based on hypothetical assumptions "
        "and simplified unlevered cash flows."
    )


# ============================================================
# TAB 3 — INVESTMENT DECISION SUMMARY
# ============================================================

with tab3:

    st.subheader("Investment Decision Summary")

    # Investment screening conclusion
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

    # Investment summary
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

    # Underwriting assumptions table
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
        "This is a preliminary financial screening "
        "result, not an investment recommendation. "
        "A complete underwriting analysis and "
        "additional due diligence are required."
    )


# ============================================================
# 11. FOOTER & MODEL DISCLOSURE
# ============================================================

st.divider()

st.caption(
    "REAL ESTATE INVESTMENT ANALYTICS  |  "
    "Python · SQL · Pandas · Streamlit · Plotly"
)

st.caption(
    "Educational project using synthetic Arizona "
    "property data. Investment returns are unlevered "
    "and exclude debt financing, capital expenditures, "
    "income taxes, and acquisition closing costs."
)