"""
Transformation 12 — FinOps KPIs (Blended Rate & Effective Discount)
=====================================================================
Calculates high-level financial metrics for the month:
1. Blended Rate: Total Cost / Total Usage (per SKU)
2. Effective Discount: Compares theoretical public price vs actual paid sum.

Output:
  - t12_finops_kpis.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['SKU_Clean', 'Cost_USD', 'Usage_Converted', 'Price_Version_Clean', 'Charge_Type_Clean']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T12")
        return pd.DataFrame()
        
    if not os.path.exists('data/raw/sku_catalog.csv'):
        print("⚠️ Missing sku_catalog.csv for T12")
        return pd.DataFrame()
        
    catalog = pd.read_csv('data/raw/sku_catalog.csv')
    
    # We only care about positive usage rows
    finops = df[df['Usage_Converted'] > 0].copy()
    
    # 1. Blended Rate
    # Just sum cost / sum usage per SKU
    kpi = finops.groupby('SKU_Clean', as_index=False).agg(
        Total_Cost_USD=('Cost_USD', 'sum'),
        Total_Usage=('Usage_Converted', 'sum')
    )
    kpi['Blended_Rate'] = (kpi['Total_Cost_USD'] / kpi['Total_Usage']).round(4)
    
    # 2. Effective Discount Calculation
    # We need the catalog public price. Join on SKU and Price_Version.
    # Note: Catalog has Price_Currency. We'll simplify assuming catalog is in USD or we just measure relative %.
    # The actual implementation involves matching catalog Price_Currency to USD but for this scenario
    # we just compute nominal "Public Cost" and compare to actual.
    
    # Merge catalog to get public rate
    # For a robust merge we need SKU name in catalog. We mapped this in S03.
    # To keep simple, we'll map catalog SKU_ID directly since we used it.
    
    merged = pd.merge(
        finops, 
        catalog[['SKU_ID', 'Price_Version', 'Price_Per_Unit']], 
        left_on=['SKU_Clean', 'Price_Version_Clean'], 
        right_on=['SKU_ID', 'Price_Version'],
        how='left'
    )
    
    merged['Public_Cost_Theoretical'] = merged['Usage_Converted'] * merged['Price_Per_Unit']
    
    # Aggregate back
    discount_agg = merged.groupby('SKU_Clean', as_index=False).agg(
        Total_Public_Cost=('Public_Cost_Theoretical', 'sum'),
        Actual_Cost=('Cost_USD', 'sum')
    )
    
    # Discount % = (Public - Actual) / Public
    # Avoid zero division
    discount_agg['Effective_Discount_Pct'] = 0.0
    mask = discount_agg['Total_Public_Cost'] > 0
    discount_agg.loc[mask, 'Effective_Discount_Pct'] = (
        (discount_agg.loc[mask, 'Total_Public_Cost'] - discount_agg.loc[mask, 'Actual_Cost']) 
        / discount_agg.loc[mask, 'Total_Public_Cost'] * 100
    ).round(2)
    
    # Merge both metrics
    final_kpis = pd.merge(kpi, discount_agg[['SKU_Clean', 'Effective_Discount_Pct']], on='SKU_Clean')
    
    # If discount is negative, it means we paid more than public rate (anomalies/penalties)
    
    final_kpis.to_csv(os.path.join(out_dir, 't12_finops_kpis.csv'), index=False)
    
    print("✅ T12 — FinOps KPIs generated")
    print(f"   Calculated Blended Rates for {len(final_kpis)} SKUs")
    
    return final_kpis

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
