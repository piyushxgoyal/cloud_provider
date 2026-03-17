"""
Transformation 13 — Optimization Opportunity Backlog
======================================================
Identifies resources recommended for termination (from T04) and estimates
potential 30-day savings based on their current unit cost.

Output:
  - t13_optimization_backlog.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    t04_path = os.path.join(out_dir, 't04_idle_resources.csv')
    t08_path = os.path.join(out_dir, 't08_unit_cost.csv')
    
    if not os.path.exists(t04_path) or not os.path.exists(t08_path):
        print("⚠️ Missing T04 or T08 outputs to build T13 backlog.")
        return pd.DataFrame()
        
    idle = pd.read_csv(t04_path)
    rates = pd.read_csv(t08_path)
    
    # We want to estimate 30-day savings for 'Terminate' candidates
    # We need the resource's SKU to find its rate. We'll join back to billing df to get SKU mapping.
    res_sku = df[['Resource_ID', 'SKU_Clean']].dropna().drop_duplicates(subset=['Resource_ID'])
    
    backlog = pd.merge(idle, res_sku, on='Resource_ID', how='left')
    backlog = pd.merge(backlog, rates[['SKU_Clean', 'Avg_Effective_Rate']], on='SKU_Clean', how='left')
    
    # To project savings, we assume 730 hours (or 2.6M seconds) in a month
    # If unit is seconds: rate * 2628000
    # If unit is GB: we just use rate * avg usage, but for idle we focus on compute
    
    def calc_potential_savings(row):
        rate = row['Avg_Effective_Rate']
        if pd.isna(rate) or row['Action_Recommended'] != 'Terminate':
            return 0.0
        # Assume seconds rate for Compute, ~2.6M seconds in a month
        return rate * 2592000 
        
    backlog['Est_Monthly_Savings_USD'] = backlog.apply(calc_potential_savings, axis=1).round(2)
    
    # Sort by highest ROI
    backlog = backlog.sort_values('Est_Monthly_Savings_USD', ascending=False)
    
    # Status column for Jira integration
    backlog['Status'] = 'Open'
    
    backlog.to_csv(os.path.join(out_dir, 't13_optimization_backlog.csv'), index=False)
    
    print("✅ T13 — Optimization Backlog generated")
    total_savings = backlog['Est_Monthly_Savings_USD'].sum()
    print(f"   Potential Monthly Savings: ${total_savings:.2f}")
    
    return backlog

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
