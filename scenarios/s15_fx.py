"""
Scenario 15 — FX Rate Normalization
=====================================
Validates and cleans the `FX_Rate` column based on `Currency_Clean`.
  - Fixes missing FX rates using standard canonical rates.
  - Fixes wrong direction rates (e.g., INR 84.0 -> 1/84.0 -> ~0.0119, handled canonically).
  - Calculates `Cost_USD` = `Cost_Clean` * `FX_Rate_Clean`.
"""

import pandas as pd
import numpy as np

# Canonical rates (as defined in the dataset generation)
CANONICAL_FX = {
    'USD': 1.00,
    'INR': 0.012,
    'EUR': 1.08,
    'GBP': 1.27
}

def fix_fx_rate(row):
    currency = row['Currency_Clean']
    rate = row['FX_Rate']
    
    desired = CANONICAL_FX.get(currency, 1.0)
    
    # Missing rate -> use canonical
    if pd.isna(rate):
        return desired
        
    # If the rate is exactly the canonical one, keep it
    if np.isclose(rate, desired, atol=1e-4):
        return rate
        
    # If the rate is the inverse (wrong direction) like 84.0 for INR
    if rate > 0 and np.isclose(1.0 / rate, desired, atol=1e-2):
        return desired # Fix it to canonical
        
    # Anything else just gets the canonical rate to be safe
    return desired

def run(df):
    # Ensure S05 is run so we have Currency_Clean and Cost_Clean
    if 'Currency_Clean' not in df.columns or 'Cost_Clean' not in df.columns:
        from scenarios.s05_cost import run as s05_run
        df = s05_run(df)
        
    # Apply FX fixes
    df['FX_Rate_Clean'] = df.apply(fix_fx_rate, axis=1)
    
    # Calculate Cost_USD
    df['Cost_USD'] = df['Cost_Clean'] * df['FX_Rate_Clean']
    
    # Flags for reporting
    df['FX_Missing'] = df['FX_Rate'].isna()
    df['FX_Wrong_Direction'] = (df['FX_Rate'] > 1) & (df['Currency_Clean'] == 'INR')  # Primary check based on generation
    
    missing_cnt = df['FX_Missing'].sum()
    wrong_dir_cnt = df['FX_Wrong_Direction'].sum()
    
    print("✅ S15 — FX Rate Normalization complete")
    print(f"   Missing FX Rates Fixed:   {missing_cnt}")
    print(f"   Inverted Rates Fixed:     {wrong_dir_cnt}")
    print(f"   Cost_USD Calculated:      {len(df)}")
    
    return df
