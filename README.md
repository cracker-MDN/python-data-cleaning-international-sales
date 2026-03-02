# International Sales Data Standardizer

A data cleaning project demonstrating advanced techniques including unit conversion, cross-field validation, and regex pattern matching using Python and pandas.

## Project Overview

This project takes international sales data (50 orders across 9 countries) and standardizes units, validates cross-field relationships, and ensures data quality through pattern matching. It demonstrates practical skills in handling real-world data from multiple regions with different conventions.

### The Challenge

International data is messy because different countries use different:
- Date formats (MM/DD vs DD/MM)
- Units of measurement (miles vs km, lbs vs kg, °F vs °C)
- Currencies (USD, EUR, GBP, JPY, PLN)
- Phone number formats

### The Approach

Applied a systematic methodology combining:
1. **Uniformity**: Convert all units to a single standard
2. **Cross-field validation**: Verify values make sense together
3. **Pattern matching**: Validate formats with regex
4. **Judgment calls**: Know when to fix vs flag vs escalate

## Results Summary

| Issue Type | Before | After |
|------------|--------|-------|
| Date formats | 5 different | All ISO (YYYY-MM-DD) |
| Weight units | kg + lbs mixed | All kg |
| Distance units | km + miles mixed | All km |
| Temperature units | °C + °F mixed | All °C |
| Currency mismatches | 8 | 0 |
| Invalid emails | 3 | Flagged |
| Invalid phones | 5 | Fixed |

## Issues Found & Solutions

### 1. Date Format Uniformity

| Format Found | Example | Region |
|--------------|---------|--------|
| YYYY-MM-DD | 2024-01-15 | ISO standard |
| DD/MM/YYYY | 15/01/2024 | European |
| MM/DD/YYYY | 01/17/2024 | American |
| DD-MM-YYYY | 18-01-2024 | European variant |
| MM-DD-YYYY | 01-20-2024 | American variant |

**Solution**: Used `pd.to_datetime(format='mixed', dayfirst=True)` with country context for ambiguous dates.

### 2. Unit Conversions

| Conversion | Formula | Rows Affected |
|------------|---------|---------------|
| lbs → kg | × 0.453592 | 11 |
| miles → km | × 1.60934 | 12 |
| °F → °C | (F-32) × 5/9 | 4 |

**Challenge**: Temperature column had mixed numeric values and "Room Temp" text. Solution: Created mask to only convert numeric Fahrenheit values.

### 3. Cross-Field Validation: Currency vs Country

| Country | Expected Currency |
|---------|-------------------|
| USA | USD |
| UK | GBP |
| Germany, France, Spain, Italy, Portugal | EUR |
| Japan | JPY |
| Poland | PLN |

**Found 8 mismatches** — orders where currency didn't match country. Fixed by mapping to expected currency.

### 4. Email Validation (Regex)

Pattern used: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

| Issue | Example | Count |
|-------|---------|-------|
| Missing TLD | james.wilson@email | 2 |
| Missing dot | emma.brown@emailcom | 1 |

**Decision**: Flagged but not fixed — can't guess correct email.

### 5. Phone Validation

| Issue | Example | Solution |
|-------|---------|----------|
| Missing + prefix | 34-91-1234567 | Added + |
| Missing country code | 555-456-7891 | Flagged for manual review |

## Project Structure

```
chapter3_sales_standardizer/
├── README.md                    # Project documentation
├── CLEANING_LOG.md              # Detailed cleaning decisions
├── requirements.txt             # Python dependencies
├── data/
│   ├── raw/
│   │   └── sales_data_messy.csv
│   └── processed/
│       └── sales_data_clean.csv
├── notebooks/
│   └── data_cleaning.ipynb
└── src/
    └── cleaning_utils.py
```

## Key Techniques Used

### Unit Conversion Pattern
```python
# Mask → Convert → Update unit
mask = df['weight_unit'] == 'lbs'
df.loc[mask, 'weight'] = df.loc[mask, 'weight'] * 0.453592
df.loc[mask, 'weight_unit'] = 'kg'
```

### Cross-Field Validation Pattern
```python
# Define rules → Map expected → Compare → Flag/Fix
currency_rules = {'USA': 'USD', 'UK': 'GBP', ...}
df['expected'] = df['country'].map(currency_rules)
df['valid'] = df['currency'] == df['expected']
```

### Regex Validation Pattern
```python
import re
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
df['valid'] = df['email'].apply(lambda x: bool(re.match(pattern, str(x))))
```

## Skills Demonstrated

- **Uniformity**: Standardizing units across international data
- **Cross-field validation**: Ensuring logical consistency between columns
- **Regex patterns**: Validating email and phone formats
- **Conditional logic**: Complex masks for selective updates
- **Judgment calls**: Knowing when to fix vs flag vs escalate
- **Documentation**: Clear logging of decisions and rationale

## How to Run

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sales-data-standardizer.git
cd sales-data-standardizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the notebook:
```bash
jupyter notebook notebooks/data_cleaning.ipynb
```

## Key Learnings

1. **International data needs context** — Country column helped interpret ambiguous dates

2. **Not everything can be auto-fixed** — Invalid emails need manual review; flag and escalate

3. **Cross-field validation catches logical errors** — Currency-country mismatch isn't a typo, it's a business rule violation

4. **Handle mixed types carefully** — "Room Temp" text in a numeric temperature column requires masking

5. **Document your judgment calls** — Why fix currency but only flag email? Write it down.

## Technologies Used

- Python 3.12
- pandas 2.0+
- NumPy
- Regular expressions (re module)
- Jupyter Notebook

## Dataset

Synthetic international sales data with fields:
- Order info: order_id, order_date
- Customer info: name, email, phone, country, city
- Product info: product_name, quantity, unit_price, currency
- Shipping info: weight, weight_unit, shipping_distance, distance_unit
- Temperature requirements: temperature_required, temp_unit
- Status: payment_status, delivery_status

## Author

[MD Noornabi]

## License

MIT License - feel free to use for learning!
