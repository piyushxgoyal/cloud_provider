"""
Transformation 16 — Churn Risk Signals
========================================
Identifies accounts with a drastic drop in usage month-over-month.
Used to alert Customer Success teams to potential SaaS churn.

Output:
  - t16_churn_risk_signals.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Account_ID', 'TS_UTC', 'Usage_Converted']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T16")
        return pd.DataFrame()
        
    ts_df = df.dropna(subset=['TS_UTC']).copy()
    ts_df['TS_UTC'] = pd.to_datetime(ts_df['TS_UTC'], utc=True)
    ts_df['Month'] = ts_df['TS_UTC'].dt.to_period('M')
    
    # Monthly usage by account
    monthly = ts_df.groupby(['Account_ID', 'Month'], as_index=False).agg(
        Total_Usage=('Usage_Converted', 'sum')
    )
    
    monthly = monthly.sort_values(['Account_ID', 'Month'])
    
    # Calculate MoM change
    monthly['Prev_Month_Usage'] = monthly.groupby('Account_ID')['Total_Usage'].shift(1)
    
    # Calculate percentage drop
    def calc_drop(row):
        curr = row['Total_Usage']
        prev = row['Prev_Month_Usage']
        if pd.isna(prev) or prev == 0:
            return 0.0
        return round(((curr - prev) / prev * 100), 1)
        
    monthly['MoM_Usage_Change_Pct'] = monthly.apply(calc_drop, axis=1)
    
    # Filter to accounts with > 50% drop (Churn Risk)
    risk = monthly[monthly['MoM_Usage_Change_Pct'] < -50.0].copy()
    
    risk['Risk_Level'] = risk['MoM_Usage_Change_Pct'].apply(
        lambda x: 'Critical' if x < -80 else 'High'
    )
    
    risk = risk.sort_values('MoM_Usage_Change_Pct', ascending=True) # Lowest first (biggest drop)
    
    risk.to_csv(os.path.join(out_dir, 't16_churn_risk_signals.csv'), index=False)
    
    print("✅ T16 — Churn Risk Signals generated")
    print(f"   Accounts at Risk: {len(risk)}")
    
    return risk

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
