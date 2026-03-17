"""
Scenario 14 — Price Version Conflict
=======================================
Validates and cleans the `Price_Version` column based on the date of usage.
  - Jan -> v1
  - Feb -> v2
  - Mar -> v3
If the provided Price_Version differs (or is dirty like 'version1', 'V-2'), 
flag it and enforce the correct version.
"""

import pandas as pd
import re

def clean_version_string(val):
    if pd.isna(val):
        return pd.NA
    val = str(val).strip().lower()
    
    # Extract digit
    m = re.search(r'(\d+)', val)
    if m:
        return f"v{m.group(1)}"
    return pd.NA

def run(df):
    # Ensure TS_UTC exists; run S02 if not
    if 'TS_UTC' not in df.columns:
        from scenarios.s02_timestamp import run as s02_run
        df = s02_run(df)
        
    df['Price_Version_Parsed'] = df['Price_Version'].apply(clean_version_string)
    
    # Calculate Expected Version from TS_UTC month
    # If TS_UTC is NaT, we can't determine the correct version
    df['Expected_Price_Version'] = df['TS_UTC'].apply(
        lambda ts: f"v{ts.month}" if pd.notna(ts) else pd.NA
    )
    
    # Flag Mismatches: anything that is missing or not an exact string match to the canonical Expected version
    df['Price_Version_Mismatch'] = (df['Price_Version'] != df['Expected_Price_Version'])
    
    # Clean output is the strictly derived version if possible, else the parsed one
    df['Price_Version_Clean'] = df['Expected_Price_Version'].combine_first(df['Price_Version_Parsed'])
    
    print("✅ S14 — Price Version Conflict complete")
    print(f"   Original Nulls:         {df['Price_Version'].isna().sum()}")
    print(f"   Mismatches Fixed:       {df['Price_Version_Mismatch'].sum()}")
    print(f"   Missing TS (No Ver):    {df['TS_UTC'].isna().sum()}")
    
    # Drop temp column
    df = df.drop(columns=['Price_Version_Parsed'])
    
    return df
