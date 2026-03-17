"""
Transformation 20 — Public Dashboard Extracts
===============================================
Pre-computes safe, high-level JSON data used by frontend charts to load quickly,
avoiding raw DB scans.
1. Top 5 accounts by spend
2. Spend by top 3 services

Output:
  - t20_public_dash.json
"""

import pandas as pd
import os
import json

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Account_ID', 'Service_Clean', 'Cost_USD']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T20")
        return {}
        
    dashboard = {}
    
    # 1. Top 5 Accounts
    top_acts = df.groupby('Account_ID')['Cost_USD'].sum().sort_values(ascending=False).head(5)
    dashboard['top_5_accounts'] = [
        {"account": act, "cost_usd": round(cost, 2)} 
        for act, cost in dict(top_acts).items()
    ]
    
    # 2. Spend by Top 3 Services
    top_svcs = df.groupby('Service_Clean')['Cost_USD'].sum().sort_values(ascending=False).head(3)
    dashboard['top_3_services'] = [
        {"service": svc, "cost_usd": round(cost, 2)}
        for svc, cost in dict(top_svcs).items()
    ]
    
    with open(os.path.join(out_dir, 't20_public_dash.json'), 'w') as f:
        json.dump(dashboard, f, indent=2)
        
    print("✅ T20 — Public Dashboard Extracts generated")
    
    return dashboard

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
