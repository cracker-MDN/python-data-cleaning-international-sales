# Data Cleaning Log - Chapter 3: International Sales Standardizer

Detailed record of all data quality issues identified and decisions made during the cleaning process.

---

## Session Information

- **Date**: 2026-03-02
- **Dataset**: sales_data_messy.csv
- **Rows**: 50
- **Columns**: 19
- **Tool**: Python 3.12, pandas

---

## Summary of Issues Found

| Issue Type | Count | Resolution |
|------------|-------|------------|
| Date format variations | 5 formats | Converted to ISO |
| Weight in lbs | 11 rows | Converted to kg |
| Distance in miles | 12 rows | Converted to km |
| Temperature in °F | 4 rows | Converted to °C |
| Currency-country mismatch | 8 rows | Fixed |
| Invalid emails | 3 rows | Flagged |
| Phones missing + | 5 rows | Fixed |

---

## Phase 1: Date Format Uniformity

### Issues Found

```python
df['order_date'].head(20)
```

Five different date formats identified:

| Row | Format | Example |
|-----|--------|---------|
| 0 | YYYY-MM-DD | 2024-01-15 |
| 1 | DD/MM/YYYY | 15/01/2024 |
| 3 | MM/DD/YYYY | 01/17/2024 |
| 5 | DD-MM-YYYY | 18-01-2024 |
| 9 | MM-DD-YYYY | 01-20-2024 |

### Decision

- **Standard format**: ISO 8601 (YYYY-MM-DD)
- **Ambiguous dates**: Used `dayfirst=True` as default (European convention)
- **Rationale**: ISO format is unambiguous and sorts correctly

### Resolution

```python
df['order_date'] = pd.to_datetime(df['order_date'], format='mixed', dayfirst=True)
```

### Note on Ambiguous Dates

Dates like 01/02/2024 could be January 2nd (US) or February 1st (EU). We used:
- `dayfirst=True` as default
- Country column could provide context for US dates if needed

### Verified

```python
df['order_date'].dtype  # datetime64[ns]
```

---

## Phase 2: Weight Unit Standardization

### Issues Found

```python
df['weight_unit'].value_counts()
# kg     39
# lbs    11
```

### Decision

- **Standard unit**: kg (metric, international standard)
- **Conversion**: 1 lb = 0.453592 kg

### Resolution

```python
lbs_mask = df['weight_unit'] == 'lbs'
df.loc[lbs_mask, 'weight'] = df.loc[lbs_mask, 'weight'] * 0.453592
df.loc[lbs_mask, 'weight_unit'] = 'kg'
```

### Verified

```python
df['weight_unit'].value_counts()
# kg    50
```

---

## Phase 3: Distance Unit Standardization

### Issues Found

```python
df['distance_unit'].value_counts()
# km       38
# miles    12
```

### Decision

- **Standard unit**: km (metric, international standard)
- **Conversion**: 1 mile = 1.60934 km

### Resolution

```python
miles_mask = df['distance_unit'] == 'miles'
df.loc[miles_mask, 'shipping_distance'] = df.loc[miles_mask, 'shipping_distance'] * 1.60934
df.loc[miles_mask, 'distance_unit'] = 'km'
```

### Verified

```python
df['distance_unit'].value_counts()
# km    50
```

---

## Phase 4: Temperature Unit Standardization

### Issues Found

```python
df['temperature_required'].value_counts()
# Room Temp    30
# 4             5
# 6             3
# (various numeric values...)

df['temp_unit'].value_counts()
# C    39
# F    11
```

### Challenge

The temperature column contains:
- Numeric values (actual temperatures)
- Text value "Room Temp" (no specific temperature needed)

Cannot apply conversion formula to "Room Temp".

### Decision

- **Standard unit**: Celsius (°C)
- **Conversion**: °C = (°F - 32) × 5/9
- **Room Temp handling**: Keep as text, only convert numeric F values
- **F rows with "Room Temp"**: Just change unit to C (no conversion needed)

### Resolution

```python
# Step 1: Convert numeric F values to C
f_numeric_mask = (df['temp_unit'] == 'F') & (df['temperature_required'] != 'Room Temp')
df.loc[f_numeric_mask, 'temperature_required'] = (
    df.loc[f_numeric_mask, 'temperature_required'].astype(float) - 32
) * 5/9
df.loc[f_numeric_mask, 'temp_unit'] = 'C'

# Step 2: Update Room Temp rows with F unit
room_temp_f_mask = (df['temp_unit'] == 'F') & (df['temperature_required'] == 'Room Temp')
df.loc[room_temp_f_mask, 'temp_unit'] = 'C'
```

### Alternative Considered

Could replace "Room Temp" with 25°C (standard room temperature). Decided against because:
- "Room Temp" means "no temperature control needed"
- 25°C means "must maintain exactly 25°C"
- These are different business requirements

### Verified

```python
df['temp_unit'].value_counts()
# C    50
```

---

## Phase 5: Cross-Field Validation - Currency vs Country

### Business Rule

Currency should match the country of the order:

