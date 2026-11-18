"""
Real Estate Acquisition & IRR Analytics Dashboard

Interactive real estate investment underwriting platform.
Includes unlevered returns, sensitivity analysis,
debt financing, and discounted cash flow modeling.

Dataset: Synthetic Arizona Build-for-Rent properties.
"""

import sys
from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BFR Underwriting",
    page_icon=":material/home_work:",
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
# 2. DESIGN SYSTEM
# Graphite neutrals, one terracotta accent.
# The accent marks the one figure that matters on each view.
# Dashed lines are reserved for hurdles and thresholds.
# ============================================================

BG = "#141415"
CARD = "#19191b"
RAISED = "#232325"
GRID = "rgba(237, 237, 237, 0.06)"
AXIS = "rgba(237, 237, 237, 0.16)"
TEXT_1 = "#ededed"
TEXT_2 = "#a1a1a6"
TEXT_3 = "#85858b"
NEUTRAL = "#6b6b70"
NEUTRAL_DEEP = "#3f3f44"
ACCENT = "#d9774e"
ACCENT_DEEP = "#9e4f30"
POSITIVE = "#4cc38a"
NEGATIVE = "#e5484d"

SANS = "'IBM Plex Sans', system-ui, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, monospace"

SELLING_COST_RATE = 0.02
DSCR_THRESHOLD = 1.25  # Illustrative underwriting threshold

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

.stApp, .stApp *:not([data-testid="stIconMaterial"]) {
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}
.block-container {
    padding-top: 64px;
    padding-bottom: 48px;
    max-width: 1440px;
}
.stApp h1 {
    font-size: 28px !important;
    font-weight: 500 !important;
    line-height: 1.15 !important;
    letter-spacing: -0.01em;
    padding: 0 !important;
}
.stApp h3 {
    font-size: 18px !important;
    font-weight: 500 !important;
    line-height: 1.3 !important;
    padding: 16px 0 0 !important;
}
[data-testid="stSidebar"] {
    background-color: #0f0f10;
    border-right: 1px solid rgba(237, 237, 237, 0.08);
}
[data-testid="stCaptionContainer"] { color: #85858b; }
[data-baseweb="tab-list"] {
    gap: 24px;
    border-bottom: 1px solid rgba(237, 237, 237, 0.08);
}
[data-baseweb="tab"] { font-size: 14px; }
.stApp button { transition: background-color 150ms cubic-bezier(0.22, 1, 0.36, 1), border-color 150ms cubic-bezier(0.22, 1, 0.36, 1), color 150ms cubic-bezier(0.22, 1, 0.36, 1); }

.stApp .uw-meta {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 12px;
    line-height: 16px;
    color: #85858b;
    margin-top: 4px;
}

/* Verdict: the one figure that decides the deal */
.stApp .uw-verdict {
    display: grid;
    grid-template-columns: minmax(0, 4fr) minmax(0, 8fr);
    background: #19191b;
    border: 1px solid rgba(237, 237, 237, 0.08);
    border-radius: 16px;
    overflow: hidden;
    margin: 16px 0 8px;
}
.stApp .uw-verdict-main {
    padding: 24px 32px 24px 24px;
    border-right: 1px solid rgba(237, 237, 237, 0.08);
}
.stApp .uw-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    line-height: 20px;
    color: #a1a1a6;
}
.stApp .uw-dot {
    width: 8px;
    height: 8px;
    border-radius: 4px;
    flex: none;
}
.stApp .uw-figure {
    font-size: 56px;
    line-height: 1.04;
    font-weight: 500;
    letter-spacing: -0.03em;
    color: #ededed;
    font-variant-numeric: tabular-nums;
    margin-top: 12px;
}
.stApp .uw-gap {
    font-size: 14px;
    line-height: 20px;
    color: #a1a1a6;
    margin-top: 8px;
    font-variant-numeric: tabular-nums;
}
.stApp .uw-bar {
    position: relative;
    height: 8px;
    border-radius: 4px;
    background: #232325;
    margin: 32px 0 32px;
}
.stApp .uw-fill {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    border-radius: 4px;
}
.stApp .uw-hurdle {
    position: absolute;
    top: -8px;
    bottom: -8px;
    border-left: 1px dashed #a1a1a6;
}
.stApp .uw-hurdle-label {
    position: absolute;
    top: 28px;
    transform: translateX(-50%);
    white-space: nowrap;
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 12px;
    line-height: 16px;
    color: #85858b;
}

