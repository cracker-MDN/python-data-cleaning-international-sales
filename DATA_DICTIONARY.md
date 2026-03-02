# Data Dictionary

Documentation of all fields in the International Sales dataset.

---

## Dataset Overview

| Property | Value |
|----------|-------|
| File | sales_data_messy.csv / sales_data_clean.csv |
| Rows | 50 |
| Columns | 19 |
| Date Range | January - February 2024 |
| Countries | 9 (USA, UK, Germany, France, Spain, Italy, Portugal, Japan, Poland) |

---

## Column Definitions

### Order Information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| order_id | string | Unique order identifier | ORD001 |
| order_date | date | Date order was placed | 2024-01-15 |

### Customer Information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| customer_name | string | Full name of customer | John Smith |
| customer_email | string | Customer email address | john.smith@email.com |
| customer_phone | string | Phone with country code | +1-555-123-4567 |
| country | string | Customer's country | USA |
| city | string | Customer's city | New York |

### Product Information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| product_name | string | Name of product ordered | Organic Coffee Beans |
| quantity | integer | Number of units ordered | 5 |
| unit_price | float | Price per unit | 24.99 |
| currency | string | Currency code (ISO 4217) | USD |

### Shipping Information

| Column | Type | Description | Example | After Cleaning |
|--------|------|-------------|---------|----------------|
| weight | float | Product weight | 2.5 | All in kg |
| weight_unit | string | Unit of weight | kg, lbs | All 'kg' |
| shipping_distance | float | Distance to destination | 150 | All in km |
| distance_unit | string | Unit of distance | km, miles | All 'km' |

### Temperature Requirements

| Column | Type | Description | Example | After Cleaning |
|--------|------|-------------|---------|----------------|
| temperature_required | string/float | Required shipping temp | 4, "Room Temp" | All in °C |
| temp_unit | string | Temperature unit | C, F | All 'C' |

**Note:** "Room Temp" indicates no specific temperature control needed.

### Status Information

| Column | Type | Description | Valid Values |
|--------|------|-------------|--------------|
| payment_status | string | Payment state | Paid, Pending |
| delivery_status | string | Delivery state | Delivered, In Transit, Processing |

---

## Valid Values Reference

### Countries & Expected Currencies

| Country | Currency Code | Currency Name |
|---------|---------------|---------------|
| USA | USD | US Dollar |
| UK | GBP | British Pound |
| Germany | EUR | Euro |
| France | EUR | Euro |
| Spain | EUR | Euro |
| Italy | EUR | Euro |
| Portugal | EUR | Euro |
| Japan | JPY | Japanese Yen |
| Poland | PLN | Polish Zloty |

### Temperature Categories

| Value | Meaning | Typical Products |
|-------|---------|------------------|
| Room Temp | No control needed | Coffee, tea, honey, pasta |
| 0-8°C | Refrigerated | Cheese, ham, butter |
| Below 0°C | Frozen | Salmon, lobster, ice cream |

---

## Data Quality Notes

### Validation Rules Applied

1. **Currency-Country Match**: Currency must match expected currency for country
2. **Email Format**: Must match pattern `xxx@xxx.xx`
3. **Phone Format**: Must start with `+` country code

### Known Limitations

- 3 emails flagged as invalid (cannot auto-correct)
- 1 phone missing country code (flagged for manual review)
- Ambiguous dates assumed European format (day first)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-02 | Initial cleaning and standardization |
