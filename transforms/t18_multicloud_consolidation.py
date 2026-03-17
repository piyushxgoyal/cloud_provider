"""
Transformation 18 — Multi-Cloud Consolidation
===============================================
A master pivot unifying AWS, Azure, and GCP spend by canonical Service and Region.
Excellent for high-level executive dashbaords.

Output:
  - t18_multicloud_consolidation.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Cost_USD', 'Service_Clean', 'Region_Clean', 'Account_Clean']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T18")
        return pd.DataFrame()
        
    # Infer provider
    mc = df.copy()
    mc['Cloud_Provider'] = mc['Account_Clean'].str.split('-').str[0].str.upper().replace({'AZ': 'AZURE'})
    
    # Clean region/service NAs
    mc['Service_Clean'] = mc['Service_Clean'].fillna('UNKNOWN')
    mc['Region_Clean'] = mc['Region_Clean'].fillna('UNKNOWN')
    
    pivot = mc.pivot_table(
        index=['Service_Clean', 'Region_Clean'],
        columns='Cloud_Provider',
        values='Cost_USD',
        aggfunc='sum',
        fill_value=0.0
    ).reset_index()
    
    # Add a cross-cloud total
    providers = [c for c in pivot.columns if c not in ['Service_Clean', 'Region_Clean']]
    pivot['Total_MultiCloud_Spend'] = pivot[providers].sum(axis=1)
    
    pivot = pivot.sort_values('Total_MultiCloud_Spend', ascending=False)
    
    pivot.to_csv(os.path.join(out_dir, 't18_multicloud_consolidation.csv'), index=False)
    
    print("✅ T18 — Multi-Cloud Consolidation Pivot generated")
    
    return pivot

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
