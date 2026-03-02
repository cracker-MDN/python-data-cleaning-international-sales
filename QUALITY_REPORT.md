# Data Quality Report

Generated after cleaning process completion.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Records | 50 |
| Records Cleaned | 50 |
| Records Dropped | 0 |
| Data Quality Score | 94% |

---

## Cleaning Summary

### Uniformity Fixes

| Issue | Records Affected | Action | Result |
|-------|------------------|--------|--------|
| Date format variations | 50 | Converted to ISO | 100% uniform |
| Weight in lbs | 11 | Converted to kg | 100% uniform |
| Distance in miles | 12 | Converted to km | 100% uniform |
| Temperature in °F | 4 | Converted to °C | 100% uniform |

### Validation Fixes

| Issue | Records Affected | Action | Result |
|-------|------------------|--------|--------|
| Currency-country mismatch | 8 | Auto-corrected | 100% valid |
| Invalid email format | 3 | Flagged | Requires manual review |
| Phone missing + prefix | 5 | Auto-corrected | 100% valid |

---

## Column Quality Scores

| Column | Completeness | Validity | Uniformity | Score |
|--------|--------------|----------|------------|-------|
| order_id | 100% | 100% | 100% | ✓ |
| order_date | 100% | 100% | 100% | ✓ |
| customer_name | 100% | 100% | 100% | ✓ |
| customer_email | 100% | 94% | 100% | ⚠️ |
| customer_phone | 100% | 100% | 100% | ✓ |
| country | 100% | 100% | 100% | ✓ |
| city | 100% | 100% | 100% | ✓ |
| product_name | 100% | 100% | 100% | ✓ |
| quantity | 100% | 100% | 100% | ✓ |
| unit_price | 100% | 100% | 100% | ✓ |
| currency | 100% | 100% | 100% | ✓ |
| weight | 100% | 100% | 100% | ✓ |
| weight_unit | 100% | 100% | 100% | ✓ |
| shipping_distance | 100% | 100% | 100% | ✓ |
| distance_unit | 100% | 100% | 100% | ✓ |
| temperature_required | 100% | 100% | 100% | ✓ |
| temp_unit | 100% | 100% | 100% | ✓ |
| payment_status | 100% | 100% | 100% | ✓ |
| delivery_status | 100% | 100% | 100% | ✓ |

---

## Outstanding Issues

### Requires Manual Review

| order_id | Issue | Current Value | Suggested Action |
|----------|-------|---------------|------------------|
| ORD004 | Invalid email | james.wilson@email | Contact customer |
| ORD007 | Invalid email | emma.brown@emailcom | Contact customer |
| ORD024 | Invalid email | david.wilson@email | Contact customer |
| ORD027 | Phone missing country code | +555-456-7891 | Verify correct prefix |

---

## Recommendations

1. **Implement input validation** at data entry to prevent format issues
2. **Create dropdown menus** for country/currency fields to ensure consistency
3. **Add email verification** step in customer registration
4. **Standardize phone input** with country code selector

---

## Methodology

- **Completeness**: % of non-null values
- **Validity**: % passing validation rules
- **Uniformity**: % in standard format

**Overall Score**: Average of all column scores
