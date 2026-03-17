"""
Transformation 17 — Unit Economics (Gross Margin Proxy)
=========================================================
Estimates gross margins per account by comparing their infrastructure
spend against a simulated flat SaaS subscription revenue ($500/mo).

Output:
  - t17_unit_economics.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    if 'Account_ID' not in df.columns or 'Cost_USD' not in df.columns:
        print("⚠️ Missing columns for T17")
        return pd.DataFrame()
        
    # Aggregate total cost per account
    econ = df.groupby('Account_ID', as_index=False).agg(
        Infra_Cost_COGS=('Cost_USD', 'sum')
    )
    
    # Simulated flat revenue for the dataset timeframe
    FLAT_REVENUE = 500.00
    econ['Estimated_Revenue'] = FLAT_REVENUE
    
    econ['Gross_Profit'] = (econ['Estimated_Revenue'] - econ['Infra_Cost_COGS']).round(2)
    econ['Gross_Margin_Pct'] = ((econ['Gross_Profit'] / econ['Estimated_Revenue']) * 100).round(1)
    
    econ['Status'] = econ['Gross_Margin_Pct'].apply(
        lambda x: 'Profitable' if x > 0 else 'Loss_Making'
    )
    
    econ = econ.sort_values('Gross_Margin_Pct', ascending=True) # Unprofitable first
    
    econ.to_csv(os.path.join(out_dir, 't17_unit_economics.csv'), index=False)
    
    print("✅ T17 — Unit Economics generated")
    losses = (econ['Status'] == 'Loss_Making').sum()
    print(f"   Loss Making Accounts: {losses} / {len(econ)}")
    
    return econ

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
