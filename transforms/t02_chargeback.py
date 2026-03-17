"""
Transformation 02 — Chargeback / Showback
===========================================
Aggregates Cost_USD by:
  - Department
  - Project

This is the core table used by Finance to charge internal teams.

Output:
  - t02_chargeback.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req_cols = ['Dept_Clean', 'Project_Clean', 'Cost_USD']
    if not all(c in df.columns for c in req_cols):
        print("⚠️ Missing columns for T02")
        return df
        
    cb = df.copy()
    cb['Dept_Clean'] = cb['Dept_Clean'].fillna('UNKNOWN_DEPT')
    cb['Project_Clean'] = cb['Project_Clean'].fillna('UNKNOWN_PROJECT')
    
    # Rollup
    chargeback = cb.groupby(['Dept_Clean', 'Project_Clean'], as_index=False).agg(
        Total_Cost_USD=('Cost_USD', 'sum'),
        Record_Count=('Usage_ID', 'count')
    ).sort_values('Total_Cost_USD', ascending=False)
    
    chargeback.to_csv(os.path.join(out_dir, 't02_chargeback.csv'), index=False)
    
    print("✅ T02 — Chargeback Table generated")
    print(f"   Total Departments: {chargeback['Dept_Clean'].nunique()}")
    print(f"   Total Projects:    {chargeback['Project_Clean'].nunique()}")
    
    return chargeback

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
