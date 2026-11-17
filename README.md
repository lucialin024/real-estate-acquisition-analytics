
# Real Estate Acquisition & Investment Analytics Platform

### Interactive Real Estate Underwriting, DCF & Debt Financing Dashboard

An end-to-end financial analytics platform built with Python,
SQL, and Streamlit to evaluate hypothetical Build-for-Rent (BFR)
real estate acquisitions.

The platform integrates property-level financial analysis,
SQL-based acquisition screening, discounted cash flow (DCF)
modeling, debt financing, and sensitivity analysis to support
data-driven investment decisions.

**Tech Stack:** Python | SQL | SQLite | Pandas | NumPy Financial | Plotly | Streamlit

**[Launch Live Dashboard](https://real-estate-irr-analytics.streamlit.app/)** |
**[View Source Code](https://github.com/lucialin024/real-estate-acquisition-analytics)**

---

## Dashboard Preview

![Real Estate Investment Dashboard](assets/dashboard_overview.png)

The interactive dashboard allows users to select an acquisition,
adjust underwriting and financing assumptions, evaluate projected
returns, and assess investment risk.

---

## Project Overview

This project simulates real estate acquisition underwriting
using synthetic property-level data from five hypothetical
Build-for-Rent investment opportunities across Arizona.

It combines financial modeling, SQL analysis, and interactive
visualization to evaluate investment profitability, financing
structure, and downside risk.

### Business Questions

- Which properties meet predefined acquisition criteria?
- What are the projected IRR, NPV, and investment multiples?
- How do operating assumptions affect property valuations?
- How does debt financing influence equity returns?
- Can projected NOI adequately cover debt obligations?
- How do changes in interest rates affect levered IRR and DSCR?
- When does leverage improve or reduce investment returns?

---

## Key Features

### 1. Acquisition Screening & SQL Analytics

- Analyze property-level rental and financial data
- Calculate acquisition price per unit and capitalization rates
- Screen acquisitions using predefined financial criteria
- Use SQL queries and Common Table Expressions (CTEs)
- Generate property-level and portfolio-level summaries

### 2. Real Estate Financial Underwriting

- Calculate gross and effective rental income
- Estimate annual Net Operating Income (NOI)
- Forecast multi-year property cash flows
- Estimate terminal property value using exit capitalization rates
- Calculate unlevered IRR, NPV, and investment multiples
- Compare projected returns against required return thresholds

### 3. Debt Financing & DCF Analysis

Developed a modular Python-based debt financing and discounted
cash flow model to evaluate acquisition returns under different
capital structures.

Features include:

- Loan-to-value (LTV) financing assumptions
- Fixed-rate mortgage amortization schedules
- Annual interest and principal repayment calculations
- Capital expenditure (CapEx) forecasting
- Acquisition closing costs and loan origination fees
- Levered and unlevered cash flow projections
- Equity IRR and NPV calculations
- Equity multiple and remaining loan balance
- Debt Service Coverage Ratio (DSCR)
- Terminal property valuation and equity sale proceeds

The model separates property-level investment performance
from equity-level returns after financing.

### 4. Interest Rate Sensitivity & Financing Risk

- Simulate borrowing rates around selected assumptions
- Compare levered versus unlevered IRR
- Analyze the relationship between interest rates and DSCR
- Assess financing risk using an illustrative 1.25x DSCR threshold
- Evaluate equity NPV against the required equity return
- Generate automated financing risk assessments
- Export sensitivity analysis results to CSV

### 5. Interactive Investment Dashboard

Built using Streamlit and Plotly with four main modules:

1. Cash Flow Analysis
2. Sensitivity Analysis
3. Investment Summary
4. Debt Financing & DCF

Users can adjust acquisition and financing assumptions,
view interactive charts, and download financial schedules.

---

## Financial Modeling Methodology

### Property Operating Performance

**Annual Gross Rental Income**

    Monthly Rent × Number of Units × 12

**Effective Rental Income**

    Annual Gross Rent × (1 - Vacancy Rate)

**Net Operating Income (NOI)**

    Effective Rental Income × (1 - Operating Expense Ratio)

**Going-In Capitalization Rate**

    Year 1 NOI / Acquisition Price

### Discounted Cash Flow Analysis

**Unlevered Operating Cash Flow**

    NOI - Capital Expenditures

**Terminal Property Value**

    Forward NOI / Exit Capitalization Rate

**Net Sale Proceeds**

    Terminal Property Value × (1 - Selling Cost Rate)

**Net Present Value (NPV)**

    NPV = Sum[CF_t / (1 + r)^t]

The model forecasts annual property cash flows and estimates
terminal property value using the following year's NOI.

Unlevered cash flows include the initial acquisition investment,
annual operating cash flow after CapEx, and net sale proceeds.

### Debt Financing Model

**Initial Loan Amount**

    Acquisition Price × LTV

**Initial Equity Investment**

    Acquisition Price - Loan Amount
    + Acquisition Closing Costs
    + Loan Origination Fees

**Annual Debt Service**

    Interest Payments + Principal Repayments

**Annual Levered Operating Cash Flow**

    NOI - CapEx - Debt Service

**Equity Sale Proceeds**

    Net Sale Proceeds - Outstanding Loan Balance

**Debt Service Coverage Ratio (DSCR)**

    NOI / Annual Debt Service

The model uses monthly amortization calculations and
aggregates debt payments into annual financial schedules.

### Investment Return Metrics

**Unlevered IRR**

Measures investment returns before financing.

**Levered IRR**

Measures projected equity returns after debt financing.

**Equity Multiple**

    Total Positive Equity Cash Flows /
    Total Equity Contributions

**Equity NPV**

Discounts projected equity cash flows using the selected
required equity return.

The dashboard allows users to compare property-level
performance with equity-level investment returns.

---

## Investment Analysis Examples

### Acquisition Screening

The initial screening model evaluates hypothetical properties
using the following criteria:

| Investment Criteria | Requirement |
|--------------------|-------------|
| Minimum Cap Rate | 8.0% |
| Maximum Acquisition Price | $7,000,000 |
| Maximum Vacancy Rate | 6.0% |

Two of the five hypothetical properties satisfy these
screening requirements.

| Property | Acquisition Price | Annual NOI | Cap Rate |
|----------|------------------:|-----------:|---------:|
| Chandler | $6,500,000 | $530,842 | 8.17% |
| Phoenix | $6,800,000 | $555,484 | 8.17% |

The combined acquisition value of these qualifying
properties is $13.3 million.

These results demonstrate preliminary acquisition screening,
rather than a final investment recommendation.

### Leveraged Investment Analysis

In one illustrative acquisition scenario, the model produced:

| Financial Metric | Projected Result |
|------------------|-----------------:|
| Unlevered IRR | 10.18% |
| Levered IRR | 9.71% |
| Equity Multiple | 1.54x |
| Equity NPV | -$233,414 |
| Minimum DSCR | 1.73x |

### Key Investment Insights

**1. Leverage does not always improve returns.**

In this scenario, projected levered IRR is lower than
unlevered IRR, indicating that financing reduces the
expected percentage return on invested equity.

**2. Debt coverage and investment profitability are different.**

The property generates sufficient projected NOI to cover
annual debt service, but equity NPV remains negative at
the selected required equity return.

**3. Financing assumptions materially affect equity returns.**

The interest rate sensitivity model demonstrates how
higher borrowing costs can reduce levered IRR and DSCR.

**4. Investment decisions require multiple financial metrics.**

IRR alone does not capture debt coverage, capital
requirements, financing risks, or investor return hurdles.

All figures are illustrative and depend on the selected
underwriting assumptions.

---

## Project Structure

```text
real-estate-acquisition-analytics/
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   └── dashboard_overview.png
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── properties.csv
│   ├── qualified_acquisitions.csv
│   ├── tempe_cash_flow_forecast.csv
│   ├── exit_cap_sensitivity.csv
│   └── two_variable_sensitivity.csv
│
├── sql/
│   └── 01_property_analysis.sql
│
├── src/
│   ├── 01_explore_properties.py
│   ├── 02_create_database.py
│   ├── 03_run_sql.py
│   ├── 04_cash_flow_forecast.py
│   ├── 05_sensitivity_analysis.py
│   ├── 06_two_variable_sensitivity.py
│   ├── 07_test_financial_model.py
│   ├── financial_model.py
│   └── debt_model.py
│
├── test_financing.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/lucialin024/real-estate-acquisition-analytics.git
cd real-estate-acquisition-analytics
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Test the Financing Model

```bash
python test_financing.py
```

### 5. Launch the Dashboard

```bash
python -m streamlit run dashboard/app.py
```

Open the local URL displayed in your terminal.

---

## Technologies & Skills Demonstrated

| Category | Technologies / Skills |
|----------|----------------------|
| Programming | Python, SQL |
| Data Analysis | Pandas, financial data analysis |
| Database | SQLite, SQL queries, CTEs |
| Financial Modeling | DCF, IRR, NPV, NOI, cap rates |
| Debt Financing | LTV, amortization, DSCR, equity returns |
| Risk Analytics | Sensitivity analysis, scenario evaluation |
| Visualization | Streamlit, Plotly, interactive charts |
| Development | Git, GitHub, modular Python functions |

---

## Model Assumptions & Limitations

This project uses synthetic Arizona real estate data
created for educational and portfolio demonstration purposes.

The financial model:

- Assumes annual NOI growth based on user inputs
- Uses forward NOI and exit cap rate for terminal valuation
- Models fixed-rate, fully amortizing debt
- Calculates monthly debt payments and annual summaries
- Includes capital expenditures and selected transaction fees
- Assumes debt repayment upon property sale
- Excludes income taxes, refinancing, and additional reserves
- Does not independently forecast local real estate markets
- Uses simplified assumptions rather than property-specific
  lease-level underwriting

The original acquisition screening module uses NOI as
a simplified proxy for annual unlevered operating cash flow.

The expanded DCF module deducts capital expenditures
and relevant transaction costs, which can produce different
return metrics from the screening module.

The 1.25x DSCR threshold is illustrative rather than
a universal lending requirement.

Results are hypothetical and do not constitute
investment recommendations.

No confidential employer information is included.

---

## Live Application

**[Launch the Real Estate Investment Analytics Dashboard](https://real-estate-irr-analytics.streamlit.app/)**

---

## Author

**Lucia Lin**

Financial Analytics | Python | SQL | DCF Modeling | Investment Analytics

[GitHub Profile](https://github.com/lucialin024)