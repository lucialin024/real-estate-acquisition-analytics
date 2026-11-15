
# Real Estate Acquisition & IRR Analytics Platform

### Interactive Real Estate Investment Underwriting Dashboard

[**Launch Live Dashboard**](https://real-estate-irr-analytics.streamlit.app/)

**Tech Stack:** Python | SQL | Pandas | NumPy Financial | Plotly | Streamlit | SQLite

## Project Overview

An end-to-end real estate investment analytics project
that evaluates hypothetical Build-for-Rent (BFR)
acquisition opportunities across Arizona.

The platform combines property-level data processing,
financial underwriting, SQL analysis, and interactive
visualization to support investment decision-making.

Users can select properties, modify investment assumptions,
forecast multi-year cash flows, and evaluate potential
returns under different market scenarios.

## Key Features

### 1. Acquisition Screening
- Calculate acquisition price per unit
- Analyze gross rental yields and cap rates
- Filter properties using financial criteria
- Rank qualified acquisition opportunities

### 2. Financial Underwriting
- Project annual rental income and NOI
- Forecast multi-year investment cash flows
- Estimate terminal property values
- Calculate unlevered IRR, NPV, and investment multiples

### 3. Sensitivity Analysis
- Model changes in annual NOI growth
- Evaluate different exit capitalization rates
- Generate a two-variable IRR sensitivity matrix
- Compare projected returns against required returns

### 4. Interactive Dashboard
- Select investment properties
- Adjust acquisition and exit assumptions
- Visualize cash flows with Plotly
- Review investment performance metrics
- Download cash flow forecasts

### 5. SQL Analytics
- Store property data in SQLite
- Perform investment screening queries
- Calculate financial metrics using CTEs
- Generate property-level portfolio summaries

## Financial Methodology

**Annual Gross Rent**

Monthly Rent × Units × 12

**Effective Rental Income**

Annual Gross Rent × (1 − Vacancy Rate)

**Net Operating Income**

Effective Rental Income × (1 − Operating Expense Ratio)

**Going-In Cap Rate**

Annual NOI / Acquisition Price

**Terminal Property Value**

Forward NOI / Exit Cap Rate

**Investment Returns**

The platform evaluates annual unlevered cash flows
to calculate IRR, NPV, and investment multiples.

## Project Structure

- `dashboard/` — Interactive Streamlit dashboard
- `data/` — Synthetic property datasets and outputs
- `sql/` — SQL screening and financial analysis
- `src/` — Python financial modeling and data processing
- `.streamlit/` — Dashboard theme configuration
- `requirements.txt` — Python dependencies

## Run Locally

Clone the repository:

    git clone https://github.com/lucialin024/real-estate-acquisition-analytics.git

Navigate to the project:

    cd real-estate-acquisition-analytics

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

Launch the dashboard:

    python -m streamlit run dashboard/app.py

## Live Application

[Open the Interactive Investment Dashboard](https://real-estate-irr-analytics.streamlit.app/)

## Data & Model Limitations

All property records and underwriting assumptions are
synthetic and used solely for educational purposes.

The model represents simplified unlevered investment
returns and excludes debt financing, capital expenditures,
income taxes, and acquisition closing costs.

It is intended for financial analytics demonstration,
not investment recommendations.

## Skills

Financial Analytics | Python | SQL | Investment Modeling