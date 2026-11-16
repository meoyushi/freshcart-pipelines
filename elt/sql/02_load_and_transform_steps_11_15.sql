-- FRESHCART: STEPS 11–15 — LOAD, VALIDATE, CLEAN AND DEDUPLICATE
-- Run this complete script in the FRESHCART_DB context using Run All.
-- This is a reconstructed teaching dataset because the classroom FreshCart
-- notebook was not supplied. It models the assignment's stated cases.
--
-- Expected after the FIRST execution:
-- Bronze raw rows: 8
-- Silver clean rows: 6
-- Quarantine rows: 2 (ORD-1004 and ORD-1006)
-- Deduplicated orders: 4
-- INR amounts for the four surviving orders total: 7,785.00
--
-- Re-running this script intentionally appends another 8 Bronze rows,
-- matching the assignment's note that Bronze grows on each run.
-- Silver tables are rebuilt from all Bronze rows on each execution.

USE DATABASE FRESHCART_DB;
USE SCHEMA BRONZE;

-- STEP 11: Load eight raw source records into Bronze.
-- Website and mobile records intentionally use different JSON field names.
INSERT INTO BRONZE.ORDERS_RAW (SOURCE_SYSTEM, RAW_PAYLOAD)
SELECT 'WEB', PARSE_JSON('{
  "order_id":"ORD-1001",
  "customer_id":"CUST-01",
  "customer_name":"Priya",
  "order_date":"2026-08-10",
  "amount":870.00,
  "currency":"INR",
  "updated_at":"2026-08-10 10:00:00"
}')
UNION ALL
SELECT 'WEB', PARSE_JSON('{
  "order_id":"ORD-1002",
  "customer_id":"CUST-02",
  "customer_name":"Arjun",
  "order_date":"2026-08-18",
  "amount":2500.00,
  "currency":"INR",
  "updated_at":"2026-08-18 11:00:00"
}')
UNION ALL
SELECT 'WEB', PARSE_JSON('{
  "order_id":"ORD-1003",
  "customer_id":"CUST-03",
  "customer_name":"Rohan",
  "order_date":"2026-08-19",
  "currency":"INR",
  "updated_at":"2026-08-19 09:00:00"
}')
UNION ALL
SELECT 'MOBILE', PARSE_JSON('{
  "orderId":"ORD-1003",
  "customerId":"CUST-03",
  "customerName":"Rohan",
  "orderDate":"2026-08-19",
  "total":2100.00,
  "currencyCode":"INR",
  "updatedAt":"2026-08-19 12:00:00"
}')
UNION ALL
SELECT 'WEB', PARSE_JSON('{
  "order_id":"ORD-1004",
  "customer_id":"CUST-04",
  "customer_name":"Meera",
  "order_date":"2026-08-20",
  "amount":null,
  "currency":"INR",
  "updated_at":"2026-08-20 10:00:00"
}')
UNION ALL
SELECT 'WEB', PARSE_JSON('{
  "order_id":"ORD-1005",
  "customer_id":"CUST-01",
  "customer_name":"Priya",
  "order_date":"2026-08-20",
  "amount":2315.00,
  "currency":"INR",
  "updated_at":"2026-08-20 10:00:00"
}')
UNION ALL
SELECT 'MOBILE', PARSE_JSON('{
  "orderId":"ORD-1005",
  "customerId":"CUST-01",
  "customerName":"Priya",
  "orderDate":"2026-08-20",
  "total":2315.00,
  "currencyCode":"INR",
  "updatedAt":"2026-08-20 12:00:00"
}')
UNION ALL
SELECT 'MOBILE', PARSE_JSON('{
  "orderId":"ORD-1006",
  "customerId":"CUST-05",
  "customerName":"Kabir",
  "orderDate":"2026-08-21",
  "total":500.00,
  "currencyCode":"EUR",
  "updatedAt":"2026-08-21 10:00:00"
}');

-- STEP 12: Standardise website/mobile fields into common columns and assign reasons.
TRUNCATE TABLE FRESHCART_DB.SILVER.ORDERS_CHECKED;

INSERT INTO FRESHCART_DB.SILVER.ORDERS_CHECKED
    (ORDER_ID, CUSTOMER_ID, CUSTOMER_NAME, ORDER_DATE, AMOUNT,
     CURRENCY, SOURCE_SYSTEM, UPDATED_AT, REASONS)
