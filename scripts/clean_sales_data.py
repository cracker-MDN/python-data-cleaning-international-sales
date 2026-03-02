"""
clean_sales_data.py
-------------------
Chapter 3 – Data Import & Cleaning: International Sales Data
DataCamp | Data Manipulation with Python

Cleans a messy international sales CSV across 7 tasks:
  1. Date format uniformity      — 5 formats → datetime64
  2. Weight standardisation      — lbs → kg
  3. Distance standardisation    — miles → km
  4. Temperature standardisation — °F → °C (skips 'Room Temp' text)
  5. Cross-field validation      — currency must match country
  6. Email validation            — regex flag (cannot auto-fix)
  7. Phone validation            — adds missing + prefix

Usage:
    python scripts/clean_sales_data.py

Input  : data/sales_data_messy.csv
Outputs: outputs/sales_data_clean.csv
         outputs/emails_for_review.csv
         outputs/phones_for_review.csv
"""

import pandas as pd
import numpy as np
import re

# ── LOAD ──────────────────────────────────────────────────────────────────
df = pd.read_csv('data/sales_data_messy.csv')
print(f"Loaded: {df.shape[0]} rows × {df.shape[1]} columns\n")

# ── TASK 1: DATE UNIFORMITY ───────────────────────────────────────────────
# 5 formats present: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD-MM-YYYY, MM-DD-YYYY
# dayfirst=True: when ambiguous, assume day comes first (European convention)
df['order_date'] = pd.to_datetime(df['order_date'], format='mixed', dayfirst=True)
print(f"✓ Task 1: Dates → datetime64  |  range: {df['order_date'].min().date()} to {df['order_date'].max().date()}")

# ── TASK 2: WEIGHT (lbs → kg) ────────────────────────────────────────────
lbs_mask = df['weight_unit'] == 'lbs'
df.loc[lbs_mask, 'weight'] = (df.loc[lbs_mask, 'weight'] * 0.453592).round(6)
df.loc[lbs_mask, 'weight_unit'] = 'kg'
print(f"✓ Task 2: Weight  — {lbs_mask.sum()} rows converted lbs → kg")

# ── TASK 3: DISTANCE (miles → km) ────────────────────────────────────────
df['shipping_distance'] = df['shipping_distance'].astype(float)
miles_mask = df['distance_unit'] == 'miles'
df.loc[miles_mask, 'shipping_distance'] = (df.loc[miles_mask, 'shipping_distance'] * 1.60934).round(3)
df.loc[miles_mask, 'distance_unit'] = 'km'
print(f"✓ Task 3: Distance — {miles_mask.sum()} rows converted miles → km")

# ── TASK 4: TEMPERATURE (°F → °C) ────────────────────────────────────────
# Two cases:
#   a) Numeric °F values  → convert using (F - 32) × 5/9
#   b) 'Room Temp' with F unit → update label only (no math on text)
f_numeric_mask = (df['temp_unit'] == 'F') & (df['temperature_required'] != 'Room Temp')
df.loc[f_numeric_mask, 'temperature_required'] = (
    (df.loc[f_numeric_mask, 'temperature_required'].astype(float) - 32) * 5 / 9
).round(2)
df.loc[f_numeric_mask, 'temp_unit'] = 'C'

room_f_mask = (df['temp_unit'] == 'F') & (df['temperature_required'] == 'Room Temp')
df.loc[room_f_mask, 'temp_unit'] = 'C'
print(f"✓ Task 4: Temp    — {f_numeric_mask.sum()} numeric + {room_f_mask.sum()} label-only rows converted °F → °C")

# ── TASK 5: CROSS-FIELD VALIDATION — CURRENCY vs COUNTRY ─────────────────
currency_rules = {
    'USA': 'USD', 'UK': 'GBP',
    'Germany': 'EUR', 'France': 'EUR', 'Spain': 'EUR',
    'Italy': 'EUR', 'Portugal': 'EUR',
    'Japan': 'JPY', 'Poland': 'PLN'
}
df['expected_currency'] = df['country'].map(currency_rules)
df['currency_valid'] = df['currency'] == df['expected_currency']
n_fixed = (~df['currency_valid']).sum()
df.loc[~df['currency_valid'], 'currency'] = df.loc[~df['currency_valid'], 'expected_currency']
df['currency_valid'] = df['currency'] == df['expected_currency']
print(f"✓ Task 5: Currency — {n_fixed} mismatches corrected  |  remaining: {(~df['currency_valid']).sum()}")

# ── TASK 6: EMAIL VALIDATION (flag only) ─────────────────────────────────
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
df['email_valid'] = df['customer_email'].apply(
    lambda x: bool(re.match(email_pattern, str(x)))
)
print(f"✓ Task 6: Email   — {(~df['email_valid']).sum()} invalid addresses flagged (cannot auto-fix)")

# ── TASK 7: PHONE VALIDATION ──────────────────────────────────────────────
df['phone_valid'] = df['customer_phone'].astype(str).str.startswith('+')
invalid_mask = ~df['phone_valid']
df.loc[invalid_mask, 'customer_phone'] = '+' + df.loc[invalid_mask, 'customer_phone'].astype(str)
df['phone_valid'] = df['customer_phone'].astype(str).str.startswith('+')
print(f"✓ Task 7: Phone   — + prefix added  |  remaining invalid: {(~df['phone_valid']).sum()}")

# ── FINAL VALIDATION REPORT ───────────────────────────────────────────────
print("\n" + "=" * 45)
print("         FINAL VALIDATION REPORT")
print("=" * 45)
print(f"  Total rows          : {len(df)}")
print(f"  Date dtype          : {df['order_date'].dtype}")
print(f"  Weight units        : {sorted(df['weight_unit'].unique())}")
print(f"  Distance units      : {sorted(df['distance_unit'].unique())}")
print(f"  Temp units          : {sorted(df['temp_unit'].unique())}")
print(f"  Currency errors     : {(~df['currency_valid']).sum()}")
print(f"  Invalid emails      : {(~df['email_valid']).sum()}  ← flagged, see emails_for_review.csv")
print(f"  Invalid phones      : {(~df['phone_valid']).sum()}")
print("=" * 45)

# ── EXPORT FLAGGED ROWS ───────────────────────────────────────────────────
emails_flagged = df[~df['email_valid']][['order_id', 'customer_name', 'customer_email']]
emails_flagged.to_csv('outputs/emails_for_review.csv', index=False)
print(f"\n📋 Flagged: outputs/emails_for_review.csv  ({len(emails_flagged)} rows)")

phones_flagged = df[~df['phone_valid']][['order_id', 'customer_name', 'customer_phone', 'country']]
phones_flagged.to_csv('outputs/phones_for_review.csv', index=False)
print(f"📋 Flagged: outputs/phones_for_review.csv  ({len(phones_flagged)} rows)")

# ── SAVE CLEANED DATA ─────────────────────────────────────────────────────
helper_cols = ['expected_currency', 'currency_valid', 'email_valid', 'phone_valid']
df_clean = df.drop(columns=helper_cols)
df_clean.to_csv('outputs/sales_data_clean.csv', index=False)
print(f"\n✅ Saved: outputs/sales_data_clean.csv  ({len(df_clean)} rows × {len(df_clean.columns)} columns)")
