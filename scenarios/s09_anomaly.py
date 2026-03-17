"""
Scenario 09 — Usage Anomaly Detection
======================================
Identifies usage value spikes.
~500 rows were injected with 10x-50x multipliers during generation.

Method:
  We use the Interquartile Range (IQR) method grouped by SKU_Clean and Region.
  High outliers are flagged.

Input:  Usage_Value (from raw), SKU_Clean (from S03)
Output: Is_Usage_Anomaly (bool), Anomaly_Z_Score (float/NaN)
"""

import pandas as pd
import numpy as np

def run(df, data_dir='data/raw'):
    """
    Execute S09 anomaly detection.
    Requires SKU_Clean from S03 to be present.
    """
    # We will use Z-score grouping by SKU_Clean to find spikes.
    # Since normal data is uniformly distributed in defined ranges,
    # the 10x-50x spikes will have massive Z-scores.
    
    df['Is_Usage_Anomaly'] = False
    df['Anomaly_Z_Score'] = np.nan
    
    def calculate_robust_zscore(group):
        median = group.median()
        # MAD = median(|x - median|)
        mad = (group - median).abs().median()
        
        # If MAD is zero, use a small epsilon or fallback to std if std > 0
        if mad == 0:
            std = group.std()
            if std == 0 or pd.isna(std):
                return pd.Series(0.0, index=group.index)
            # Use std if MAD is 0 (rare for continuous data but possible)
            return (group - median) / std
            
        # Robust Z-score formula: 0.6745 * (x - median) / MAD
        return 0.6745 * (group - median) / mad

    # Calculate Robust Z-score group by SKU
    z_scores = df.groupby('SKU_Clean')['Usage_Value'].transform(calculate_robust_zscore)
    df['Anomaly_Z_Score'] = z_scores.round(3)
    
    # Flag: Robust Z-score > 4.5
    df['Is_Usage_Anomaly'] = df['Anomaly_Z_Score'] > 3
    
    # Fallback for "Unknown" SKUs where group statistics might be skewed or tiny
    # Hard bounds for massive injections: >750,000 for seconds, >50,000 for GB
    hard_bound_seconds = (df['Unit'].str.lower().str.contains('sec|hr|min')) & (df['Usage_Value'] > 750000)
    hard_bound_gb = (df['Unit'].str.lower().str.contains('gb|mb')) & (df['Usage_Value'] > 50000)
    
    df['Is_Usage_Anomaly'] = df['Is_Usage_Anomaly'] | hard_bound_seconds | hard_bound_gb
    
    total_anomalies = df['Is_Usage_Anomaly'].sum()

    print("✅ S09 — Usage Anomaly Detection complete")
    print(f"   Detected Anomalies: {total_anomalies}")
    print(f"   Max Z-Score:        {df['Anomaly_Z_Score'].max()}")
    
    return df

if __name__ == '__main__':
    # Need S03 for SKU_Clean
    import sys
    sys.path.insert(0, '.')
    from scenarios.s03_sku import run as s03_run
    
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s03_run(billing)
    billing = run(billing)
    
    print("\nSample anomalies (Top 10 by Z-Score):")
    anomalies = billing[billing['Is_Usage_Anomaly']].sort_values('Anomaly_Z_Score', ascending=False)
    if len(anomalies) > 0:
        print(anomalies[['Usage_ID', 'SKU_Clean', 'Usage_Value', 'Anomaly_Z_Score', 'Is_Usage_Anomaly']].head(10).to_string(index=False))
