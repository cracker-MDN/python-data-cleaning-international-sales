# 🧹 Data Import & Cleaning — International Sales Data

> Transforms a messy, multi-format international sales dataset into a clean, analysis-ready file using pandas and regex.

---

## 📋 Project Overview

Real-world data rarely arrives clean — especially international datasets where different countries use different date formats, units of measurement, and currencies. This project simulates exactly that scenario with 50 international food orders across 9 countries.

**Dataset:** `sales_data_messy.csv` — 50 orders · 19 columns · 9 countries  
**Outcome:** A fully validated, standardised CSV ready for downstream analysis

---

## 🛠️ Cleaning Tasks

| # | Task | Problem | Technique |
|---|------|---------|-----------|
| 1 | **Date Uniformity** | 5 different formats in one column | `pd.to_datetime(format='mixed', dayfirst=True)` |
| 2 | **Weight Standardisation** | `kg` and `lbs` mixed | Boolean mask · `× 0.453592` |
| 3 | **Distance Standardisation** | `km` and `miles` mixed | Boolean mask · `× 1.60934` |
| 4 | **Temperature Standardisation** | `°F` + text `'Room Temp'` mixed with `°C` | Conditional mask — numeric rows only |
| 5 | **Cross-Field Validation** | Currency didn't match country | Country → currency lookup table |
| 6 | **Email Validation** | Malformed addresses (missing TLD / dot) | Regex · flag for manual review |
| 7 | **Phone Validation** | Missing international `+` prefix | String fix · 1 flagged for review |

---

## 💡 Key Analyst Decisions

**Why keep `'Room Temp'` as text instead of converting to 25°C?**  
`'Room Temp'` is a business rule meaning *"no temperature control required"*. Replacing it with 25 would imply a precise temperature requirement where none exists — changing the fundamental meaning of the data.

**Why flag emails instead of fixing them?**  
We can't know whether `james.wilson@email` ends in `.com`, `.co.uk`, or `.org`. Guessing incorrectly is worse than flagging it for a human to verify.

**What is cross-field validation?**  
Checking consistency *between* columns — not just within one. The `currency` column is only meaningful when checked against `country`. ORD007 had `country = USA` with `currency = EUR` — a clear data entry error caught only by comparing both columns together.

**Fix vs Flag vs Escalate:**  
- Phones missing `+` → auto-fixable (pattern is clear)  
- Emails with missing domain parts → flag (can't guess correctly)  
- Currency mismatches → fixed (business rules are unambiguous)

---

## 📁 Repo Structure

```
ch3-sales-data-cleaning/
│
├── data/
│   └── sales_data_messy.csv           ← Raw input (7 types of data quality issues)
│
├── notebooks/
│   └── ch3_sales_data_cleaning.ipynb  ← Step-by-step walkthrough with explanations
│
├── scripts/
│   └── clean_sales_data.py            ← Standalone runnable script
│
├── outputs/
│   ├── sales_data_clean.csv           ← Final cleaned dataset
│   ├── emails_for_review.csv          ← 3 flagged emails (manual review needed)
│   └── phones_for_review.csv          ← 1 flagged phone (incomplete country code)
│
├── docs/
│   ├── DATA_DICTIONARY.md             ← All 19 columns explained with valid values
│   └── PROBLEMS_CHECKLIST.md          ← Practice guide for the 9 cleaning tasks
│
├── CLEANING_LOG.md                    ← Every change made, rows affected, decisions taken
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run

**Option A — Notebook (step-by-step with explanations):**
```bash
jupyter notebook notebooks/ch3_sales_data_cleaning.ipynb
```

**Option B — Script (runs all 7 tasks end to end):**
```bash
python scripts/clean_sales_data.py
```

---

## 📦 Requirements

```bash
pip install -r requirements.txt
```

| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | ≥ 2.0.0 | Data manipulation |
| `numpy` | ≥ 1.24.0 | Numerical operations |
| `re` | stdlib | Regex email/phone validation |

---

## 📊 Before & After

| Column | Before (messy) | After (clean) |
|--------|---------------|--------------|
| `order_date` | 5 mixed string formats | Uniform `datetime64[ns]` |
| `weight` | `kg` + `lbs` mixed | All `kg` |
| `shipping_distance` | `km` + `miles` mixed | All `km` |
| `temperature_required` | `°C` + `°F` + text | All `°C` + text preserved |
| `currency` | 8 wrong codes | All corrected |
| `customer_email` | 3 malformed | 3 flagged · exported for review |
| `customer_phone` | 5 missing `+` | All prefixed · 1 flagged for review |

---

## 🔗 Related Projects

- 📊 [Ice Cream Sales Analysis](https://github.com/yourusername/ice-cream-sales-analysis) — Excel · SUMIFS · R² correlation
- 🧠 [Glassdoor Text Cleaning](https://github.com/yourusername/glassdoor-text-cleaning) — NLTK · TextBlob · NLP prep

---

*Built by [Your Name] · [LinkedIn URL]*