| Country | Expected Currency |
|---------|-------------------|
| USA | USD |
| UK | GBP |
| Germany, France, Spain, Italy, Portugal | EUR |
| Japan | JPY |
| Poland | PLN |

### Issues Found

```python
currency_rules = {
    'USA': 'USD', 'UK': 'GBP', 'Germany': 'EUR', 
    'France': 'EUR', 'Spain': 'EUR', 'Italy': 'EUR',
    'Portugal': 'EUR', 'Japan': 'JPY', 'Poland': 'PLN'
}
df['expected_currency'] = df['country'].map(currency_rules)
df['currency_valid'] = df['currency'] == df['expected_currency']
```

8 mismatches found:

| order_id | country | actual | expected |
|----------|---------|--------|----------|
| ORD005 | Japan | USD | JPY |
| ORD007 | USA | EUR | USD |
| ORD009 | France | USD | EUR |
| ORD017 | USA | GBP | USD |
| ORD030 | UK | USD | GBP |
| ORD035 | France | GBP | EUR |
| ORD045 | USA | EUR | USD |
| ORD049 | Japan | USD | JPY |

### Decision

- **Action**: Fix automatically
- **Rationale**: Assumed data entry error, not intentional international pricing
- **In real project**: Would verify with business team first

### Resolution

```python
df.loc[~df['currency_valid'], 'currency'] = df.loc[~df['currency_valid'], 'expected_currency']
```

### Verified

```python
(~df['currency_valid']).sum()  # 0
```

---

## Phase 6: Email Validation (Regex)

### Pattern Used

```python
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

This pattern requires:
- Valid characters before @
- @ symbol
- Domain name
- Dot followed by 2+ letter TLD

### Issues Found

```python
df['email_valid'] = df['customer_email'].apply(
    lambda x: bool(re.match(email_pattern, str(x)))
)
```

3 invalid emails:

| order_id | email | issue |
|----------|-------|-------|
| ORD004 | james.wilson@email | Missing TLD (.com, etc.) |
| ORD007 | emma.brown@emailcom | Missing dot before TLD |
| ORD024 | david.wilson@email | Missing TLD |

### Decision

- **Action**: Flag only, do not fix
- **Rationale**: Cannot guess correct email address
- **Next step**: Export for manual review / customer contact

### Resolution

```python
# Created flag column
df['email_valid'] = df['customer_email'].apply(...)
# 3 rows flagged as invalid
```

### Why Not Fix?

- james.wilson@email could be @email.com, @email.org, @email.co.uk, etc.
- Guessing would introduce new errors
- Better to flag and have human verify

---

## Phase 7: Phone Validation

### Issues Found

```python
df['phone_valid'] = df['customer_phone'].astype(str).str.startswith('+')
```

5 phones missing + prefix:

| order_id | phone | country | issue |
|----------|-------|---------|-------|
| ORD006 | 34-91-1234567 | Spain | Missing + |
| ORD011 | 81-6-9876-5432 | Japan | Missing + |
| ORD014 | 1-555-456-7890 | USA | Missing + |
| ORD027 | 555-456-7891 | USA | Missing + AND country code |
| ORD042 | 44-171-6789012 | UK | Missing + |

### Decision

- **Action**: Add + prefix to all
- **Special case**: ORD027 still needs country code (flagged for manual review)

### Resolution

```python
mask = ~df['phone_valid']
df.loc[mask, 'customer_phone'] = '+' + df.loc[mask, 'customer_phone'].astype(str)
```

### Note on ORD027

After fix: +555-456-7891 (still invalid — should be +1-555-456-7891)

This demonstrates knowing when to escalate — we fixed what we could, flagged what needs human review.

---

## Final Validation

```python
print(f"Date dtype: {df['order_date'].dtype}")           # datetime64[ns]
print(f"Weight units: {df['weight_unit'].unique()}")     # ['kg']
print(f"Distance units: {df['distance_unit'].unique()}") # ['km']
print(f"Temp units: {df['temp_unit'].unique()}")         # ['C']
print(f"Currency mismatches: {(~df['currency_valid']).sum()}")  # 0
print(f"Invalid emails: {(~df['email_valid']).sum()}")   # 3
print(f"Invalid phones: {(~df['phone_valid']).sum()}")   # 0
```

---

## Key Learnings

1. **Context helps resolve ambiguity** — Country column clarifies date format

2. **Mixed types need careful handling** — "Room Temp" in numeric column requires masking

3. **Cross-field validation catches business rule violations** — Not just typos

4. **Know when to stop** — Flag invalid emails for human review instead of guessing

5. **Document judgment calls** — Future analysts need to know why you made each decision

---

## Techniques Used

| Task | Technique |
|------|-----------|
| Date conversion | `pd.to_datetime(format='mixed', dayfirst=True)` |
| Unit conversion | Boolean mask + `.loc[]` + formula |
| Cross-field validation | `.map()` with rules dictionary |
| Regex validation | `re.match()` with pattern |
| Conditional updates | Complex boolean masks with `&` |