/* Fact grids: hairlines come from a 1px gap over the hairline color */
.stApp .uw-grid {
    display: grid;
    grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
    gap: 1px;
    background: rgba(237, 237, 237, 0.08);
}
.stApp .uw-card {
    border: 1px solid rgba(237, 237, 237, 0.08);
    border-radius: 14px;
    overflow: hidden;
    margin: 8px 0 8px;
}
.stApp .uw-verdict .uw-grid { height: 100%; }
.stApp .uw-fact {
    background: #19191b;
    padding: 20px 24px;
}
.stApp .uw-label {
    font-size: 13px;
    line-height: 20px;
    color: #a1a1a6;
}
.stApp .uw-value {
    font-size: 22px;
    white-space: nowrap;
    line-height: 1.1;
    font-weight: 500;
    color: #ededed;
    font-variant-numeric: tabular-nums;
    margin-top: 8px;
}
.stApp .uw-note {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 12px;
    line-height: 16px;
    color: #85858b;
    margin-top: 8px;
}

/* Financing check rows */
.stApp .uw-checks {
    background: #19191b;
    border: 1px solid rgba(237, 237, 237, 0.08);
    border-radius: 14px;
    overflow: hidden;
    margin: 8px 0;
}
.stApp .uw-check {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    font-size: 14px;
    line-height: 20px;
    color: #ededed;
    font-variant-numeric: tabular-nums;
}
.stApp .uw-check + .uw-check { border-top: 1px solid rgba(237, 237, 237, 0.08); }

@media (max-width: 960px) {
    .stApp .uw-verdict { grid-template-columns: 1fr; }
    .stApp .uw-verdict-main {
        border-right: 0;
        border-bottom: 1px solid rgba(237, 237, 237, 0.08);
    }
    .stApp .uw-figure { font-size: 44px; }
    .stApp .uw-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Formatting and rendering helpers
# ------------------------------------------------------------

def money(value):
    """Whole dollars everywhere, with a leading minus for outflows."""
    if pd.isna(value):
        return "N/A"
    return f"\u2212${abs(value):,.0f}" if value < 0 else f"${value:,.0f}"


def pp(value):
    """Signed percentage-point change with a true minus sign."""
    return f"{value:+.2f} pp".replace("-", "\u2212")


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def fact(label, value, note=None, accent=False):
    color = ACCENT if accent else TEXT_1
    note_html = (
        f'<div class="uw-note">{escape(note)}</div>' if note else ""
    )
    return (
        f'<div class="uw-fact">'
        f'<div class="uw-label">{escape(label)}</div>'
        f'<div class="uw-value" style="color:{color}">{escape(value)}</div>'
        f"{note_html}</div>"
    )


def fact_grid(cells, cols, card=True):
    grid = (
        f'<div class="uw-grid" style="--cols:{cols}">'
        f'{"".join(cells)}</div>'
    )
    return f'<div class="uw-card">{grid}</div>' if card else grid


def style_chart(fig, height, x_title=None, y_title=None):
    axis = dict(
        gridcolor=GRID,
        zerolinecolor=AXIS,
        linecolor=GRID,
        tickfont=dict(family=MONO, size=12, color=TEXT_3),
        title_font=dict(size=12, color=TEXT_3),
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family=SANS, size=13, color=TEXT_2),
        height=height,
        margin=dict(l=8, r=8, t=40, b=8),
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=dict(
            orientation="h",
            x=0,
            y=1.02,
            yanchor="bottom",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=13, color=TEXT_2),
        ),
        hoverlabel=dict(
            bgcolor=RAISED,
            bordercolor="#2e2e31",
            font=dict(family=MONO, size=12, color=TEXT_1),
        ),
    )
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    return fig


