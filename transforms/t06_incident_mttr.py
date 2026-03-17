"""
Transformation 06 — Incident MTTA / MTTR Metrics
==================================================
Calculates downtime duration (Incident_End - Incident_Start) by joining incidents.csv
with the cleaned usage billing data.

Output:
  - t06_incident_mttr.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    if 'Incident_ID' not in df.columns:
        print("⚠️ Missing Incident_ID for T06")
        return pd.DataFrame()
        
    incidents_path = 'data/raw/incidents.csv'
    if not os.path.exists(incidents_path):
        print("⚠️ Cannot find incidents.csv for T06")
        return pd.DataFrame()
        
    incidents = pd.read_csv(incidents_path)
    
    # Needs valid start and end to compute duration
    incidents = incidents.dropna(subset=['Incident_Start', 'Incident_End']).copy()
    
    # Parse to UTC datetime
    incidents['Incident_Start'] = pd.to_datetime(incidents['Incident_Start'], utc=True, errors='coerce')
    incidents['Incident_End']   = pd.to_datetime(incidents['Incident_End'], utc=True, errors='coerce')
    
    # Drop rows that failed to parse
    incidents = incidents.dropna(subset=['Incident_Start', 'Incident_End'])
    
    # Calculate MTTR (Duration in minutes)
    incidents['Downtime_Minutes'] = (incidents['Incident_End'] - incidents['Incident_Start']).dt.total_seconds() / 60.0
    
    # Filter out negative durations (dirty data slip-throughs if any)
    valid_inc = incidents[incidents['Downtime_Minutes'] >= 0]
    
    # Group by Service for overall MTTR
    mttr_agg = valid_inc.groupby('Affected_Service', as_index=False).agg(
        Incident_Count=('Incident_ID', 'count'),
        MTTR_Minutes=('Downtime_Minutes', 'mean'),
        Max_Downtime=('Downtime_Minutes', 'max')
    ).round(1)
    
    mttr_agg.to_csv(os.path.join(out_dir, 't06_incident_mttr.csv'), index=False)
    
    print("✅ T06 — Incident MTTR Metrics generated")
    try:
        overall_mttr = valid_inc['Downtime_Minutes'].mean()
        print(f"   Overall MTTR: {overall_mttr:.1f} mins")
    except:
        pass
        
    return mttr_agg

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
