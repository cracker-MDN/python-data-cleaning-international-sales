# Chapter 3: Advanced Data Problems - Practice Guide

## Dataset: International Sales Data Standardizer

You have 50 international sales orders with advanced data quality issues. This chapter focuses on cross-field validation, unit standardization, and pattern matching.

---

## Problems Overview

| Problem Type | Lesson | Count | Columns Affected |
|--------------|--------|-------|------------------|
| Date format inconsistency | Uniformity | ~15 | order_date |
| Unit conversion needed | Uniformity | ~12 | weight_unit, distance_unit |
| Temperature unit mismatch | Uniformity | ~8 | temp_unit vs country |
| Currency-country mismatch | Cross-field validation | ~6 | currency vs country |
| Invalid email format | Pattern matching (regex) | ~4 | customer_email |
| Invalid phone format | Pattern matching (regex) | ~5 | customer_phone |
| Distance unit mismatch | Cross-field validation | ~8 | distance_unit vs country |

---

## TASK 1: Date Format Uniformity

**Lesson: "Uniformity" - Dates**

The `order_date` column has multiple formats:

| Format | Example | Countries typically using |
|--------|---------|---------------------------|
| YYYY-MM-DD | 2024-01-15 | ISO standard, Japan |
| DD/MM/YYYY | 15/01/2024 | UK, Europe, most of world |
| MM/DD/YYYY | 01/17/2024 | USA |
| DD-MM-YYYY | 18-01-2024 | Europe variant |
| MM-DD-YYYY | 01-20-2024 | USA variant |

**Your tasks:**
- [ ] Identify all date formats present
- [ ] Convert all to a single standard format (YYYY-MM-DD recommended)
- [ ] Handle ambiguous dates (is 01/02/2024 January 2nd or February 1st?)

**Hint code:**
```python
# Check unique date patterns
print(df['order_date'].head(20))

# Convert with dayfirst parameter for DD/MM/YYYY formats
# Be careful: some are MM/DD/YYYY (USA)
```

**Challenge:** How do you handle truly ambiguous dates like 01/02/2024? You may need to use the `country` column as context!

---

## TASK 2: Weight Unit Standardization

**Lesson: "Uniformity" - Unit conversion**

The `weight` column has values in different units:

| Unit | Rows using it | Conversion |
|------|---------------|------------|
| kg | ~38 | Standard |
| lbs | ~12 | × 0.453592 to get kg |

**Your tasks:**
- [ ] Find all rows with weight in lbs
- [ ] Convert lbs to kg
- [ ] Update the weight_unit column to 'kg'
- [ ] Round to 2 decimal places

**Hint code:**
```python
# Find lbs rows
lbs_mask = df['weight_unit'] == 'lbs'
print(f"Rows in lbs: {lbs_mask.sum()}")

# Convert
df.loc[lbs_mask, 'weight'] = df.loc[lbs_mask, 'weight'] * 0.453592
df.loc[lbs_mask, 'weight_unit'] = 'kg'
```

---

## TASK 3: Distance Unit Standardization

**Lesson: "Uniformity" - Unit conversion**

The `shipping_distance` column has values in different units:

| Unit | Conversion |
|------|------------|
| km | Standard |
| miles | × 1.60934 to get km |

**Your tasks:**
- [ ] Find all rows with distance in miles
- [ ] Convert miles to km
- [ ] Update the distance_unit column

**Cross-field issue:** Some European countries have distances in miles (wrong!) and some US orders have km (also wrong!). This connects to Task 6.

---

## TASK 4: Temperature Unit Standardization

**Lesson: "Uniformity" - Unit conversion**

The `temperature_required` column stores temperature for shipping. The `temp_unit` column indicates F or C.

**Issue:** USA uses Fahrenheit, but most of the world uses Celsius.

| Unit | Conversion to Celsius |
|------|----------------------|
| C | Standard |
| F | (F - 32) × 5/9 |

**Special value:** "Room Temp" means no specific temperature required.

**Your tasks:**
- [ ] Handle "Room Temp" values (convert to NaN or keep as special category)
- [ ] Convert numeric Fahrenheit values to Celsius
- [ ] Standardize temp_unit to 'C'

**Hint code:**
```python
# First, separate room temp from numeric temps
room_temp_mask = df['temperature_required'] == 'Room Temp'

# Convert temperature column to numeric (Room Temp becomes NaN)
df['temperature_required'] = pd.to_numeric(df['temperature_required'], errors='coerce')
```

---

## TASK 5: Cross-Field Validation - Currency vs Country

**Lesson: "Cross-field validation"**

Currency should match country! These are the valid combinations:

| Country | Expected Currency |
|---------|-------------------|
| USA | USD |
| UK | GBP |
| Germany, France, Spain, Italy, Portugal | EUR |
| Japan | JPY |
| Poland | PLN |