def show_chart(fig):
    st.plotly_chart(fig, width="stretch", theme=None)


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

    st.title("Underwriting")
    st.caption("Arizona build-for-rent")

    selected_property = st.selectbox(
        "Property",
        df["property_id"].tolist(),
        format_func=lambda property_id: (
            f"{df.loc[df['property_id'] == property_id, 'city'].iloc[0]}"
            f" · {property_id}"
        ),
    )

    property_data = df.loc[
        df["property_id"] == selected_property
    ].iloc[0]

    st.subheader("Assumptions")

    acquisition_price = st.number_input(
        "Acquisition price ($)",
        min_value=100_000.0,
        value=float(property_data["acquisition_price"]),
        step=50_000.0,
        format="%.0f",
    )

    noi_growth_rate = st.slider(
        "Annual NOI growth (%)",
        0.0, 8.0, 3.0, 0.5
    ) / 100

    exit_cap_rate = st.slider(
        "Exit cap rate (%)",
        5.0, 10.0, 7.5, 0.25
    ) / 100

    holding_period = st.slider(
        "Holding period (years)",
        3, 10, 5
    )

    required_return = st.slider(
        "Required return (%)",
        5.0, 20.0, 10.0, 0.5
    ) / 100

    with st.expander(
        "Debt and DCF inputs",
        expanded=False
    ):

        st.caption(
            "Financing, CapEx and closing costs"
        )

        ltv = st.slider(
            "Loan-to-value (%)",
            0, 90, 70, 5
        ) / 100

        interest_rate = st.slider(
            "Annual interest rate (%)",
            0.0, 15.0, 6.5, 0.25
        ) / 100

        amortization_years = st.number_input(
            "Amortization period (years)",
            min_value=1,
            max_value=40,
            value=30,
            step=1,
        )

        annual_capex = st.number_input(
            "Year 1 CapEx ($)",
            min_value=0.0,
            value=25_000.0,
            step=5_000.0,
            format="%.0f",
        )

        capex_growth_rate = st.slider(
            "Annual CapEx growth (%)",
            0.0, 10.0, 2.0, 0.5
        ) / 100

        acquisition_cost_rate = st.slider(
            "Acquisition closing costs (%)",
            0.0, 10.0, 1.0, 0.25
        ) / 100

        loan_fee_rate = st.slider(
            "Loan origination fees (%)",
            0.0, 5.0, 1.0, 0.25
        ) / 100

        equity_discount_rate = st.slider(
            "Required equity return (%)",
            5.0, 30.0, 12.0, 0.5
        ) / 100

    st.caption(
        "Synthetic property data, for educational use"
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

# Unlevered screening model
results = calculate_investment_returns(
    acquisition_price=acquisition_price,
    year_1_noi=year_1_noi,
    noi_growth_rate=noi_growth_rate,
    exit_cap_rate=exit_cap_rate,
    holding_period=holding_period,
    discount_rate=required_return,
)

meets_hurdle = results["irr"] >= required_return


def run_levered(rate):
    return calculate_levered_returns(
        acquisition_price=acquisition_price,
        year_1_noi=year_1_noi,
        noi_growth_rate=noi_growth_rate,
        exit_cap_rate=exit_cap_rate,
        ltv=ltv,
        interest_rate=rate,
        amortization_years=int(amortization_years),
        holding_period=holding_period,
        annual_capex=annual_capex,
        capex_growth_rate=capex_growth_rate,
        selling_cost_rate=SELLING_COST_RATE,
        acquisition_cost_rate=acquisition_cost_rate,
        loan_fee_rate=loan_fee_rate,
        unlevered_discount_rate=required_return,
        equity_discount_rate=equity_discount_rate,
    )


def min_dscr(annual_results):
    frame = pd.DataFrame(annual_results)
    debt_years = frame.loc[frame["debt_service"] > 0, "dscr"]
    return debt_years.min() if not debt_years.empty else None


# Leveraged DCF model
levered_results = run_levered(interest_rate)
annual = pd.DataFrame(levered_results["annual_results"])
minimum_dscr = min_dscr(levered_results["annual_results"])


# ============================================================
# 7. BUILD CASH FLOW DATA
# ============================================================

annual_noi = [
    year_1_noi * (1 + noi_growth_rate) ** (year - 1)
    for year in range(1, holding_period + 1)
]

cash_flow_df = pd.DataFrame({
    "Year": range(holding_period + 1),
    "Cash flow": results["cash_flows"],
})

operating_cash_flows = [0] + annual_noi

sale_cash_flows = (
    [0] * holding_period
    + [results["net_sale_proceeds"]]
)


# ============================================================
# 8. HEADER AND VERDICT
# ============================================================

st.title(f"{property_data['city']} build-for-rent")

html(
    f'<div class="uw-meta">{escape(str(selected_property))} · '
    f'{int(property_data["units"])} units · '
    f"{holding_period}-year hold · "
    f"{exit_cap_rate:.2%} exit cap</div>"
)

irr = results["irr"]
gap_pp = (irr - required_return) * 100
scale_max = max(required_return, irr, 0.01) * 1.4
fill_pct = min(max(irr, 0) / scale_max, 1) * 100
hurdle_pct = required_return / scale_max * 100
lead_color = ACCENT if meets_hurdle else NEUTRAL
gap_color = POSITIVE if gap_pp >= 0 else NEGATIVE
status_text = "clears hurdle" if meets_hurdle else "below hurdle"

verdict_facts = fact_grid(
    [
        fact(
            "NPV",
            money(results["npv"]),
            f"at {required_return:.1%} discount rate",
        ),
        fact(
            "Investment multiple",
            f"{results['investment_multiple']:.2f}x",
        ),
        fact(
            "Exit value",
            money(results["exit_value"]),
            f"at {exit_cap_rate:.2%} exit cap",
        ),
        fact("Acquisition price", money(acquisition_price)),
        fact("Year 1 NOI", money(year_1_noi)),
        fact("Going-in cap rate", f"{going_in_cap_rate:.2%}"),
    ],
    cols=3,
    card=False,
)

html(
    '<div class="uw-verdict">'
    '<div class="uw-verdict-main">'
    '<div class="uw-status">'
    f'<span class="uw-dot" style="background:{lead_color}"></span>'
    f"Unlevered IRR · {escape(status_text)}</div>"
    f'<div class="uw-figure">{irr:.2%}</div>'
    '<div class="uw-gap">'
    f'<span style="color:{gap_color}">{pp(gap_pp)}</span>'
    " vs required return</div>"
    '<div class="uw-bar">'
    f'<div class="uw-fill" style="width:{fill_pct:.1f}%;'
    f'background:{lead_color}"></div>'
    f'<div class="uw-hurdle" style="left:{hurdle_pct:.1f}%">'
    f'<span class="uw-hurdle-label">Hurdle {required_return:.1%}</span>'
    "</div></div>"
    "</div>"
    f"{verdict_facts}"
    "</div>"
)


# ============================================================
# 9. DASHBOARD NAVIGATION
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Cash flows",
    "Sensitivity",
    "Summary",
    "Debt and DCF",
])


