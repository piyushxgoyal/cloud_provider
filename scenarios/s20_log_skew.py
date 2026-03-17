"""
Scenario 20 — Log Time Skew Normalization
===========================================
Validates and cleans `Log_Skew_Seconds`.
  - Imputes missing (null) skews to 0.0.
  - Flags any row where the absolute skew exceeds 60 seconds as `Is_High_Skew`.
"""

import pandas as pd

def clean_log_skew(val):
    try:
        if pd.isna(val):
            return 0.0
        return float(val)
    except:
        return 0.0

def run(df):
    if 'Log_Skew_Seconds' not in df.columns:
        print("⚠️ Log_Skew_Seconds column missing, skipping S20.")
        return df
        
    df['Log_Skew_Clean'] = df['Log_Skew_Seconds'].apply(clean_log_skew)
    
    # Flag if absolute value > 60.0
    df['Is_High_Skew'] = df['Log_Skew_Clean'].abs() > 60.0
    
    print("✅ S20 — Log Time Skew Normalization complete")
    null_skews = df['Log_Skew_Seconds'].isna().sum()
    print(f"   Null Skews Imputed to 0.0: {null_skews}")
    print(f"   High Skew Logs Flagged:    {df['Is_High_Skew'].sum()}")
    
    return df
