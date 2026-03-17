"""
Transformation 04 — Idle & Rightsizing Recommendations
======================================================
Identifies resources that are consistently underutilized.
Rule: CPU_Clean < 10% AND Mem_Clean < 10%.

Output:
  - t04_idle_resources.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Resource_ID', 'Service_Clean', 'CPU_Clean', 'Mem_Clean', 'Cost_USD']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T04")
        return df
        
    # Only applies to Compute/Database where metrics exist
    valid = df.dropna(subset=['CPU_Clean', 'Mem_Clean']).copy()
    
    # Recommendation logic:
    # If CPU < 10 and Mem < 10 -> IDLE (Target for Termination)
    valid['Is_Idle'] = (valid['CPU_Clean'] < 10) & (valid['Mem_Clean'] < 10)
    
    # Aggregate by Resource_ID to find consistently idle ones
    res_agg = valid.groupby(['Resource_ID', 'Service_Clean'], as_index=False).agg(
        Avg_CPU=('CPU_Clean', 'mean'),
        Avg_Mem=('Mem_Clean', 'mean'),
        Total_Cost=('Cost_USD', 'sum'),
        Idle_Pings=('Is_Idle', 'sum'),
        Total_Pings=('Usage_ID', 'count')
    )
    
    # Filter to resources that are strictly idle
    res_agg['Idle_Ratio'] = res_agg['Idle_Pings'] / res_agg['Total_Pings']
    
    # Flag as recommended for termination if idle > 80% of the time it reported
    res_agg['Action_Recommended'] = res_agg['Idle_Ratio'].apply(
        lambda x: 'Terminate' if x > 0.8 else ('Downsize' if x > 0.5 else 'None')
    )
    
    idle_list = res_agg[res_agg['Action_Recommended'] != 'None'].sort_values('Total_Cost', ascending=False)
    
    idle_list.to_csv(os.path.join(out_dir, 't04_idle_resources.csv'), index=False)
    
    print("✅ T04 — Idle & Rightsizing Recommendations generated")
    print(f"   Underutilized Resources: {len(idle_list)}")
    print(f"   Potential Wasted Spend:  ${idle_list['Total_Cost'].sum():.2f}")
    
    return idle_list

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