# ============================================================
# TAB 1 — CASH FLOW ANALYSIS
# ============================================================

with tab1:

    st.subheader("Projected cash flows")

    st.caption(
        "Purchase in year 0, operating NOI each year, "
        "and net sale proceeds at exit"
    )

    cash_flow_chart = go.Figure()

    cash_flow_chart.add_bar(
        x=cash_flow_df["Year"],
        y=[-acquisition_price] + [0] * holding_period,
        name="Acquisition",
        marker_color=NEUTRAL_DEEP,
        hovertemplate="Year %{x}<br>Acquisition %{y:$,.0f}<extra></extra>",
    )

    cash_flow_chart.add_bar(
        x=cash_flow_df["Year"],
        y=operating_cash_flows,
        name="Operating NOI",
        marker_color=NEUTRAL,
        hovertemplate="Year %{x}<br>NOI %{y:$,.0f}<extra></extra>",
    )

    cash_flow_chart.add_bar(
        x=cash_flow_df["Year"],
        y=sale_cash_flows,
        name="Net sale proceeds",
        marker_color=ACCENT,
        hovertemplate="Year %{x}<br>Sale %{y:$,.0f}<extra></extra>",
    )

    style_chart(cash_flow_chart, 360, "Year", None)
    cash_flow_chart.update_layout(barmode="relative", bargap=0.4)
    cash_flow_chart.update_traces(marker_line_width=0)
    cash_flow_chart.update_xaxes(dtick=1, showgrid=False, zeroline=False)
    cash_flow_chart.update_yaxes(tickformat="$~s")

    show_chart(cash_flow_chart)

    st.subheader("Cash flow schedule")

    st.dataframe(
        cash_flow_df.style.format({"Cash flow": money}),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download cash flows (CSV)",
        data=cash_flow_df.to_csv(index=False),
        file_name=f"{selected_property}_cash_flows.csv",
        mime="text/csv",
        icon=":material/download:",
    )


# ============================================================
# TAB 2 — IRR SENSITIVITY ANALYSIS
# ============================================================

