# Cleaning Log — International Sales Data

**File:** `data/sales_data_messy.csv`  
**Cleaned output:** `outputs/sales_data_clean.csv`  
**Tool:** Python 3 · pandas · numpy · re  
**Notebook:** `notebooks/ch3_sales_data_cleaning.ipynb`

---

## Dataset Overview

| Property | Value |
|----------|-------|
| Rows | 50 |
| Columns | 19 |
| Countries | 9 |
| Order date range | 2024-01-15 to 2024-02-09 |
| Unique products | 50 specialty food items |

---

## Task 1: Date Format Uniformity

**Column:** `order_date`  
**Problem:** 5 different date formats mixed in a single string column

| Format | Example | Origin |
|--------|---------|--------|
| `YYYY-MM-DD` | `2024-01-15` | ISO standard |
| `DD/MM/YYYY` | `15/01/2024` | European / UK |
| `MM/DD/YYYY` | `01/17/2024` | American |
| `DD-MM-YYYY` | `18-01-2024` | European variant |
| `MM-DD-YYYY` | `01-20-2024` | American variant |

**Rows affected:** All 50 (entire column parsed and standardised)  
**Fix:** `pd.to_datetime(df['order_date'], format='mixed', dayfirst=True)`  
**Result dtype:** `datetime64[ns]`  
**Date range after:** `2024-01-15` → `2024-02-09`

> **Ambiguous date handling:** When day and month are both ≤ 12 (e.g. `01/02/2024`), `dayfirst=True` treats the first number as day (European convention). For rows like `ORD034` where `country = Germany`, this is correct. Rows from USA with ambiguous dates carry minor uncertainty, but are a small proportion of the dataset.

---

## Task 2: Weight Unit Standardisation

**Columns:** `weight`, `weight_unit`  
**Problem:** 12 rows stored weight in `lbs` instead of `kg`

**Rows converted (lbs → kg):**

| order_id | Original weight | Unit | Converted weight (kg) |
|----------|----------------|------|----------------------|
| ORD003 | 3.2 | lbs | 1.451 |
| ORD007 | 2.0 | lbs | 0.907 |
| ORD010 | 1.8 | lbs | 0.816 |
| ORD014 | 3.6 | lbs | 1.633 |
| ORD019 | 1.1 | lbs | 0.499 |
| ORD021 | 4.8 | lbs | 2.177 |
| ORD028 | 2.5 | lbs | 1.134 |
| ORD033 | 4.2 | lbs | 1.905 |
| ORD037 | 2.8 | lbs | 1.270 |
| ORD039 | 0.9 | lbs | 0.408 |
| ORD042 | 1.8 | lbs | 0.816 |
| ORD045 | *(varies)* | lbs | *(converted)* |

**Conversion factor:** `× 0.453592`  
**Method:** Boolean mask with `.loc[]` — only lbs rows modified  
**Result:** All 50 rows now `kg`

---

## Task 3: Distance Unit Standardisation

**Columns:** `shipping_distance`, `distance_unit`  
**Problem:** 12 rows stored distance in `miles` instead of `km`  
**Additional fix:** Column cast to `float` before conversion to avoid integer dtype warning

**Conversion factor:** `× 1.60934`  
**Method:** Boolean mask with `.loc[]`  
**Result:** All 50 rows now `km`

> **Note:** ORD001 (USA, New York) had 150 miles → 241.4 km. ORD004 (UK, London) had 95 miles → 152.9 km. These were US/UK domestic shipments correctly recorded in miles before standardisation.

---

## Task 4: Temperature Unit Standardisation

**Columns:** `temperature_required`, `temp_unit`  
**Problem:** Column contains both numeric temperatures and the text value `'Room Temp'`. 11 rows used Fahrenheit.

**Two-step approach:**

**Step 1 — Numeric °F rows (4 rows):** Converted using `°C = (°F − 32) × 5/9`

| order_id | Original (°F) | Converted (°C) |
|----------|--------------|---------------|
| ORD009 | 6°F | −14.44°C |
| ORD023 | 4°F | −15.56°C |
| ORD027 | 2°F | −16.67°C |
| ORD033 | −18°F | −27.78°C |

**Step 2 — `'Room Temp'` rows with F unit (7 rows):** Unit label updated to `C`, no numeric conversion applied.

**Result:** All 50 rows now `temp_unit = C`

