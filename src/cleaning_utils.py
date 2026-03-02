"""
International Sales Data Cleaning Utilities
Reusable functions for unit conversion, cross-field validation, and pattern matching.
"""

import pandas as pd
import numpy as np
import re


# =============================================================================
# CONVERSION CONSTANTS
# =============================================================================

LBS_TO_KG = 0.453592
MILES_TO_KM = 1.60934

CURRENCY_RULES = {
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

EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


# =============================================================================
# UNIT CONVERSION FUNCTIONS
# =============================================================================

def convert_weight_to_kg(df: pd.DataFrame, weight_col: str = 'weight', 
                         unit_col: str = 'weight_unit') -> pd.DataFrame:
    """
    Convert weight from lbs to kg.
    
    Parameters:
        df: DataFrame with weight data
        weight_col: Name of weight column
        unit_col: Name of unit column
    
    Returns:
        DataFrame with standardized weight in kg
    """
    df = df.copy()
    mask = df[unit_col] == 'lbs'
    
    df.loc[mask, weight_col] = df.loc[mask, weight_col] * LBS_TO_KG
    df.loc[mask, unit_col] = 'kg'
    
    return df


def convert_distance_to_km(df: pd.DataFrame, distance_col: str = 'shipping_distance',
                           unit_col: str = 'distance_unit') -> pd.DataFrame:
    """
    Convert distance from miles to km.
    
    Parameters:
        df: DataFrame with distance data
        distance_col: Name of distance column
        unit_col: Name of unit column
    
    Returns:
        DataFrame with standardized distance in km
    """
    df = df.copy()
    mask = df[unit_col] == 'miles'
    
    # Convert to float first to avoid dtype warning
    df[distance_col] = df[distance_col].astype(float)
    df.loc[mask, distance_col] = df.loc[mask, distance_col] * MILES_TO_KM
    df.loc[mask, unit_col] = 'km'
    
    return df


def convert_temp_to_celsius(df: pd.DataFrame, temp_col: str = 'temperature_required',
                            unit_col: str = 'temp_unit', 
                            room_temp_value: str = 'Room Temp') -> pd.DataFrame:
    """
    Convert temperature from Fahrenheit to Celsius.
    Handles mixed numeric and text values (e.g., "Room Temp").
    
    Parameters:
        df: DataFrame with temperature data
        temp_col: Name of temperature column
        unit_col: Name of unit column
        room_temp_value: Text value indicating no specific temperature needed
    
    Returns:
        DataFrame with standardized temperature in Celsius
    """
    df = df.copy()
    
    # Only convert numeric F values
    f_numeric_mask = (df[unit_col] == 'F') & (df[temp_col] != room_temp_value)
    
    df.loc[f_numeric_mask, temp_col] = (
        df.loc[f_numeric_mask, temp_col].astype(float) - 32
    ) * 5/9
    df.loc[f_numeric_mask, unit_col] = 'C'
    
    # Update Room Temp F rows (just change unit)
    room_temp_f_mask = (df[unit_col] == 'F') & (df[temp_col] == room_temp_value)
    df.loc[room_temp_f_mask, unit_col] = 'C'
    
    return df


# =============================================================================
# CROSS-FIELD VALIDATION FUNCTIONS
# =============================================================================

def validate_currency_country(df: pd.DataFrame, currency_col: str = 'currency',
                              country_col: str = 'country',
                              rules: dict = None) -> pd.DataFrame:
    """
    Validate that currency matches expected currency for each country.
    
    Parameters:
        df: DataFrame with currency and country data
        currency_col: Name of currency column
        country_col: Name of country column
        rules: Dictionary mapping country to expected currency
    
    Returns:
        DataFrame with expected_currency and currency_valid columns added
    """
    if rules is None:
        rules = CURRENCY_RULES
    
    df = df.copy()
    df['expected_currency'] = df[country_col].map(rules)
    df['currency_valid'] = df[currency_col] == df['expected_currency']
    
    return df


def fix_currency_mismatches(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix currency values that don't match expected currency for country.
    Must run validate_currency_country first.
    
    Parameters:
        df: DataFrame with currency_valid column
    
    Returns:
        DataFrame with corrected currency values
    """
    df = df.copy()
    
    if 'currency_valid' not in df.columns:
        raise ValueError("Run validate_currency_country first")
    
    mask = ~df['currency_valid']
    df.loc[mask, 'currency'] = df.loc[mask, 'expected_currency']
    
    # Revalidate
    df['currency_valid'] = df['currency'] == df['expected_currency']
    
    return df


# =============================================================================
# PATTERN VALIDATION FUNCTIONS
# =============================================================================

def validate_emails(df: pd.DataFrame, email_col: str = 'customer_email',
                    pattern: str = None) -> pd.DataFrame:
    """
    Validate email addresses using regex pattern.
    
    Parameters:
        df: DataFrame with email data
        email_col: Name of email column
        pattern: Regex pattern for valid email (default provided)
    
    Returns:
        DataFrame with email_valid column added
    """
    if pattern is None:
        pattern = EMAIL_PATTERN
    
    df = df.copy()
    df['email_valid'] = df[email_col].apply(
        lambda x: bool(re.match(pattern, str(x)))
    )
    
    return df


def validate_phones(df: pd.DataFrame, phone_col: str = 'customer_phone') -> pd.DataFrame:
    """
    Validate phone numbers have + prefix.
    
    Parameters:
        df: DataFrame with phone data
        phone_col: Name of phone column
    
    Returns:
        DataFrame with phone_valid column added
    """
    df = df.copy()
    df['phone_valid'] = df[phone_col].astype(str).str.startswith('+')
    
    return df


def fix_phone_prefix(df: pd.DataFrame, phone_col: str = 'customer_phone') -> pd.DataFrame:
    """
    Add + prefix to phone numbers that are missing it.
    
    Parameters:
        df: DataFrame with phone data
        phone_col: Name of phone column
    
    Returns:
        DataFrame with fixed phone numbers
    """
    df = df.copy()
    
    if 'phone_valid' not in df.columns:
        df = validate_phones(df, phone_col)
    
    mask = ~df['phone_valid']
    df.loc[mask, phone_col] = '+' + df.loc[mask, phone_col].astype(str)
    
    # Revalidate
    df['phone_valid'] = df[phone_col].astype(str).str.startswith('+')
    
    return df


# =============================================================================
# COMPLETE PIPELINE
# =============================================================================

def clean_sales_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Complete cleaning pipeline for international sales data.
    
    Parameters:
        df: Raw DataFrame to clean
    
    Returns:
        Tuple of (cleaned DataFrame, cleaning report dictionary)
    """
    df_clean = df.copy()
    report = {
        'original_rows': len(df),
        'steps': []
    }
    
    # Step 1: Standardize dates
    df_clean['order_date'] = pd.to_datetime(df_clean['order_date'], format='mixed', dayfirst=True)
    report['steps'].append("Dates: Converted to datetime64")
    
    # Step 2: Convert weight
    lbs_count = (df_clean['weight_unit'] == 'lbs').sum()
    df_clean = convert_weight_to_kg(df_clean)
    report['steps'].append(f"Weight: Converted {lbs_count} rows from lbs to kg")
    
    # Step 3: Convert distance
    miles_count = (df_clean['distance_unit'] == 'miles').sum()
    df_clean = convert_distance_to_km(df_clean)
    report['steps'].append(f"Distance: Converted {miles_count} rows from miles to km")
    
    # Step 4: Convert temperature
    f_count = (df_clean['temp_unit'] == 'F').sum()
    df_clean = convert_temp_to_celsius(df_clean)
    report['steps'].append(f"Temperature: Converted {f_count} rows from F to C")
    
    # Step 5: Validate and fix currency
    df_clean = validate_currency_country(df_clean)
    mismatches = (~df_clean['currency_valid']).sum()
    df_clean = fix_currency_mismatches(df_clean)
    report['steps'].append(f"Currency: Fixed {mismatches} country mismatches")
    
    # Step 6: Validate emails
    df_clean = validate_emails(df_clean)
    invalid_emails = (~df_clean['email_valid']).sum()
    report['steps'].append(f"Emails: {invalid_emails} invalid (flagged)")
    
    # Step 7: Validate and fix phones
    df_clean = validate_phones(df_clean)
    invalid_phones = (~df_clean['phone_valid']).sum()
    df_clean = fix_phone_prefix(df_clean)
    report['steps'].append(f"Phones: Fixed {invalid_phones} missing + prefix")
    
    return df_clean, report


def generate_quality_report(df: pd.DataFrame) -> dict:
    """
    Generate a data quality report for cleaned data.
    
    Parameters:
        df: Cleaned DataFrame
    
    Returns:
        Dictionary with quality metrics
    """
    report = {
        'total_rows': len(df),
        'date_dtype': str(df['order_date'].dtype),
        'weight_unit_uniform': (df['weight_unit'] == 'kg').all(),
        'distance_unit_uniform': (df['distance_unit'] == 'km').all(),
        'temp_unit_uniform': (df['temp_unit'] == 'C').all(),
        'currency_valid_pct': df['currency_valid'].mean() * 100 if 'currency_valid' in df.columns else None,
        'email_valid_pct': df['email_valid'].mean() * 100 if 'email_valid' in df.columns else None,
        'phone_valid_pct': df['phone_valid'].mean() * 100 if 'phone_valid' in df.columns else None
    }
    
    return report


def print_cleaning_report(report: dict) -> None:
    """Print formatted cleaning report."""
    print("=" * 50)
    print("CLEANING REPORT")
    print("=" * 50)
    print(f"Original rows: {report['original_rows']}")
    print("\nSteps completed:")
    for step in report['steps']:
        print(f"  ✓ {step}")
    print("=" * 50)


# =============================================================================
# RUN IF EXECUTED DIRECTLY
# =============================================================================

if __name__ == "__main__":
    # Load data
    df = pd.read_csv('data/raw/sales_data_messy.csv')
    print(f"Loaded {len(df)} rows\n")
    
    # Clean data
    df_clean, report = clean_sales_data(df)
    print_cleaning_report(report)
    
    # Quality report
    print("\nQuality Report:")
    quality = generate_quality_report(df_clean)
    for key, value in quality.items():
        print(f"  {key}: {value}")
    
    # Save (drop helper columns)
    cols_to_drop = ['expected_currency', 'currency_valid', 'email_valid', 'phone_valid']
    df_export = df_clean.drop(columns=[c for c in cols_to_drop if c in df_clean.columns])
    df_export.to_csv('data/processed/sales_data_clean.csv', index=False)
    print("\nCleaned data saved to data/processed/sales_data_clean.csv")
