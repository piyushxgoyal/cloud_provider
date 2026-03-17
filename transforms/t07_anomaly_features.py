"""
Transformation 07 — Anomaly Detection Features
================================================
Extracts all flagged anomalies, creating a pivot feature table summarizing
anomaly counts and peak Z-scores by Date and SKU.

Output:
  - t07_anomaly_features.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Is_Usage_Anomaly', 'Anomaly_Z_Score', 'TS_UTC', 'SKU_Clean']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T07")
        return pd.DataFrame()
        
    anomalies = df[df['Is_Usage_Anomaly']].copy()
    if anomalies.empty:
        print("⚠️ No anomalies detected in data to pivot.")
        return pd.DataFrame()
        
    anomalies['TS_UTC'] = pd.to_datetime(anomalies['TS_UTC'], utc=True, errors='coerce')
    anomalies['Date'] = anomalies['TS_UTC'].dt.date
    
    agg = anomalies.groupby(['Date', 'SKU_Clean'], as_index=False).agg(
        Anomaly_Count=('Usage_ID', 'count'),
        Max_Z_Score=('Anomaly_Z_Score', 'max'),
        Avg_Z_Score=('Anomaly_Z_Score', 'mean'),
        Total_Cost_Impact=('Cost_USD', 'sum')
    ).round(2)
    
    agg = agg.sort_values('Total_Cost_Impact', ascending=False)
    
    agg.to_csv(os.path.join(out_dir, 't07_anomaly_features.csv'), index=False)
    
    print("✅ T07 — Anomaly Detection Features generated")
    print(f"   Total Anomaly Events: {agg['Anomaly_Count'].sum()}")
    print(f"   Total Impact Cost:    ${agg['Total_Cost_Impact'].sum():.2f}")
    
    return agg

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