> **Design decision:** `'Room Temp'` was kept as a text value rather than replaced with `25`. It carries a distinct business meaning — *"no temperature control required"* — which would be erased if converted to a number. A numeric 25 would imply a strict 25°C requirement, fundamentally misrepresenting the data.

---

## Task 5: Cross-Field Validation — Currency vs Country

**Columns:** `currency`, `country`  
**Problem:** 8 orders had currency codes inconsistent with their country

**Mismatches found and corrected:**

| order_id | Country | Wrong currency | Corrected to |
|----------|---------|---------------|-------------|
| ORD005 | Japan | USD | JPY |
| ORD007 | USA | EUR | USD |
| ORD009 | France | USD | EUR |
| ORD017 | USA | GBP | USD |
| ORD030 | UK | USD | GBP |
| ORD035 | France | GBP | EUR |
| ORD045 | USA | EUR | USD |
| ORD049 | Japan | USD | JPY |

**Fix:** Country-to-currency lookup dictionary; mismatched rows replaced with expected value  
**Rows affected:** 8  
**Remaining mismatches after fix:** 0

> **Assumption:** All mismatches treated as data entry errors. In production, currency mismatches could sometimes be intentional (e.g. an international customer paying in USD). These would require business team verification before auto-correction.

---

## Task 6: Email Validation

**Column:** `customer_email`  
**Validation method:** Regex pattern `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

**Invalid emails found:**

| order_id | Email | Issue |
|----------|-------|-------|
| ORD004 | `james.wilson@email` | Missing TLD (`.com`, `.co.uk`, etc.) |
| ORD007 | `emma.brown@emailcom` | Missing dot before `com` |
| ORD024 | `david.wilson@email` | Missing TLD |

**Action:** Flagged only — not modified  
**Reason:** The correct email address cannot be inferred. Auto-guessing `.com` risks creating a wrong or non-existent address.  
**Output:** `outputs/emails_for_review.csv`

---

## Task 7: Phone Validation

**Column:** `customer_phone`  
**Problem:** 5 phones missing the international `+` prefix

| order_id | Original | After fix | Note |
|----------|----------|-----------|------|
| ORD006 | `34-91-1234567` | `+34-91-1234567` | ✅ Valid after fix |
| ORD011 | `81-6-9876-5432` | `+81-6-9876-5432` | ✅ Valid after fix |
| ORD014 | `1-555-456-7890` | `+1-555-456-7890` | ✅ Valid after fix |
| ORD027 | `555-456-7891` | `+555-456-7891` | ⚠️ Still incomplete |
| ORD042 | `44-171-6789012` | `+44-171-6789012` | ✅ Valid after fix |

**Auto-fix:** `+` prefix added to all 5 rows  
**⚠️ ORD027 caveat:** Number appears to be missing the country code entirely (USA = `+1`). Format now has `+` prefix but is still not a valid international number.  
**Output:** `outputs/phones_for_review.csv`

---

## Helper Columns — Added and Removed

These validation columns were created during cleaning and **dropped before saving** the final output:

| Column | Purpose | Dropped? |
|--------|---------|---------|
| `expected_currency` | Mapped correct currency per country | ✅ Yes |
| `currency_valid` | Boolean flag for mismatches | ✅ Yes |
| `email_valid` | Boolean flag for email validation | ✅ Yes |
| `phone_valid` | Boolean flag for phone validation | ✅ Yes |

---

## Final Summary

| Task | Rows Changed | Method |
|------|-------------|--------|
| Date uniformity | 50 | `pd.to_datetime(format='mixed')` |
| Weight conversion | 12 | Boolean mask + `× 0.453592` |
| Distance conversion | 12 | Boolean mask + `× 1.60934` |
| Temperature conversion | 11 | Conditional mask + `(F−32)×5/9` |
| Currency correction | 8 | Country lookup → replace |
| Email validation | 0 modified / 3 flagged | Regex + manual review CSV |
| Phone fix | 5 | `+` prefix added; 1 flagged |
| **Total rows in output** | **50** | **No rows added or removed** |

---

## Files Generated

| File | Description |
|------|-------------|
| `outputs/sales_data_clean.csv` | Final cleaned dataset (50 rows × 19 columns) |
| `outputs/emails_for_review.csv` | 3 invalid emails — needs manual verification |
| `outputs/phones_for_review.csv` | 1 phone with incomplete country code |