with tab2:

    st.subheader("IRR by NOI growth and exit cap rate")

    st.caption(
        f"Shaded cells clear the {required_return:.1%} required "
        "return. The dashed line is the hurdle and the outlined "
        "cell is your current case."
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
                "NOI growth": growth,
                "Exit cap rate": cap,
                "IRR": scenario["irr"],
            })

    sensitivity_df = pd.DataFrame(
        sensitivity_results
    )

    sensitivity_matrix = sensitivity_df.pivot(
        index="NOI growth",
        columns="Exit cap rate",
        values="IRR",
    )

    x_values = [cap * 100 for cap in sensitivity_matrix.columns]
    y_values = [growth * 100 for growth in sensitivity_matrix.index]
    gap_to_hurdle = (sensitivity_matrix.values - required_return) * 100

    # Cells below the hurdle stay neutral, cells above it shade
    # toward terracotta, with the break exactly at the hurdle.
    z_low = min(gap_to_hurdle.min(), -0.01)
    z_high = max(gap_to_hurdle.max(), 0.01)
    hurdle_at = -z_low / (z_high - z_low)
    hurdle_colorscale = [
        [0.0, "#161617"],
        [hurdle_at, "#2a2a2d"],
        [min(hurdle_at + 0.001, 1.0), "#5a3022"],
        [1.0, ACCENT_DEEP],
    ]

    heatmap = go.Figure()

    heatmap.add_trace(
        go.Heatmap(
            z=gap_to_hurdle,
            x=x_values,
            y=y_values,
            text=[
                [f"{value:.2%}" for value in row]
                for row in sensitivity_matrix.values
            ],
            texttemplate="%{text}",
            textfont=dict(family=MONO, size=13, color=TEXT_1),
            colorscale=hurdle_colorscale,
            zmin=z_low,
            zmax=z_high,
            xgap=2,
            ygap=2,
            showscale=False,
            hovertemplate=(
                "Exit cap %{x:.1f}%<br>"
                "NOI growth %{y:.1f}%<br>"
                "IRR %{text}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    heatmap.add_trace(
        go.Contour(
            z=gap_to_hurdle,
            x=x_values,
            y=y_values,
            autocontour=False,
            contours=dict(start=0, end=0, size=1, coloring="none"),
            line=dict(color=TEXT_1, width=1.5, dash="dash"),
            showscale=False,
            hoverinfo="skip",
            name=f"{required_return:.1%} hurdle",
            showlegend=True,
        )
    )

    if (
        growth_rates[0] <= noi_growth_rate <= growth_rates[-1]
        and exit_cap_rates[0] <= exit_cap_rate <= exit_cap_rates[-1]
    ):
        heatmap.add_shape(
            type="rect",
            x0=exit_cap_rate * 100 - 0.23,
            x1=exit_cap_rate * 100 + 0.23,
            y0=noi_growth_rate * 100 - 0.46,
            y1=noi_growth_rate * 100 + 0.46,
            line=dict(color=TEXT_1, width=1.5),
            layer="above",
        )

    style_chart(heatmap, 480, "Exit cap rate", "Annual NOI growth")
    heatmap.update_xaxes(
        tickvals=x_values,
        ticktext=[f"{cap:.1%}" for cap in sensitivity_matrix.columns],
        showgrid=False,
        zeroline=False,
    )
    heatmap.update_yaxes(
        tickvals=y_values,
        ticktext=[f"{growth:.1%}" for growth in sensitivity_matrix.index],
        showgrid=False,
        zeroline=False,
    )

    show_chart(heatmap)

    st.subheader("Sensitivity data")

    formatted_matrix = sensitivity_matrix.map(
        lambda value: f"{value:.2%}"
    )
    formatted_matrix.index = [
        f"{growth:.1%}" for growth in sensitivity_matrix.index
    ]
    formatted_matrix.columns = [
        f"{cap:.1%}" for cap in sensitivity_matrix.columns
    ]
    formatted_matrix.index.name = "NOI growth / exit cap"

    st.dataframe(
        formatted_matrix,
        width="stretch",
    )


# ============================================================
# TAB 3 — INVESTMENT DECISION SUMMARY
# ============================================================

with tab3:

    st.subheader("Decision summary")

    verdict_sentence = (
        "clears" if meets_hurdle else "falls short of"
    )

    st.write(
        f"The **{property_data['city']}** acquisition "
        f"has a projected unlevered IRR of "
        f"**{results['irr']:.2%}**, which {verdict_sentence} "
        f"the required return of **{required_return:.2%}** "
        f"by {abs(gap_pp):.2f} percentage points."
    )

    st.write(
        f"The estimated exit value is "
        f"**{money(results['exit_value'])}**, "
        f"based on an exit cap rate of "
        f"**{exit_cap_rate:.2%}**."
    )

    st.subheader("Key assumptions")

    assumptions_df = pd.DataFrame({
        "Assumption": [
            "Acquisition price",
            "Year 1 NOI",
            "Annual NOI growth",
            "Exit cap rate",
            "Holding period",
            "Required return",
            "Selling costs",
        ],
        "Value": [
            money(acquisition_price),
            money(year_1_noi),
            f"{noi_growth_rate:.2%}",
            f"{exit_cap_rate:.2%}",
            f"{holding_period} years",
            f"{required_return:.2%}",
            f"{SELLING_COST_RATE:.2%}",
        ],
    })

    st.dataframe(
        assumptions_df,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Preliminary screening result, not an "
        "investment recommendation"
    )


# ============================================================
# TAB 4 — DEBT FINANCING & DCF ANALYSIS
# ============================================================

with tab4:

    st.subheader("Returns after debt")

    st.caption(
        "Property and equity returns after financing, CapEx, "
        "closing costs and loan repayment"
    )

    # --------------------------------------------------------
    # A. FINANCING METRICS
    # --------------------------------------------------------

    levered_gap = (
        levered_results["levered_irr"] - equity_discount_rate
    ) * 100

    html(
        fact_grid(
            [
                fact(
                    "Levered IRR",
                    f"{levered_results['levered_irr']:.2%}",
                    f"{pp(levered_gap)} vs {equity_discount_rate:.1%} hurdle",
                    accent=levered_gap >= 0,
                ),
                fact(
                    "Equity multiple",
                    f"{levered_results['equity_multiple']:.2f}x",
                ),
                fact(
                    "Equity NPV",
                    money(levered_results["levered_npv"]),
                    f"at {equity_discount_rate:.1%}",
                ),
                fact(
                    "Minimum annual DSCR",
                    (
                        f"{minimum_dscr:.2f}x"
                        if minimum_dscr is not None
                        else "N/A"
                    ),
                    f"vs {DSCR_THRESHOLD:.2f}x threshold",
                ),
                fact(
                    "Loan amount",
                    money(levered_results["loan_amount"]),
                    f"{ltv:.0%} LTV at {interest_rate:.2%}",
                ),
                fact(
                    "Initial equity",
                    money(levered_results["initial_equity"]),
                ),
                fact(
                    "Unlevered IRR",
                    f"{levered_results['unlevered_irr']:.2%}",
                    "after CapEx and closing costs",
                ),
                fact(
                    "Remaining debt at exit",
                    money(levered_results["remaining_loan_balance"]),
                ),
            ],
            cols=4,
        )
    )

    # --------------------------------------------------------
    # B. LEVERED VS UNLEVERED CASH FLOWS
    # --------------------------------------------------------

    st.subheader("Unlevered vs levered cash flows")

    years = list(range(holding_period + 1))

    comparison_chart = go.Figure()

    comparison_chart.add_trace(
        go.Bar(
            name="Unlevered",
            x=years,
            y=levered_results["unlevered_cash_flows"],
            marker_color=NEUTRAL,
            hovertemplate="Year %{x}<br>Unlevered %{y:$,.0f}<extra></extra>",
        )
    )

    comparison_chart.add_trace(
        go.Bar(
            name="Levered equity",
            x=years,
            y=levered_results["levered_cash_flows"],
            marker_color=ACCENT,
            hovertemplate="Year %{x}<br>Levered %{y:$,.0f}<extra></extra>",
        )
    )

    style_chart(comparison_chart, 340, "Year", None)
    comparison_chart.update_layout(
        barmode="group", bargap=0.35, bargroupgap=0.1
    )
    comparison_chart.update_traces(marker_line_width=0)
    comparison_chart.update_xaxes(dtick=1, showgrid=False, zeroline=False)
    comparison_chart.update_yaxes(tickformat="$~s")

    show_chart(comparison_chart)

    # --------------------------------------------------------
    # C. ANNUAL DCF AND DEBT SCHEDULE
    # --------------------------------------------------------

    st.subheader("Operating cash flow and debt schedule")

    operating_table = annual.rename(
        columns={
            "year": "Year",
            "noi": "NOI",
            "capex": "CapEx",
            "interest": "Interest",
            "principal": "Principal",
            "debt_service": "Debt service",
            "dscr": "DSCR",
            "unlevered_cash_flow": "Unlevered CF",
            "levered_cash_flow": "Levered CF",
            "ending_loan_balance": "Ending loan balance",
        }
    )

    money_columns = [
        "NOI",
        "CapEx",
        "Interest",
        "Principal",
        "Debt service",
        "Unlevered CF",
        "Levered CF",
        "Ending loan balance",
    ]

    format_columns = {
        col: money
        for col in money_columns
        if col in operating_table.columns
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
        "Operating cash flows exclude sale proceeds. "
        "The schedule below adds the sale and loan payoff."
    )

    # --------------------------------------------------------
    # D. COMPLETE INVESTMENT CASH FLOWS
    # --------------------------------------------------------

    st.subheader("DCF cash flow schedule")

    investment_cash_flows = pd.DataFrame({
        "Year": years,
        "Unlevered CF":
            levered_results["unlevered_cash_flows"],
        "Levered equity CF":
            levered_results["levered_cash_flows"],
    })

    st.dataframe(
        investment_cash_flows.style.format({
            "Unlevered CF": money,
            "Levered equity CF": money,
        }),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download DCF schedule (CSV)",
        data=operating_table.to_csv(index=False),
        file_name=f"{selected_property}_debt_dcf.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    # --------------------------------------------------------
    # E. TERMINAL VALUATION
    # --------------------------------------------------------

    st.subheader("Exit valuation")

    html(
        fact_grid(
            [
                fact(
                    "Gross exit value",
                    money(levered_results["exit_value"]),
                    f"forward NOI at {exit_cap_rate:.2%} cap",
                ),
                fact(
                    "Net sale proceeds",
                    money(levered_results["net_sale_proceeds"]),
                    f"after {SELLING_COST_RATE:.0%} selling costs",
                ),
                fact(
                    "Equity sale proceeds",
                    money(levered_results["equity_sale_proceeds"]),
                    "after loan payoff",
                ),
            ],
            cols=3,
        )
    )

    st.caption(
        "Fixed-rate amortizing debt with monthly payments, "
        "growing NOI and CapEx, exit on forward NOI. "
        "Excludes taxes, refinancing and reserves."
    )

    # ========================================================
    # F. INTEREST RATE SENSITIVITY ANALYSIS
    # ========================================================

    st.subheader("Interest rate sensitivity")

    st.caption(
        "How borrowing costs move levered returns and debt coverage"
    )

    # Interest rates around the selected assumption
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

        scenario_results = run_levered(scenario_rate)

        interest_sensitivity.append({
            "Interest rate": scenario_rate * 100,
            "Levered IRR": (
                scenario_results["levered_irr"] * 100
            ),
            "Unlevered IRR": (
                scenario_results["unlevered_irr"] * 100
            ),
            "Minimum DSCR": min_dscr(
                scenario_results["annual_results"]
            ),
            "Equity NPV": scenario_results["levered_npv"],
        })

    interest_df = pd.DataFrame(interest_sensitivity)

    # --------------------------------------------------------
    # CHART 1 — INTEREST RATE VS INVESTMENT IRR
    # --------------------------------------------------------

    irr_chart = go.Figure()

    irr_chart.add_trace(
        go.Scatter(
            x=interest_df["Interest rate"],
            y=interest_df["Unlevered IRR"],
            mode="lines",
            name="Unlevered IRR",
            line=dict(color=NEUTRAL, width=2),
            hovertemplate="Unlevered %{y:.2f}%<extra></extra>",
        )
    )

    irr_chart.add_trace(
        go.Scatter(
            x=interest_df["Interest rate"],
            y=interest_df["Levered IRR"],
            mode="lines+markers",
            name="Levered IRR",
            line=dict(color=ACCENT, width=2.5),
            marker=dict(size=6),
            hovertemplate="Levered %{y:.2f}%<extra></extra>",
        )
    )

    irr_chart.add_hline(
        y=equity_discount_rate * 100,
        line_dash="dash",
        line_width=1,
        line_color=TEXT_2,
        annotation_text=f"Equity hurdle {equity_discount_rate:.1%}",
        annotation_position="bottom right",
        annotation_font=dict(family=MONO, size=12, color=TEXT_3),
    )

    irr_chart.add_vline(
        x=interest_rate * 100,
        line_dash="dot",
        line_width=1,
        line_color=TEXT_3,
        annotation_text=f"Current {interest_rate:.2%}",
        annotation_position="top right",
        annotation_font=dict(family=MONO, size=12, color=TEXT_3),
    )

    style_chart(irr_chart, 360, "Annual interest rate", "Projected IRR")
    irr_chart.update_layout(hovermode="x unified")
    irr_chart.update_xaxes(ticksuffix="%", showgrid=False, zeroline=False)
    irr_chart.update_yaxes(ticksuffix="%")

    st.markdown("**Borrowing cost vs returns**")
    show_chart(irr_chart)

    # --------------------------------------------------------
    # CHART 2 — INTEREST RATE VS DSCR
    # --------------------------------------------------------

    dscr_chart = go.Figure()

    dscr_chart.add_trace(
        go.Scatter(
            x=interest_df["Interest rate"],
            y=interest_df["Minimum DSCR"],
            mode="lines+markers",
            name="Minimum DSCR",
            line=dict(color=ACCENT, width=2.5),
            marker=dict(size=6),
            hovertemplate=(
                "Rate %{x:.2f}%<br>"
                "Minimum DSCR %{y:.2f}x"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    dscr_chart.add_hline(
        y=DSCR_THRESHOLD,
        line_dash="dash",
        line_width=1,
        line_color=TEXT_2,
        annotation_text=f"Illustrative {DSCR_THRESHOLD:.2f}x threshold",
        annotation_position="top left",
        annotation_font=dict(family=MONO, size=12, color=TEXT_3),
    )

    dscr_chart.add_vline(
        x=interest_rate * 100,
        line_dash="dot",
        line_width=1,
        line_color=TEXT_3,
        annotation_text=f"Current {interest_rate:.2%}",
        annotation_position="top right",
        annotation_font=dict(family=MONO, size=12, color=TEXT_3),
    )

    style_chart(
        dscr_chart, 300, "Annual interest rate", "Minimum annual DSCR"
    )
    dscr_chart.update_xaxes(ticksuffix="%", showgrid=False, zeroline=False)
    dscr_chart.update_yaxes(ticksuffix="x")

    st.markdown("**Borrowing cost vs debt coverage**")
    st.caption(
        "Debt service coverage is NOI divided by "
        "required debt payments"
    )
    show_chart(dscr_chart)

    # --------------------------------------------------------
    # SENSITIVITY RESULTS TABLE
    # --------------------------------------------------------

    st.subheader("Sensitivity table")

    st.dataframe(
        interest_df.style.format({
            "Interest rate": "{:.2f}%",
            "Levered IRR": "{:.2f}%",
            "Unlevered IRR": "{:.2f}%",
            "Minimum DSCR": "{:.2f}x",
            "Equity NPV": money,
        }, na_rep="N/A"),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download rate sensitivity (CSV)",
        data=interest_df.to_csv(index=False),
        file_name=(
            f"{selected_property}_interest_sensitivity.csv"
        ),
        mime="text/csv",
        icon=":material/download:",
    )

    # --------------------------------------------------------
    # FINANCING CHECK
    # --------------------------------------------------------

    st.subheader("Financing check")

    checks = []

    irr_difference = (
        levered_results["levered_irr"]
        - levered_results["unlevered_irr"]
    ) * 100

    if irr_difference > 0:
        checks.append((
            POSITIVE,
            f"Leverage adds {irr_difference:.2f} pp to IRR",
        ))
    elif irr_difference < 0:
        checks.append((
            NEGATIVE,
            f"Leverage costs {abs(irr_difference):.2f} pp of IRR",
        ))
    else:
        checks.append((
            TEXT_3,
            "Levered and unlevered IRR are equal",
        ))

    if minimum_dscr is None:
        checks.append((TEXT_3, "No debt service at these assumptions"))
    elif minimum_dscr < DSCR_THRESHOLD:
        checks.append((
            NEGATIVE,
            f"Minimum DSCR {minimum_dscr:.2f}x, below the "
            f"illustrative {DSCR_THRESHOLD:.2f}x threshold",
        ))
    else:
        checks.append((
            POSITIVE,
            f"Minimum DSCR {minimum_dscr:.2f}x, above the "
            f"illustrative {DSCR_THRESHOLD:.2f}x threshold",
        ))

    if levered_results["levered_npv"] < 0:
        checks.append((
            NEGATIVE,
            f"Equity NPV is negative at {equity_discount_rate:.1%}",
        ))
    else:
        checks.append((
            POSITIVE,
            f"Equity NPV is positive at {equity_discount_rate:.1%}",
        ))

    html(
        '<div class="uw-checks">'
        + "".join(
            '<div class="uw-check">'
            f'<span class="uw-dot" style="background:{color}"></span>'
            f"{escape(text)}</div>"
            for color, text in checks
        )
        + "</div>"
    )

    st.caption(
        "Each scenario is a different fixed rate at origination, "
        "not a floating-rate loan. The 1.25x DSCR benchmark is "
        "illustrative, not a universal lending requirement."
    )


# ============================================================
# 10. FOOTER
# ============================================================

st.caption(
    "Synthetic Arizona property data, for educational use. "
    "The screening IRR uses simplified unlevered cash flows; "
    "the Debt and DCF tab adds CapEx, financing, fees and "
    "loan repayment."
)