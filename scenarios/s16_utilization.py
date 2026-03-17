"""
Scenario 16 — CPU & Memory Utilization
========================================
Validates and cleans `CPU_Util` and `Memory_Util`.
  - Storage services must be NaN.
  - Compute/Database services must have values between 0.0 and 100.0. Missing values imputed to mean.
  - Flags IDLE (< 10%) and OVERUTILIZED (> 80%) resources.
"""

import pandas as pd
import numpy as np

def run(df):
    # Ensure S03 is run so we have Service_Clean
    if 'Service_Clean' not in df.columns:
        from scenarios.s03_sku import run as s03_run
        df = s03_run(df)
        
    df['CPU_Clean'] = df['CPU_Util']
    df['Mem_Clean'] = df['Memory_Util']
    
    # 1. Nullify Storage rows (should not have CPU/Mem)
    storage_mask = df['Service_Clean'].str.lower() == 'storage'
    df.loc[storage_mask, ['CPU_Clean', 'Mem_Clean']] = pd.NA
    
    # 2. Impute missing Compute/Database rows with domain mean (safe fallback if missing)
    non_storage_mask = ~storage_mask
    
    cpu_mean = df.loc[non_storage_mask, 'CPU_Clean'].mean()
    mem_mean = df.loc[non_storage_mask, 'Mem_Clean'].mean()
    
    df.loc[non_storage_mask & df['CPU_Clean'].isna(), 'CPU_Clean'] = cpu_mean
    df.loc[non_storage_mask & df['Mem_Clean'].isna(), 'Mem_Clean'] = mem_mean
    
    # 3. Clip out-of-bounds metrics to 0-100 range
    df['CPU_Clean'] = pd.to_numeric(df['CPU_Clean'], errors='coerce')
    df['Mem_Clean'] = pd.to_numeric(df['Mem_Clean'], errors='coerce')
    
    df.loc[non_storage_mask, 'CPU_Clean'] = df.loc[non_storage_mask, 'CPU_Clean'].clip(0, 100)
    df.loc[non_storage_mask, 'Mem_Clean'] = df.loc[non_storage_mask, 'Mem_Clean'].clip(0, 100)
    
    # 4. Generate Insight Flags
    # IDLE: CPU and Mem both < 10%
    df['Is_Idle'] = (df['CPU_Clean'] < 10) & (df['Mem_Clean'] < 10) & non_storage_mask
    
    # OVERUTILIZED: CPU or Mem > 80% (just OR check for alert purposes)
    df['Is_Overutilized'] = ((df['CPU_Clean'] > 80) | (df['Mem_Clean'] > 80)) & non_storage_mask
    
    print("✅ S16 — CPU/Memory Utilization complete")
    print(f"   Storage nulled:       {storage_mask.sum()}")
    print(f"   Idle resources:       {df['Is_Idle'].sum()}")
    print(f"   Overutilized res:     {df['Is_Overutilized'].sum()}")
    
    return df
