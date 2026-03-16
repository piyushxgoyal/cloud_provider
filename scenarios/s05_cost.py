"""
Scenario 05 — Cost Cleaning & Currency Normalization
======================================================
Cleans Cost and Currency columns:
  - Strip currency symbols (₹, $, €, £)
  - Remove comma formatting (1,200.50 → 1200.50)
  - Convert to float
  - Flag negative costs and zero costs
  - Normalize Currency names to canonical (INR/USD/EUR/GBP)

Input:  dirty Cost (string with symbols/commas), dirty Currency
Output: Cost_Clean (float), Currency_Clean, Is_Negative_Cost (bool), Is_Zero_Cost (bool)
"""

import pandas as pd
import re
import numpy as np


# Currency name normalization mapping
CURRENCY_MAP = {
    'inr': 'INR', 'indian rupee': 'INR', 'rupee': 'INR', 'rupees': 'INR',
    'usd': 'USD', 'dollar': 'USD', 'dollars': 'USD', 'us dollar': 'USD',
    'eur': 'EUR', 'euro': 'EUR', 'euros': 'EUR',
    'gbp': 'GBP', 'pound': 'GBP', 'pounds': 'GBP',
}


def clean_cost(val):
    """
    Clean a single cost value.

    Handles:
      - Currency symbols: ₹1,200.50, $500, €200, £100
      - Comma formatting: 1,200.50
      - Negative values: -500
      - Zero values: 0

    Returns:
        float or np.nan
    """
    if pd.isna(val) or str(val).strip() == '':
        return np.nan

    val = str(val).strip()

    # Remove currency symbols
    val = re.sub(r'[₹$€£]', '', val)

    # Remove commas
    val = val.replace(',', '')

    # Strip whitespace again
    val = val.strip()

    if val == '':
        return np.nan

    try:
        return float(val)
    except ValueError:
        return np.nan


def clean_currency(val):
    """
    Normalize currency name to canonical form.

    Returns:
        'INR', 'USD', 'EUR', 'GBP', or 'UNKNOWN'
    """
    if pd.isna(val) or str(val).strip() == '':
        return 'UNKNOWN'

    key = str(val).strip().lower()

    # Direct match
    if key in CURRENCY_MAP:
        return CURRENCY_MAP[key]

    # Already canonical
    if key.upper() in ('INR', 'USD', 'EUR', 'GBP'):
        return key.upper()

    return 'UNKNOWN'


def run(df, data_dir='data/raw'):
    """
    Execute S05 cleaning on the dataframe.

    Args:
        df: DataFrame with 'Cost' and 'Currency' columns

    Returns:
        df with new columns: Cost_Clean, Currency_Clean, Is_Negative_Cost, Is_Zero_Cost
    """
    # Clean cost values
    df['Cost_Clean'] = df['Cost'].apply(clean_cost)

    # Normalize currency
    df['Currency_Clean'] = df['Currency'].apply(clean_currency)

    # Flag negative and zero costs
    df['Is_Negative_Cost'] = df['Cost_Clean'] < 0
    df['Is_Zero_Cost'] = df['Cost_Clean'] == 0

    print("✅ S05 — Cost Cleaning complete")
    print(f"   Non-null costs:     {df['Cost_Clean'].notna().sum()}")
    print(f"   Null costs:         {df['Cost_Clean'].isna().sum()}")
    print(f"   Negative costs:     {df['Is_Negative_Cost'].sum()}")
    print(f"   Zero costs:         {df['Is_Zero_Cost'].sum()}")
    print(f"   Currency dist:      {df['Currency_Clean'].value_counts().to_dict()}")

    return df


if __name__ == '__main__':
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = run(billing)
    print("\nSample:")
    print(billing[['Cost', 'Cost_Clean', 'Currency', 'Currency_Clean', 'Is_Negative_Cost', 'Is_Zero_Cost']].sample(10).to_string(index=False))
