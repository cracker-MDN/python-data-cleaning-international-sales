# Data Dictionary — International Sales Data

**Dataset:** `sales_data_messy.csv` / `sales_data_clean.csv`  
**Rows:** 50 orders  
**Columns:** 19  
**Date range:** 2024-01-15 to 2024-02-09  
**Countries:** USA, UK, Germany, France, Spain, Italy, Portugal, Japan, Poland

---

## Column Reference

### Order Identifiers

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `order_id` | string | `ORD001` | Unique order identifier. Format: `ORD` + 3-digit number |
| `order_date` | string → datetime | `2024-01-15` | Date the order was placed. **Messy version contains 5 different formats** — see Task 1 |

---

### Customer Information

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `customer_name` | string | `John Smith` | Full name of the customer |
| `customer_email` | string | `john.smith@email.com` | Customer email address. **Some entries are malformed** — see Task 7 |
| `customer_phone` | string | `+1-555-123-4567` | International phone number. Expected format: `+[country_code]-[number]`. **Some entries missing `+` prefix** — see Task 8 |
| `country` | string | `USA` | Customer's country. Used as reference for validating `currency` and `distance_unit` |
| `city` | string | `New York` | Customer's city |

**Countries in dataset:** USA, UK, Germany, France, Spain, Italy, Portugal, Japan, Poland

---

### Product Information

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `product_name` | string | `Organic Coffee Beans` | Name of the product ordered. 50 unique specialty food products |
| `quantity` | integer | `5` | Number of units ordered |
| `unit_price` | float | `24.99` | Price per unit in the order's currency |
| `currency` | string | `USD` | Currency of the transaction. **Must match country** — see Task 5 |

**Valid currency values by country:**

| Country | Expected Currency |
|---------|------------------|
| USA | `USD` |
| UK | `GBP` |
| Germany, France, Spain, Italy, Portugal | `EUR` |
| Japan | `JPY` |
| Poland | `PLN` |

---

### Shipping & Weight

| Column | Type | Example (messy) | Example (clean) | Description |
|--------|------|-----------------|-----------------|-------------|
| `weight` | float | `3.2` (lbs) | `1.45` (kg) | Package weight. **Messy version mixes kg and lbs** |
| `weight_unit` | string | `lbs` or `kg` | `kg` | Unit for `weight`. Standardised to `kg` in clean version |
| `shipping_distance` | float | `150` (miles) | `241.4` (km) | Distance shipped. **Messy version mixes km and miles** |
| `distance_unit` | string | `miles` or `km` | `km` | Unit for `shipping_distance`. Standardised to `km` in clean version |

---

### Temperature

| Column | Type | Example (messy) | Example (clean) | Description |
|--------|------|-----------------|-----------------|-------------|
| `temperature_required` | string/float | `6` (°F) or `Room Temp` | `-14.44` (°C) or `Room Temp` | Required storage/shipping temperature. Special value `'Room Temp'` means no temperature control required |
| `temp_unit` | string | `F` or `C` | `C` | Unit for `temperature_required`. Standardised to `C` in clean version |

**Temperature categories after cleaning:**

| Value | Meaning |
|-------|---------|
| `Room Temp` | No temperature control required (shelf-stable products) |
| `0°C to 8°C` | Refrigerated (e.g. cheese, clotted cream) |
| `Below 0°C` | Frozen (e.g. Kobe beef, smoked salmon) |
| `Above 8°C` | Chilled but not cold (e.g. some chocolates, wines) |

> **Design note:** `'Room Temp'` was preserved as a text value rather than converted to 25°C. It represents a business rule — "no temperature control required" — not a precise numeric target.

---

### Order Status

| Column | Type | Values | Description |
|--------|------|--------|-------------|
| `payment_status` | string | `Paid` (45), `Pending` (5) | Whether the order has been paid |
| `delivery_status` | string | `Delivered` (35), `Processing` (8), `In Transit` (7) | Current fulfilment status of the order |

---

## Data Quality Issues (Messy Version)

| Column | Issue | Count | Resolution |
|--------|-------|-------|------------|
| `order_date` | 5 different formats | ~15 rows | Standardised via `pd.to_datetime(format='mixed')` |
| `weight` / `weight_unit` | Mix of `kg` and `lbs` | 12 rows in lbs | Converted: `× 0.453592` |
| `shipping_distance` / `distance_unit` | Mix of `km` and `miles` | 12 rows in miles | Converted: `× 1.60934` |
| `temperature_required` / `temp_unit` | Mix of `C` and `F` | 11 rows in °F | Converted: `(F − 32) × 5/9` |
| `currency` | Doesn't match country | 8 rows | Corrected using country lookup |
| `customer_email` | Malformed (missing TLD or dot) | 3 rows | Flagged — cannot auto-fix |
| `customer_phone` | Missing `+` prefix | 5 rows | `+` added; 1 row flagged (missing country code) |

---

## Sample Products by Temperature Category

| Product | Typical Temp | Category |
|---------|-------------|----------|
| Organic Coffee Beans, Earl Grey Tea, Honey Collection | Room Temp | Shelf-stable |
| Cheese Selection, Clotted Cream, Butter Collection | 4–8°C | Refrigerated |
| Smoked Salmon, Lobster Bisque, Kobe Beef | 0–2°C | Chilled/Frozen |
| Wagyu Beef Jerky, Black Forest Ham | −18°C | Frozen |
