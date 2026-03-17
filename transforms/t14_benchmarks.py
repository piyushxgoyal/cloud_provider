"""
Transformation 14 — Industry Benchmarks
=========================================
Derives the percentage spend by cloud provider and compares against a 
simulated "Industry Average" of 60% AWS, 30% Azure, 10% GCP.

Output:
  - t14_industry_benchmarks.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    if 'Cost_USD' not in df.columns:
        print("⚠️ Missing Cost_USD for T14")
        return pd.DataFrame()
        
    # Infer provider from SKU or Region if canonical Cloud_Provider isn't directly on row
    # We mapped Account_ID -> Cloud_Provider in S01 theoretically, but we can extract from Account_ID prefix
    df['Cloud_Provider_Extracted'] = df['Account_ID'].str.split('-').str[0].str.upper()
    
    # Fix 'AZ' -> 'AZURE'
    df['Cloud_Provider_Extracted'] = df['Cloud_Provider_Extracted'].replace({'AZ': 'AZURE'})
    
    brand = df.groupby('Cloud_Provider_Extracted', as_index=False).agg(
        Total_Spend=('Cost_USD', 'sum')
    )
    
    total = brand['Total_Spend'].sum()
    if total > 0:
        brand['Our_Spend_Pct'] = (brand['Total_Spend'] / total * 100).round(1)
    else:
        brand['Our_Spend_Pct'] = 0.0
        
    # Map industry benchmarks
    industry_map = {
        'AWS': 60.0,
        'AZURE': 30.0,
        'GCP': 10.0
    }
    
    brand['Industry_Benchmark_Pct'] = brand['Cloud_Provider_Extracted'].map(industry_map).fillna(0.0)
    
    # Variance
    brand['Variance_vs_Industry'] = (brand['Our_Spend_Pct'] - brand['Industry_Benchmark_Pct']).round(1)
    
    brand.to_csv(os.path.join(out_dir, 't14_industry_benchmarks.csv'), index=False)
    
    print("✅ T14 — Industry Benchmarks generated")
    
    return brand

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
