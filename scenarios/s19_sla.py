"""
Scenario 19 — SLA Event Normalization
=======================================
Validates and cleans `SLA_Event` boolean flags.
  - Converts string variations ('true', '1', 'yes', 'false', '0', 'no') into native Python booleans (True/False).
  - Flags rows that had messy boolean strings.
"""

import pandas as pd

def clean_sla_boolean(val):
    if pd.isna(val):
        return False  # Default to False if null
        
    val_str = str(val).strip().lower()
    if val_str in ['true', '1', 'yes', 't', 'y']:
        return True
    elif val_str in ['false', '0', 'no', 'f', 'n']:
        return False
    else:
        return False  # Fail safe

def run(df):
    if 'SLA_Event' not in df.columns:
        print("⚠️ SLA_Event column missing, skipping S19.")
        return df
        
    df['SLA_Event_Clean'] = df['SLA_Event'].apply(clean_sla_boolean)
    
    # Flag to detect if it was messy (needed cleaning)
    # A perfectly clean string representation of a boolean in a CSV is typically 'True' or 'False'
    df['SLA_Messy_Flag'] = (df['SLA_Event'].astype(str) != df['SLA_Event_Clean'].astype(str)) & df['SLA_Event'].notna()
    
    # Let's also enforce string format for final output consistency if requested
    df['SLA_Event_Clean_Str'] = df['SLA_Event_Clean'].astype(str)
    
    # 3. Printing stats
    print("✅ S19 — SLA Event Normalization complete")
    print(f"   Messy Booleans Fixed: {df['SLA_Messy_Flag'].sum()}")
    print(f"   Total TRUE SLAs:      {df['SLA_Event_Clean'].sum()}")
    
    return df
