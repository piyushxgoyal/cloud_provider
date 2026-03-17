"""
Transformation 08 — Unit Cost Normalization (Effective Rate)
==============================================================
Calculates the Effective Unit Cost (Cost_USD / Usage_Converted) for each row.
Filters out free tiered records or 0 usage records to compute actual paid rate.

Output:
  - t08_unit_cost.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Cost_USD', 'Usage_Converted', 'SKU_Clean', 'Unit_Canonical', 'Charge_Type_Clean']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T08")
        return df
        
    # Exclude free tiers and refunds, and handle dividing by 0
    paid = df[df['Charge_Type_Clean'].astype(str).str.lower().isin(['usage', 'on-demand', 'reserved', 'spot'])].copy()
    paid = paid[paid['Usage_Converted'] > 0]
    
    paid['Effective_Rate'] = (paid['Cost_USD'] / paid['Usage_Converted'])
    
    # Aggregate by SKU to find the average effective rate across the fleet
    rates = paid.groupby(['SKU_Clean', 'Unit_Canonical'], as_index=False).agg(
        Avg_Effective_Rate=('Effective_Rate', 'mean'),
        Min_Rate=('Effective_Rate', 'min'),
        Max_Rate=('Effective_Rate', 'max'),
        Total_Spend=('Cost_USD', 'sum')
    ).round(5)
    
    rates = rates.sort_values('Total_Spend', ascending=False)
    
    rates.to_csv(os.path.join(out_dir, 't08_unit_cost.csv'), index=False)
    
    print("✅ T08 — Unit Cost Normalization generated")
    print(f"   Tracked SKUs: {len(rates)}")
    
    return rates

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