WITH NORMALISED AS (
    SELECT
        CASE WHEN SOURCE_SYSTEM = 'WEB'
             THEN RAW_PAYLOAD:order_id::VARCHAR
             ELSE RAW_PAYLOAD:orderId::VARCHAR END AS ORDER_ID,
        CASE WHEN SOURCE_SYSTEM = 'WEB'
             THEN RAW_PAYLOAD:customer_id::VARCHAR
             ELSE RAW_PAYLOAD:customerId::VARCHAR END AS CUSTOMER_ID,
        CASE WHEN SOURCE_SYSTEM = 'WEB'
             THEN RAW_PAYLOAD:customer_name::VARCHAR
             ELSE RAW_PAYLOAD:customerName::VARCHAR END AS CUSTOMER_NAME,
        TRY_TO_DATE(CASE WHEN SOURCE_SYSTEM = 'WEB'
             THEN RAW_PAYLOAD:order_date::VARCHAR
             ELSE RAW_PAYLOAD:orderDate::VARCHAR END) AS ORDER_DATE,
        TRY_TO_DECIMAL(CASE WHEN SOURCE_SYSTEM = 'WEB'
             THEN RAW_PAYLOAD:amount::VARCHAR
             ELSE RAW_PAYLOAD:total::VARCHAR END, 12, 2) AS AMOUNT,
        CASE WHEN SOURCE_SYSTEM = 'WEB'
             THEN RAW_PAYLOAD:currency::VARCHAR
             ELSE RAW_PAYLOAD:currencyCode::VARCHAR END AS CURRENCY,
        SOURCE_SYSTEM,
        TRY_TO_TIMESTAMP_NTZ(CASE WHEN SOURCE_SYSTEM = 'WEB'
             THEN RAW_PAYLOAD:updated_at::VARCHAR
             ELSE RAW_PAYLOAD:updatedAt::VARCHAR END) AS UPDATED_AT
    FROM FRESHCART_DB.BRONZE.ORDERS_RAW
)
SELECT
    ORDER_ID, CUSTOMER_ID, CUSTOMER_NAME, ORDER_DATE, AMOUNT,
    CURRENCY, SOURCE_SYSTEM, UPDATED_AT,
    ARRAY_CONSTRUCT_COMPACT(
        IFF(ORDER_ID IS NULL, 'missing_order_id', NULL),
        IFF(ORDER_DATE IS NULL, 'invalid_order_date', NULL),
        IFF(AMOUNT IS NULL OR AMOUNT <= 0, 'invalid_amount', NULL),
        IFF(CURRENCY NOT IN ('INR', 'USD') OR CURRENCY IS NULL,
            'unsupported_currency', NULL)
    ) AS REASONS
FROM NORMALISED;

-- STEP 13: Split valid rows into ORDERS_CLEAN and invalid rows into quarantine.
TRUNCATE TABLE FRESHCART_DB.SILVER.ORDERS_CLEAN;
TRUNCATE TABLE FRESHCART_DB.SILVER.ORDERS_QUARANTINE;

INSERT INTO FRESHCART_DB.SILVER.ORDERS_CLEAN
    (ORDER_ID, CUSTOMER_ID, CUSTOMER_NAME, ORDER_DATE, AMOUNT,
     CURRENCY, SOURCE_SYSTEM, UPDATED_AT)
SELECT ORDER_ID, CUSTOMER_ID, CUSTOMER_NAME, ORDER_DATE, AMOUNT,
       CURRENCY, SOURCE_SYSTEM, UPDATED_AT
FROM FRESHCART_DB.SILVER.ORDERS_CHECKED
WHERE ARRAY_SIZE(REASONS) = 0;

INSERT INTO FRESHCART_DB.SILVER.ORDERS_QUARANTINE
    (ORDER_ID, CUSTOMER_ID, CUSTOMER_NAME, ORDER_DATE, AMOUNT,
     CURRENCY, SOURCE_SYSTEM, UPDATED_AT, REASONS)
SELECT ORDER_ID, CUSTOMER_ID, CUSTOMER_NAME, ORDER_DATE, AMOUNT,
       CURRENCY, SOURCE_SYSTEM, UPDATED_AT, REASONS
FROM FRESHCART_DB.SILVER.ORDERS_CHECKED
WHERE ARRAY_SIZE(REASONS) > 0;

-- STEP 14: Deduplicate by order ID, keeping the most recently updated record.
TRUNCATE TABLE FRESHCART_DB.SILVER.ORDERS_DEDUP;

INSERT INTO FRESHCART_DB.SILVER.ORDERS_DEDUP
    (ORDER_ID, CUSTOMER_ID, CUSTOMER_NAME, ORDER_DATE, AMOUNT,
     CURRENCY, AMOUNT_INR, SOURCE_SYSTEM, UPDATED_AT)
SELECT
    ORDER_ID,
    CUSTOMER_ID,
    CUSTOMER_NAME,
    ORDER_DATE,
    AMOUNT,
    CURRENCY,
    CASE
        WHEN CURRENCY = 'INR' THEN AMOUNT
        WHEN CURRENCY = 'USD' THEN AMOUNT * 83
        ELSE NULL
    END AS AMOUNT_INR,
    SOURCE_SYSTEM,
    UPDATED_AT
FROM FRESHCART_DB.SILVER.ORDERS_CLEAN
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY ORDER_ID
    ORDER BY UPDATED_AT DESC
) = 1;

-- STEP 15: Verification queries. Review all result sets.
SELECT COUNT(*) AS BRONZE_RAW_ROWS
FROM FRESHCART_DB.BRONZE.ORDERS_RAW;

SELECT COUNT(*) AS SILVER_CHECKED_ROWS
FROM FRESHCART_DB.SILVER.ORDERS_CHECKED;

SELECT COUNT(*) AS SILVER_CLEAN_ROWS
FROM FRESHCART_DB.SILVER.ORDERS_CLEAN;

SELECT ORDER_ID, REASONS
FROM FRESHCART_DB.SILVER.ORDERS_QUARANTINE
ORDER BY ORDER_ID;

SELECT COUNT(*) AS DEDUPLICATED_ORDERS,
       SUM(AMOUNT_INR) AS TOTAL_REVENUE_INR
FROM FRESHCART_DB.SILVER.ORDERS_DEDUP;

SELECT ORDER_ID, CUSTOMER_ID, AMOUNT, CURRENCY, AMOUNT_INR, UPDATED_AT
FROM FRESHCART_DB.SILVER.ORDERS_DEDUP
ORDER BY ORDER_ID;