**Your tasks:**
- [ ] Find rows where currency doesn't match country
- [ ] Investigate: Is the currency wrong or is it intentional (international pricing)?
- [ ] Decide how to handle: flag, fix, or document

**Hint code:**
```python
# Define expected currencies
currency_rules = {
    'USA': 'USD',
    'UK': 'GBP',
    'Germany': 'EUR',
    'France': 'EUR',
    'Spain': 'EUR',
    'Italy': 'EUR',
    'Portugal': 'EUR',
    'Japan': 'JPY',
    'Poland': 'PLN'
}

# Check each row
def check_currency(row):
    expected = currency_rules.get(row['country'])
    return row['currency'] == expected

df['currency_valid'] = df.apply(check_currency, axis=1)
print(df[~df['currency_valid']][['order_id', 'country', 'currency']])
```

---

## TASK 6: Cross-Field Validation - Distance Unit vs Country

**Lesson: "Cross-field validation"**

Distance units should be appropriate for the country:

| Country | Expected Unit |
|---------|---------------|
| USA, UK | miles |
| All others (metric countries) | km |

**Your tasks:**
- [ ] Find rows where distance unit doesn't match country convention
- [ ] Decide: Convert to expected unit or keep as-is with flag?

---

## TASK 7: Email Validation with Regex

**Lesson: "Pattern matching" - Regular expressions**

The `customer_email` column has some invalid emails:

| Issue | Example |
|-------|---------|
| Missing @ symbol | james.wilson@email (no domain) |
| Missing dot in domain | emma.brown@emailcom |
| Completely invalid | various |

**Your tasks:**
- [ ] Create a regex pattern for valid emails
- [ ] Find all invalid emails
- [ ] Flag or fix them

**Hint code:**
```python
import re

# Basic email pattern
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Check validity
df['email_valid'] = df['customer_email'].apply(
    lambda x: bool(re.match(email_pattern, str(x)))
)

# Find invalid
print(df[~df['email_valid']][['order_id', 'customer_email']])
```

---

## TASK 8: Phone Number Validation with Regex

**Lesson: "Pattern matching" - Regular expressions**

The `customer_phone` column has inconsistent formats:

| Issue | Example |
|-------|---------|
| Missing country code + | 34-91-1234567 (should be +34...) |
| Missing + prefix | 1-555-456-7890 (should be +1...) |
| Inconsistent separators | Some use -, some use spaces |

**Your tasks:**
- [ ] Identify phone numbers missing the + prefix
- [ ] Standardize format or flag invalid entries

**Hint code:**
```python
# Check if starts with +
df['phone_has_plus'] = df['customer_phone'].str.startswith('+')
print(df[~df['phone_has_plus']][['order_id', 'customer_phone', 'country']])
```

---

## TASK 9: Temperature Cross-Validation

**Lesson: "Cross-field validation"**

Some products require refrigeration or freezing. Check if temperatures make sense:

| Temperature Range | Meaning |
|-------------------|---------|
| Below 0°C | Frozen |
| 0-8°C | Refrigerated |
| Above 8°C or Room Temp | Shelf stable |

**Cross-check with products:**
- Beef, salmon, lobster should be cold/frozen
- Coffee, tea, honey should be room temp

**Your tasks:**
- [ ] Find products with suspicious temperature requirements
- [ ] Flag potential data entry errors

---

## Summary: Problems Planted

### Date Formats (15 issues)
- Rows 2, 4, 8, 10, 12, 16, 18, 22, 26, 30, 34, 38, 42, 46, 50: Various non-ISO formats

### Weight in lbs (12 rows)
- Rows 3, 7, 10, 14, 19, 21, 28, 33, 37, 39, 42: Weight in lbs instead of kg

### Currency Mismatches (6 rows)
- Row 5: Japan with USD
- Row 7: USA with EUR
- Row 9: France with USD
- Row 17: USA with GBP
- Row 30: UK with USD
- Row 35, 45, 49: Various mismatches

### Invalid Emails (4 rows)
- Row 4: james.wilson@email (missing TLD)
- Row 7: emma.brown@emailcom (missing dot)
- Row 24: david.wilson@email (missing TLD)

### Phone Issues (5 rows)
- Row 6, 11, 14, 27, 42: Missing + prefix

### Distance Unit Issues (8 rows)
- European countries with miles instead of km
- USA orders with km instead of miles

---

## Validation Checklist

After cleaning, verify:

- [ ] All dates in YYYY-MM-DD format
- [ ] All weights in kg
- [ ] All distances in km (or appropriate for country)
- [ ] All temperatures in Celsius
- [ ] All emails match valid pattern
- [ ] All phones have + prefix
- [ ] Currency matches country (or flagged if intentional)

---

## Stretch Goals

1. **Create a `validate_order()` function** that checks all cross-field rules
2. **Build a data quality report** showing % valid for each check
3. **Handle ambiguous dates** using country context
4. **Calculate shipping cost** using standardized distance/weight

Good luck! This chapter requires more judgment calls than previous chapters.
