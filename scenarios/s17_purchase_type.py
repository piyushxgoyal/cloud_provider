"""
Scenario 17 — Purchase Type Normalization
===========================================
Validates and cleans `Purchase_Type`.
  - Normalizes various string formats, cases, and separators into standard canon.
  - Canonical values: 'on-demand', 'reserved', 'spot'.
"""

import pandas as pd

def clean_purchase_type(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'on-demand'  # default fallback if missing
        
    val_str = str(val).lower().strip()
    
    # Check for specific variations
    if 'spot' in val_str:
        return 'spot'
    elif 'reserv' in val_str or val_str == 'ri':
        return 'reserved'
    else:
        return 'on-demand'  # default covers 'on-demand', 'on_demand', 'on demand', etc.

def run(df):
    df['Purchase_Type_Clean'] = df['Purchase_Type'].apply(clean_purchase_type)
    
    # Flags for reporting
    df['Purchase_Type_Mismatch'] = (df['Purchase_Type'] != df['Purchase_Type_Clean']) & df['Purchase_Type'].notna()
    
    print("✅ S17 — Purchase Type Normalization complete")
    mismatches = df['Purchase_Type_Mismatch'].sum()
    print(f"   Purchase Type Mismatches Fixed: {mismatches}")
    print(f"   Unique Clean Purchase Types:    {df['Purchase_Type_Clean'].nunique()}")
    
    return df
