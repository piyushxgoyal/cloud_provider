"""
Transformation 03 — RI / Savings Plan Utilization
===================================================
Calculates the ratio of Cost structured as 'reserved' vs 'on-demand' vs 'spot'.
Used by FinOps to measure committed coverage metrics.

Output:
  - t03_ri_utilization.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    if 'Purchase_Type_Clean' not in df.columns or 'Cost_USD' not in df.columns:
        print("⚠️ Missing columns for T03")
        return df
        
    # Group by purchase type
    ri = df.groupby('Purchase_Type_Clean', as_index=False).agg(
        Total_Cost_USD=('Cost_USD', 'sum'),
        Record_Count=('Usage_ID', 'count')
    )
    
    # Calculate % of total cost
    total_cost = ri['Total_Cost_USD'].sum()
    if total_cost > 0:
        ri['Cost_Percentage'] = (ri['Total_Cost_USD'] / total_cost * 100).round(2)
    else:
        ri['Cost_Percentage'] = 0.0
        
    ri.to_csv(os.path.join(out_dir, 't03_ri_utilization.csv'), index=False)
    
    print("✅ T03 — RI/SP Utilization generated")
    try:
        res_pct = ri.loc[ri['Purchase_Type_Clean'] == 'reserved', 'Cost_Percentage'].values[0]
        print(f"   Reserved Coverage: {res_pct}%")
    except:
        pass
        
    return ri

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
