
-- ============================================================
-- REAL ESTATE ACQUISITION & INVESTMENT ANALYTICS
-- ============================================================
-- Project: Real Estate Acquisition Analytics Platform
-- Dataset: Synthetic Build-for-Rent (BFR) Properties
-- Database: SQLite
--
-- Purpose:
--   1. Explore property-level acquisition data
--   2. Analyze property prices and rental income
--   3. Calculate Net Operating Income (NOI)
--   4. Calculate capitalization rates
--   5. Screen and rank acquisition opportunities
--   6. Generate investment portfolio summaries
--
-- All financial data is hypothetical.
-- ============================================================


-- ============================================================
-- 1. PROPERTY DATA OVERVIEW
-- ============================================================

SELECT
    property_id,
    city,
    units,
    acquisition_price,
    monthly_rent,
    vacancy_rate,
    operating_expense_ratio
FROM properties
ORDER BY acquisition_price ASC;


-- ============================================================
-- 2. BASIC ACQUISITION SCREENING
-- ============================================================
-- Criteria:
--   Minimum units: 25
--   Maximum acquisition price: $7,000,000

SELECT
    property_id,
    city,
    units,
    acquisition_price
FROM properties
WHERE units >= 25
  AND acquisition_price <= 7000000
ORDER BY acquisition_price ASC;


-- ============================================================
-- 3. INVESTMENT PORTFOLIO SUMMARY
-- ============================================================
-- Summary of properties meeting basic screening criteria

SELECT
    COUNT(*) AS total_deals,
    SUM(acquisition_price) AS total_acquisition_value,
    ROUND(AVG(acquisition_price), 2)
        AS avg_acquisition_price,
    SUM(units) AS total_units
FROM properties
WHERE units >= 25
  AND acquisition_price <= 7000000;


-- ============================================================
-- 4. CITY-LEVEL ACQUISITION ANALYSIS
-- ============================================================
-- Compare investment opportunities by city

SELECT
    city,
    COUNT(*) AS property_count,
    SUM(units) AS total_units,
    ROUND(AVG(acquisition_price), 2)
        AS avg_acquisition_price,
    ROUND(
        SUM(acquisition_price) * 1.0
        / NULLIF(SUM(units), 0),
        2
    ) AS avg_price_per_unit
FROM properties
GROUP BY city
ORDER BY avg_acquisition_price DESC;


-- ============================================================
-- 5. ANNUAL GROSS RENTAL INCOME
-- ============================================================
-- Annual Gross Rent = Monthly Rent * Units * 12

SELECT
    property_id,
    city,
    units,
    monthly_rent,
    monthly_rent * units * 12
        AS annual_gross_rent
FROM properties
ORDER BY annual_gross_rent DESC;


-- ============================================================
-- 6. NET OPERATING INCOME (NOI)
-- ============================================================
-- Effective Rent = Annual Gross Rent * (1 - Vacancy Rate)
-- NOI = Effective Rent * (1 - Operating Expense Ratio)

WITH rental_income AS (
    SELECT
        property_id,
        city,
        monthly_rent * units * 12
            AS annual_gross_rent,
        vacancy_rate,
        operating_expense_ratio
    FROM properties
),
effective_income AS (
    SELECT
        property_id,
        city,
        annual_gross_rent * (1 - vacancy_rate)
            AS effective_rental_income,
        operating_expense_ratio
    FROM rental_income
)
SELECT
    property_id,
    city,
    ROUND(effective_rental_income, 2)
        AS effective_rental_income,
    ROUND(
        effective_rental_income
        * operating_expense_ratio,
        2
    ) AS operating_expenses,
    ROUND(
        effective_rental_income
        * (1 - operating_expense_ratio),
        2
    ) AS noi
FROM effective_income
ORDER BY noi DESC;


-- ============================================================
-- 7. PROPERTY CAP RATE ANALYSIS
-- ============================================================
-- Cap Rate = NOI / Acquisition Price
-- Cap rates are stored as decimals.

WITH rental_income AS (
    SELECT
        property_id,
        city,
        acquisition_price,
        monthly_rent * units * 12
            AS annual_gross_rent,
        vacancy_rate,
        operating_expense_ratio
    FROM properties
),
effective_income AS (
    SELECT
        property_id,
        city,
        acquisition_price,
        annual_gross_rent * (1 - vacancy_rate)
            AS effective_rental_income,
        operating_expense_ratio
    FROM rental_income
),
property_noi AS (
    SELECT
        property_id,
        city,
        acquisition_price,
        effective_rental_income
        * (1 - operating_expense_ratio) AS noi
    FROM effective_income
)
SELECT
    property_id,
    city,
    ROUND(noi, 2) AS noi,
    ROUND(
        noi * 1.0 / NULLIF(acquisition_price, 0),
        6
    ) AS cap_rate
FROM property_noi
ORDER BY cap_rate DESC;


-- ============================================================
-- 8. QUALIFIED ACQUISITION OPPORTUNITIES
-- ============================================================
-- Investment Criteria:
--   Minimum cap rate: 8%
--   Maximum acquisition price: $7,000,000
--   Maximum vacancy rate: 6%

WITH property_metrics AS (
    SELECT
        property_id,
        city,
        units,
        acquisition_price,
        vacancy_rate,
        monthly_rent * units * 12
        * (1 - vacancy_rate)
        * (1 - operating_expense_ratio) AS noi
    FROM properties
),
investment_returns AS (
    SELECT
        property_id,
        city,
        units,
        acquisition_price,
        vacancy_rate,
        noi,
        noi * 1.0 / NULLIF(acquisition_price, 0)
            AS cap_rate
    FROM property_metrics
)
SELECT
    property_id,
    city,
    units,
    acquisition_price,
    ROUND(noi, 2) AS noi,
    ROUND(cap_rate * 100, 2) AS cap_rate_pct
FROM investment_returns
WHERE cap_rate >= 0.08
  AND acquisition_price <= 7000000
  AND vacancy_rate <= 0.06
ORDER BY cap_rate DESC;


-- ============================================================
-- 9. QUALIFIED INVESTMENT PORTFOLIO SUMMARY
-- ============================================================
-- Summarize properties meeting all investment criteria

WITH investment_returns AS (
    SELECT
        property_id,
        city,
        acquisition_price,
        vacancy_rate,
        monthly_rent * units * 12
        * (1 - vacancy_rate)
        * (1 - operating_expense_ratio)
        / NULLIF(acquisition_price, 0)
            AS cap_rate
    FROM properties
),
qualified_deals AS (
    SELECT
        property_id,
        acquisition_price,
        cap_rate
    FROM investment_returns
    WHERE cap_rate >= 0.08
      AND acquisition_price <= 7000000
      AND vacancy_rate <= 0.06
)
SELECT
    COUNT(*) AS total_qualified_deals,
    SUM(acquisition_price) AS total_investment,
    ROUND(AVG(cap_rate) * 100, 2)
        AS avg_cap_rate_pct
FROM qualified_deals;